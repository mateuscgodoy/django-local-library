import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookForm


def index(request):
    """View function for home page of site."""

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()
    num_authors = (
        Author.objects.count()
    )  # The 'all()' is implied by default, so I could be left off.
    num_genres = Genre.objects.count()
    the_books = Book.objects.filter(title__icontains="the").count()
    num_of_visits = request.session.get("num_of_visits", 0)
    request.session["num_of_visits"] = num_of_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genres": num_genres,
        "the_books": the_books,
        "num_of_visits": num_of_visits,
    }

    return render(request, "catalog/index.html", context=context)


class BookListView(generic.ListView):
    model = Book
    template_name = "catalog/books.html"
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    template_name = "catalog/authors.html"


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on load to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class AllBorrowed(PermissionRequiredMixin, generic.ListView):
    """Generic list base view to handle librarians access to all borrowed books instances."""

    permission_required = "catalog.can_mark_returned"
    model = BookInstance
    template_name = "catalog/all_borrowed.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower__isnull=False, status__exact="o"
        ).order_by("due_back")


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    """On a GET call will render the Renew Form, and on a POST will process it's data."""

    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == "POST":
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()

            return HttpResponseRedirect(reverse("catalog:all-borrowed"))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})

    context = {"form": form, "book_instance": book_instance}
    return render(request, "catalog/book_renew_librarian.html", context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    # initial = {"date_of_death": "11/11/2023"}
    permission_required = "catalog.add_author"


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    #! NOT RECOMMEND, COULD RESULT IN UNINTENDED FIELDS BEING SHOW
    fields = "__all__"
    permission_required = "catalog.change_author"


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy("catalog:authors")
    permission_required = "catalog.delete_author"

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = "catalog.add_book"
    fields = ["title", "summary", "author", "isbn", "genre", "language"]


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = "catalog.change_book"
    fields = ["title", "summary", "author", "isbn", "genre", "language"]
