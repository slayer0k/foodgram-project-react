from django.contrib import admin
from django.utils.html import format_html

from foodgram.models import (Ingredients, Recipes, ShopLists, Subscriptions,
                             Tags, RecipeIngredients, RecipeTags)

admin.site.register(ShopLists)
admin.site.register(Subscriptions)


class RecipeIngredientsInline(admin.StackedInline):
    model = RecipeIngredients
    raw_id_fields = ['ingredient']
    extra = 0


class RecipeTagsInline(admin.StackedInline):
    model = RecipeTags
    raw_id_fields = ['tag']
    extra = 0


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

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{} {}</span>',
            self.color
        )
