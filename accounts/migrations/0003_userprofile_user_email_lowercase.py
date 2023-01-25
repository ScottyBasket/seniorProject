# Generated by Django 4.1.5 on 2023-01-20 23:23

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_userprofile_gender'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='userprofile',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('email'), name='user_email_lowercase'),
        ),
    ]
