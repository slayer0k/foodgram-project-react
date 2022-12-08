from django.contrib import admin

from foodgram.models import (Ingredients, RecipeIngredients, Recipes,
                             RecipeTags, ShopLists, Subscriptions, Tags)

admin.site.register(ShopLists)
admin.site.register(Subscriptions)


class RecipeIngredientsInline(admin.StackedInline):
    model = RecipeIngredients
    raw_id_fields = ['ingredient']
    extra = 0
    min_num = 1


class RecipeTagsInline(admin.StackedInline):
    model = RecipeTags
    raw_id_fields = ['tag']
    extra = 0
    min_num = 1


@admin.register(Ingredients)
class AdminIngredients(admin.ModelAdmin):
    list_display = ('name', 'measuring_unit',)
    list_filter = ('name',)
    search_fields = ('^name',)


@admin.register(Recipes)
class AdminRecipes(admin.ModelAdmin):
    inlines = [RecipeIngredientsInline, RecipeTagsInline]
    list_display = ('author', 'name')
    list_filter = ('tags__name',)
    search_fields = ('^author', '^name')
    raw_id_fields = ('author',)
    exclude = ('ingredients',)


@admin.register(Tags)
class AdminTags(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
