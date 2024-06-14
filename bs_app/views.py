from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from .forms import SignUpForm, ReviewForm
from .models import Book, Genre, Review, Author, Cart, CartItem
from django.http import JsonResponse
from django.contrib import messages


def index(request, genre_name=None):
    query = request.GET.get('q')
    max_price = request.GET.get('max_price', None)
    books = Book.objects.annotate(avg_rating=Avg('reviews__rating'))
    if genre_name:
        books = books.filter(genres__name__iexact=genre_name)
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__name__icontains=query) | Q(genres__name__icontains=query))
    if max_price:
        books = books.filter(price__lte=max_price)
    genres = Genre.objects.all()
    return render(request, 'index.html', {
        'books': books,
        'genres': genres,
        'selected_genre': genre_name,
        'query': query,
        'max_price': max_price
    })


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    avg_rating = Review.objects.filter(book=book).aggregate(avg_rating=Avg('rating'))['avg_rating']
    review_count = Review.objects.filter(book=book).count()
    reviews = Review.objects.filter(book=book)
    genres = Genre.objects.all()
    return render(request, 'book_detail.html', {
        'book': book,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'reviews': reviews,
        'user': request.user,
        'genres': genres
    })


def login_view(request):
    next_url = request.GET.get('next', 'index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect(request.POST.get('next', 'index'))
    else:
        form = AuthenticationForm()
    genres = Genre.objects.all()
    return render(request, 'login.html', {
        'form': form,
        'next': next_url,
        'genres': genres
    })


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('/?signup=success')
    else:
        form = SignUpForm()
    genres = Genre.objects.all()
    return render(request, 'signup.html', {
        'form': form,
        'genres': genres
    })


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('index')


@login_required
def add_review(request, book_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        book = Book.objects.get(pk=book_id)
        Review.objects.create(book=book, user=request.user, rating=rating, comment=comment)
    return redirect('book_detail', book_id=book_id)


def books_by_genre(request, genre_name):
    max_price = request.GET.get('max_price', None)
    books = Book.objects.filter(genres__name__iexact=genre_name).annotate(avg_rating=Avg('reviews__rating'))
    if max_price:
        books = books.filter(price__lte=max_price)
    genres = Genre.objects.all()
    return render(request, 'index.html', {
        'books': books,
        'genres': genres,
        'selected_genre': genre_name,
        'max_price': max_price
    })


def books_by_price(request):
    max_price = request.GET.get('max_price')
    if max_price is not None:
        # Fetch books based on the max_price parameter
        books = Book.objects.filter(price__lte=max_price)
        # Serialize books data as JSON
        books_data = [{'title': book.title, 'author': book.author.name, 'price': book.price} for book in books]
        return JsonResponse({'books': books_data})
    else:
        # Handle the case when max_price parameter is not provided
        return JsonResponse({'error': 'Max price parameter is missing'}, status=400)


def autocomplete_suggestions(request):
    if 'term' in request.GET:
        query = request.GET.get('term')
        books = Book.objects.filter(title__icontains=query).values_list('title', flat=True)
        authors = Author.objects.filter(name__icontains=query).values_list('name', flat=True)
        genres = Genre.objects.filter(name__icontains=query).values_list('name', flat=True)

        suggestions = list(set(list(books) + list(authors) + list(genres)))
        return JsonResponse(suggestions, safe=False)

    return JsonResponse([], safe=False)


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    messages.success(request, f'Added {book.title} to cart.')
    return redirect('view_cart')


def view_cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user) if request.user.is_authenticated else []
    cart_item_count = len(cart_items)
    return render(request, 'view_cart.html', {'cart_items': cart_items, 'cart_item_count': cart_item_count})
