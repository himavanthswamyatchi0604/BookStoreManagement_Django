from django.urls import path
from . import views
from .views import add_to_cart

urlpatterns = [
    path('', views.index, name='index'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books-by-genre/<str:genre_name>/', views.books_by_genre, name='books_by_genre'),
    path('book/<int:book_id>/add_review/', views.add_review, name='add_review'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('books/', views.books_by_price, name='books_by_price'),
    path('autocomplete/', views.autocomplete_suggestions, name='autocomplete_suggestions'),
    path('add_to_cart/<int:book_id>/',  add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_item_quantity/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
]
