from django.contrib import admin

from foodgram.models import (Ingredients, Recipes, RecipeTags, ShopLists,
                             Subscriptions, Tags)

admin.site.register(ShopLists)
admin.site.register(Subscriptions)
admin.site.register(RecipeTags)


@admin.register(Ingredients)
class AdminIngredients(admin.ModelAdmin):
    list_display = ('name', 'measuring_unit',)
    list_filter = ('name',)
    search_fields = ('^name',)


@admin.register(Recipes)
class AdminRecipes(admin.ModelAdmin):
    list_display = ('author', 'name',)
    list_filter = ('tags__name',)
    search_fields = ('^author', '^name')


@admin.register(Tags)
class AdminTags(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
