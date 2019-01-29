from django.contrib import admin
from catalog.models import Book, Author, Genre, BookInstance

# Register your models here.
#admin.site.register(Book)
#admin.site.register(Author)
admin.site.register(Genre)
#admin.site.register(BookInstance)

class BookInline(admin.TabularInline):
    model = Book

#Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "date_of_birth", "date_of_death")
    inlines = [BookInline]
    
    fields = ["first_name", "last_name", ("date_of_birth", "date_of_death")]

#Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    
# Register the Admin classes for book useing the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "display_genre")
    inlines = [BookInstanceInline]

# Register the Admin classess for BookInstance useing the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ("book", "status", "borrower", "due_back", "id")
    list_filter = ("status", "due_back")

    fieldsets = (
        (None, {
            "fields": ("book", "imprint", "id")
        }),
        ("Availability", {
            "fields": ("status", "due_back", "borrower")
        }),
    )
