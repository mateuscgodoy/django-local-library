from django.shortcuts import render

from .models import Book, Author, BookInstance, Genre


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

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genres": num_genres,
        "the_books": the_books,
    }

    return render(request, "catalog/index.html", context=context)
