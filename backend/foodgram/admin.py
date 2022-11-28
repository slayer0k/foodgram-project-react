from django.contrib import admin

from foodgram.models import (Ingredients, RecipeIngredients, Recipes,
                             ShopLists, Subscriptions, Tags)

admin.site.register(Tags)
admin.site.register(ShopLists)
admin.site.register(Subscriptions)
admin.site.register(RecipeIngredients)
admin.site.register(Recipes)


@admin.register(Ingredients)
class AdminIngredients(admin.ModelAdmin):
    list_display = ('name', 'measuring_unit',)
    list_filter = ('name',)
