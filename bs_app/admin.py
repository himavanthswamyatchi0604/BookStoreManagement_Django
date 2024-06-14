from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Book, Genre, Author, Review, Order

admin.site.register(Book)
admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Review)
admin.site.register(Order)
