import datetime

from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.views.generic import ListView

from catalog.models import Author

# Create your views here.
@login_required
def index(request):
    """View function for home page of site."""

    #Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genre = Genre.objects.all().count()

    # Available books (status = "a")
    num_instances_available = BookInstance.objects.filter(status__exact = "a").count()

    # The "all()" is implied by default.
    num_authors = Author.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genre": num_genre,
        "num_visits": num_visits,
    }
    
    #Render the HTML template index.html with the data in the context variable
    return render(request, "index.html", context = context)
    
class BookListView(generic.ListView):
    template_name = "catalog/book_list.html"
    context_object_name = "book_list"
    paginate_by = 10

    def get_queryset(self):
        return Book.objects.all()

class BookDetailView(generic.DetailView):
    model = Book
    template_name = "catalog/book_detail.html"

class AuthorListView(generic.ListView):
    template_name = "catalog/author_list.html"
    context_object_name = "author_list"
    paginate_by = 10

    def get_queryset(self):
        return Author.objects.all()

class AuthorBookView(generic.DetailView):
    model = Author
    template_name = "catalog/author_book.html"

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact="o").order_by("due_back")

class LoanedBookList(PermissionRequiredMixin,generic.ListView):
    permission_required = "catalog.can_mark_returned"
    model = BookInstance
    template_name = "catalog/loaned_book.html"
    context_object_name = "loanedbook_list"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.all()

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('BorrowedBookList') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(CreateView):
    model = Author
    fields = "__all__"
    
class AuthorUpdate(UpdateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy("AuthorListView")

class BookCreate(CreateView):
    model = Book
    fields = "__all__"
    
class BookUpdate(UpdateView):
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre"]

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy("BookListView")

# Search Engine
class LibrarySearchListView(ListView):
    """
    Display a Blog List page filtered by the search query.
    """
    model = Book
    paginate_by = 5

    def get_queryset(self):
        qs = Book.objects.all()
        
        keywords = self.request.GET.get('q')
        if keywords:
            query = SearchQuery(keywords)
            title_vector = SearchVector('title')
            vectors = title_vector
            qs = qs.annotate(search=vectors).filter(search=query)
            qs = qs.annotate(rank=SearchRank(vectors, query)).order_by('-rank')

        return qs
