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
    login_form = AuthenticationForm()
    signup_form = SignUpForm()
    return render(request, 'index.html', {
        'books': books,
        'genres': genres,
        'selected_genre': genre_name,
        'query': query,
        'max_price': max_price,
        'login_form': login_form,
        'signup_form': signup_form
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
                return redirect(next_url)
    return redirect('index')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('/?signup=success')
    return redirect('index')


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

    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()
    total_price = sum(item.total_price for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'hide_sidebar': True})


def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    # Optionally add a success message if needed
    return redirect('view_cart')


@login_required
def update_cart_item_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')

        cart_item = get_object_or_404(CartItem, id=item_id)

        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1

        cart_item.save()

        # Calculate updated total price for the item
        cart_item.refresh_from_db()
        total_price = cart_item.total_price

        # Calculate total price of the cart
        cart = cart_item.cart
        cart_items = cart.items.all()
        cart_total = sum(item.total_price for item in cart_items)

        # Return updated data
        data = {
            'quantity': cart_item.quantity,
            'total_price': total_price,
            'cart_total': cart_total
        }
        return JsonResponse(data)

    return redirect('view_cart')
