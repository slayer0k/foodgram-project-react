from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

from foodgram.validators import bigger_than_zero

User = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(
        max_length=150, verbose_name='Название ингридиента',
        unique=True
    )
    measuring_unit = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self) -> str:
        return self.name


class Tags(models.Model):
    name = models.CharField(unique=True, max_length=150)
    slug = models.SlugField(unique=True)
    color = models.CharField(
        unique=True, max_length=7,
        validators=[RegexValidator(regex=r'^#[A-Z0-9]{6}')]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='автор рецепта',
        related_name='recipes',
    )
    name = models.CharField(
        max_length=150, verbose_name='Название рецепта',
        db_index=True
    )
    image = models.ImageField(
        'Изображение рецепта', upload_to='recipes/'
    )
    description = models.TextField('описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredients, through='RecipeIngridients',
        verbose_name='ингридиенты', db_index=True
    )
    tags = models.ManyToManyField(Tags, verbose_name='тэги', db_index=True)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', validators=[bigger_than_zero, ]
    )

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='ingredients')
    amount = models.PositiveSmallIntegerField(
        'количество', validators=[bigger_than_zero, ]
    )
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE, related_name='recipes')

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Ингридиент для рецепта'
        verbose_name_plural = 'Ингридиенты для рецепта'

    def __str__(self) -> str:
        return f'{self.recipe} - {self.ingridient}'


class Favorites(models.Model):
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name='favorited'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_favorite'
            ),
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('pk',)

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class Subscriptions(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribed'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'], name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name='dont_follow_yourself'
            ),
        ]
        ordering = ('pk',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.author} - {self.subscriber}'


class ShopLists(models.Model):
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, related_name='is_shopping_cart'
    )
    user = models.ForeignKey(
        User, related_name='shoplist', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = 'Список покупок'
        verbose_name = 'Покупка'

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'
