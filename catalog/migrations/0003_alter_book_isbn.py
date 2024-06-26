# Generated by Django 5.0.4 on 2024-04-29 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_language_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(help_text='13 character <a href="https://www.isbn-international.org/content/what-isbn/10>ISBN</a> number."', max_length=13, unique=True, verbose_name='ISBN'),
        ),
    ]
