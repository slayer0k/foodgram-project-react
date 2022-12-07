from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram.models import (Ingredients, RecipeIngredients, Recipes,
                             RecipeTags, Tags)
from foodgram.validators import bigger_than_zero

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.subscribed.filter(author=obj).exists()
        )


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'


class RecipeIngridientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )
    name = serializers.CharField(source='ingredient.name', required=False)
    measuring_unit = serializers.CharField(
        source='ingredient.measuring_unit', required=False
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = RecipeIngredients
        fields = '__all__'
        read_only_fields = ('name', 'measuring_unit')

    def validate_amount(self, value):
        bigger_than_zero(value)
        return value


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        limit = self.context['request'].GET.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return RecipesForSubscribers(queryset, many=True).data


class RecipesForSubscribers(serializers.ModelSerializer):

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipesSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True, required=True
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngridientSerializer(
        many=True, required=True, source='recipeingredients_set'
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

    def create_ingredients(self, ingredients, recipe):
        objs = [
            RecipeIngredients(
                recipe=recipe, amount=ingredient['amount'],
                ingredient=ingredient['id']
            ) for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(objs)

    def create_tags(self, tags, recipe):
        objs = [
            RecipeTags(recipe=recipe, tag=tag) for tag in tags
        ]
        RecipeTags.objects.bulk_create(objs)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients_set')
        recipe = Recipes.objects.create(**validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        if validated_data.get('tags'):
            tags = validated_data.pop('tags')
            instance.recipe_tags.all().delete()
            self.create_tags(tags, instance)
        if validated_data.get('image'):
            instance.image.delete()
        if validated_data.get('recipeingredients_set'):
            ingredients = validated_data.pop('recipeingredients_set')
            instance.recipeingredients_set.all().delete()
            self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = TagsSerializer(instance.tags, many=True).data
        return data


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'
