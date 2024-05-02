import uuid
from datetime import date

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint  # Constrains fields to unique values
from django.db.models.functions import Lower  # Returns lower cased value of field
from django.urls import reverse


class Genre(models.Model):
    """Model representing a book genre."""

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)",
    )

    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse("genre-detail", args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("name"),
                name="genre_name_case_insensitive_unique",
                violation_error_message="Genre already exists (case insensitive match)",
            )
        ]


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""

    title = models.CharField(max_length=200)
    author = models.ForeignKey("Author", on_delete=models.RESTRICT, null=True)
    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book"
    )
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        help_text='13 character <a href="https://www.isbn-international.org/content/what-isbn/10">ISBN</a> number.',
    )
    genre = models.ManyToManyField(
        Genre, help_text="Select one or more genres for this book"
    )
    language = models.ForeignKey(
        "Language",
        help_text="Select the language that the books was written in",
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        ordering = ["title", "author"]

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse("catalog:book-detail", args=[str(self.id)])

    #! NOT COMPUTATIONALLY OPTIMAL (just por demonstration purposes)
    def display_genre(self):
        """
        Create a string for the Genre. This is required to display genre in Admin.
        """
        return ", ".join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = "Genre"


class BookInstance(models.Model):
    """Model representing a specific copy of the book (i.e. that can
    be borrowed from the library)."""

    LOAD_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book across whole library",
    )
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=1,
        choices=LOAD_STATUS,
        blank=True,
        default="m",
        help_text="Book availability",
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def is_overdue(self):
        """Determines if the book is overdue based on due data and current data."""
        return bool(self.due_back and date.today() > self.due_back)

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.id} ({self.book.title})"


class Author(models.Model):
    """Model representing an author."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        """Return the URL to access a particular author instance."""
        return reverse("catalog:author-detail", args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.last_name}, {self.first_name}"


class Language(models.Model):
    """Model representing a language."""

    name = models.CharField(max_length=50, unique=True)

    def get_absolute_url(self):
        """Return the URL to access a particular language instance."""
        return reverse("language-detail", args=[str(self.id)])

    def __str__(self):
        """Defines how a language should be displayed."""
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("name"),
                name="language_names_case_insensitive_unique",
                violation_error_message="Language already exists (case insensitive comparison).",
            )
        ]
