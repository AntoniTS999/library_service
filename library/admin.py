from email.headerregistry import Group

from django.contrib import admin

from library.models import Book

admin.site.register(Book)

admin.site.unregister(Group)
