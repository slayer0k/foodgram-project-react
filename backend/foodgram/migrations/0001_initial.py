# Generated by Django 2.2.16 on 2022-11-25 16:25

import django.core.validators
from django.db import migrations, models

import foodgram.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Название ингридиента')),
                ('measuring_unit', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'Ингридиент',
                'verbose_name_plural': 'Ингридиенты',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(validators=[foodgram.validators.bigger_than_zero], verbose_name='количество')),
            ],
            options={
                'verbose_name': 'Ингридиент для рецепта',
                'verbose_name_plural': 'Ингридиенты для рецепта',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Recipes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=150, verbose_name='Название рецепта')),
                ('image', models.ImageField(upload_to='recipes/', verbose_name='Изображение рецепта')),
                ('description', models.TextField(verbose_name='описание рецепта')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[foodgram.validators.bigger_than_zero], verbose_name='Время приготовления')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='ShopLists',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Покупка',
                'verbose_name_plural': 'Список покупок',
            },
        ),
        migrations.CreateModel(
            name='Subscriptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('color', models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator(regex='^#[A-Z0-9]{6}')])),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
            },
        ),
    ]
