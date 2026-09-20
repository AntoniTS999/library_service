from django.contrib import admin

from books.models import Book
from borrowings.models import Borrowing


class BookInline(admin.TabularInline):
    model = Book
    extra = 1


class BorrowingAdmin(admin.ModelAdmin):
    inlines = [BookInline]


admin.site.register(Borrowing, BorrowingAdmin)
