from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram.models import (Favorites, Ingredients, RecipeIngredients,
                             Recipes, RecipeTags, ShopLists, Subscriptions,
                             Tags)
from foodgram.validators import bigger_than_zero

User = get_user_model()


def is_subscribed(user, obj):
    return (
        user.is_authenticated
        and user.subscribed.filter(author=obj).exists()
    )


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        return {
            'email': instance.email, 'id': instance.id,
            'username': instance.username, 'first_name': instance.first_name,
            'last_name': instance.last_name,
        }


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        return is_subscribed(self.context['request'].user, obj)


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'


class RecipeIngridientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = RecipeIngredients
        fields = '__all__'

    def validate_amount(self, value):
        bigger_than_zero(value)
        return value

    def to_representation(self, instance):
        return {
            'id': instance.ingredient.id,
            'name': instance.ingredient.name,
            'measurement_unit': instance.ingredient.measuring_unit,
            'amount': instance.amount
        }


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return is_subscribed(self.context['request'].user, obj)

    def get_recipes(self, obj):
        limit = self.context['request'].GET.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return RecipesForSubscribers(queryset, many=True).data


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscriptions
        fields = ('author', 'subscriber')
        read_only_fields = ('subscriber', 'author')

    def create(self, validated_data):
        if validated_data['author'] == validated_data['subscriber']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        subscription, status = Subscriptions.objects.get_or_create(
            **validated_data)
        if not status:
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора!'
            )
        return subscription

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author, context={'request': self.context['request']}
        ).data


class RecipesForSubscribers(serializers.ModelSerializer):

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipesSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngridientSerializer(
        many=True, required=True, source='recipe_ingredient'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text',
            'cooking_time'
        )

    def validate_cooking_time(self, value):
        bigger_than_zero(value)
        return value

    def validate_ingredients(self, value):
        values = set()
        for ingredient in value:
            values.add(ingredient['id'])
        if len(values) < len(value):
            raise serializers.ValidationError(
                'Вы добавляете одинаковые ингидиенты несколько раз'
            )
        return value

    def validate_tags(self, value):
        if len(set(value)) < len(value):
            raise serializers.ValidationError(
                'Нельзя добавлять одинаковые тэги к одному рецепту'
            )
        return value

    def user(self):
        return self.context['request'].user

    def get_is_favorited(self, obj):
        return (
            self.user().is_authenticated
            and self.user().favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.user().is_authenticated
            and self.user().shoplist.filter(recipe=obj).exists()
        )

    def create_ingredients_tags(self, tags, ingredients, recipe):
        objs = [
            RecipeTags(recipe=recipe, tag=tag) for tag in tags
        ]
        RecipeTags.objects.bulk_create(objs)
        objs = [
            RecipeIngredients(
                recipe=recipe, amount=ingredient['amount'],
                ingredient=ingredient['id']
            ) for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(objs)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient')
        recipe = Recipes.objects.create(**validated_data)
        self.create_ingredients_tags(tags, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.image.delete()
        instance.recipe_ingredient.all().delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient')
        self.create_ingredients_tags(tags, ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = TagsSerializer(instance.tags, many=True).data
        return data


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class FavoritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = '__all__'
        read_only_fields = ('recipe', 'user')

    def create(self, validated_data):
        print(validated_data)
        favorite, status = Favorites.objects.get_or_create(**validated_data)
        if not status:
            raise serializers.ValidationError(
                'Вы уже добавляли этот рецепт в избранное!'
            )
        return favorite

    def to_representation(self, instance):
        return RecipesForSubscribers(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopLists
        fields = '__all__'
        read_only_fields = ('recipe', 'user')

    def create(self, validated_data):
        object, status = ShopLists.objects.get_or_create(**validated_data)
        if not status:
            raise serializers.ValidationError(
                'Этот рецепт уже есть в корзине'
            )
        return object

    def to_representation(self, instance):
        return RecipesForSubscribers(instance.recipe).data
