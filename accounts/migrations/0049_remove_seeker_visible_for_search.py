# Generated by Django 4.2.1 on 2023-12-15 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0048_seeker_visible_for_search'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seeker',
            name='visible_for_search',
        ),
    ]
