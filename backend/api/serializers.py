from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram.models import (Favorites, Ingredients, RecipeIngridients,
                             Recipes, ShopLists, Subscriptions, Tags)
from foodgram.validators import bigger_than_zero

User = get_user_model()


def is_subscribed(user, obj):
    return (
        user.is_authenticated
        and obj in User.objects.filter(subscribers__subscriber=user)
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


class ChangePassword(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate(self, attrs):
        user = self.context.get('user')
        if not user.check_password(attrs.get('current_password')):
            raise serializers.ValidationError(
                'пароль не соответствует'
            )
        return attrs


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'


class RecipeIngridientSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
    )
    amount = serializers.IntegerField(validators=[bigger_than_zero, ])

    class Meta:
        model = RecipeIngridients
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        print(data)
        return data


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
        print(limit)
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return RecipesForSubscribers(queryset, many=True).data


class FollowSerializer(serializers.ModelSerializer):
    subscriber = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Subscriptions
        fields = ('author', 'subscriber')

    def create(self, validated_data):
        if validated_data['author'] == validated_data['subscriber']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        if Subscriptions.objects.filter(**validated_data).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного автора'
            )
        return Subscriptions.objects.create(**validated_data)

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author, context={'request': self.context['request']}
        ).data


class RecipesForSubscribers(serializers.ModelSerializer):

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True
    )
    ingridients = RecipeIngridientSerializer()
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = '__all__'


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngridientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'description',
            'cooking_time'
        )

    def user(self):
        return self.context['request'].user

    def get_is_favorited(self, obj):
        return self.user().is_authenticated and Favorites.objects.filter(
            recipe=obj, user=self.user()
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return self.user().is_authenticated and ShopLists.objects.filter(
            recipe=obj, user=self.user()).exists()
