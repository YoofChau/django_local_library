from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name = "index"),
    path("book/", views.BookListView.as_view(), name = "BookListView"),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path("author/", views.AuthorListView.as_view(), name = "AuthorListView"),
    path("author/<int:pk>", views.AuthorBookView.as_view(), name = "AuthorBook"),
    path("mybook/", views.LoanedBooksByUserListView.as_view(), name="my-borrowed"),
    path("borrowedbook/", views.LoanedBookList.as_view(), name="BorrowedBookList"),
    path("book/<uuid:pk>/renew/", views.renew_book_librarian, name="renew-book-librarian"),
    path("author/create/", views.AuthorCreate.as_view(), name="author_create"),
    path("author/<int:pk>/update/", views.AuthorUpdate.as_view(), name="author_update"),
    path("author/<int:pk>/delete/", views.AuthorDelete.as_view(), name="author_delete"),
    path("book/create/", views.BookCreate.as_view(), name="book_create"),
    path("book/<int:pk>/update/", views.BookUpdate.as_view(), name="book_update"),
    path("book/<int:pk>/delete/", views.BookDelete.as_view(), name="book_delete"),
    path("book/searchresult/", views.LibrarySearchListView.as_view(), name="Library_SearchView"),
]

