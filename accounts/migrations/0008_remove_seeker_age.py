# Generated by Django 4.2.1 on 2023-05-09 18:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_seeker_age'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seeker',
            name='age',
        ),
    ]
