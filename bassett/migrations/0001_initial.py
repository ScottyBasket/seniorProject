# Generated by Django 4.1.5 on 2023-01-13 14:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('gender', models.CharField(choices=[('female', 'Female'), ('male', 'Male'), ('coed', 'Co-Ed')], max_length=22)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('last_signup_date', models.DateField()),
                ('min_men', models.PositiveIntegerField(blank=True, help_text='minimum men players required for co-ed', null=True)),
                ('min_women', models.PositiveIntegerField(blank=True, help_text='minimum women players required for co-ed', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Sport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('rules', models.TextField()),
                ('min_players', models.PositiveIntegerField()),
                ('max_players', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=False)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bassett.league')),
                ('player', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SportLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bassett.location')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bassett.sport')),
            ],
        ),
        migrations.AddField(
            model_name='league',
            name='sport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bassett.sport'),
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField()),
                ('date', models.DateField()),
                ('score1', models.PositiveIntegerField()),
                ('score2', models.PositiveIntegerField()),
                ('color1', models.CharField(choices=[('black', 'Black'), ('white', 'White')], default=('black', 'Black'), max_length=7)),
                ('color2', models.CharField(choices=[('black', 'Black'), ('white', 'White')], default=('white', 'White'), max_length=7)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bassett.league')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bassett.location')),
                ('team1', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='team1', to='bassett.team')),
                ('team2', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='team2', to='bassett.team')),
            ],
        ),
    ]
