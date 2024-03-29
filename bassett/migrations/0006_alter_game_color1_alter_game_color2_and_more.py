# Generated by Django 4.1.5 on 2023-01-23 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bassett', '0005_alter_game_color1_alter_game_color2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='color1',
            field=models.CharField(choices=[('black', 'Black'), ('white', 'White')], default='b', max_length=7),
        ),
        migrations.AlterField(
            model_name='game',
            name='color2',
            field=models.CharField(choices=[('black', 'Black'), ('white', 'White')], default='b', max_length=7),
        ),
        migrations.AlterField(
            model_name='league',
            name='gender',
            field=models.CharField(choices=[('female', 'Female'), ('male', 'Male'), ('coed', 'Co-Ed')], max_length=7),
        ),
    ]
