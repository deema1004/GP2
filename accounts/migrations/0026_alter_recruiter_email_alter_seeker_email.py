# Generated by Django 4.2.1 on 2023-05-15 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_alter_recruiter_email_alter_seeker_cv_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruiter',
            name='email',
            field=models.EmailField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='seeker',
            name='email',
            field=models.EmailField(blank=True, max_length=500, null=True),
        ),
    ]
