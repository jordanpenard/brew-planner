from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('recipe', views.recipe, name="recipe"),
    path('recipe/add', views.add_recipe, name="add_recipe"),
    path('recipe/<int:pk>', views.edit_recipe, name="edit_recipe"),
    path('recipe/<int:pk>/add_grain', views.add_grain, name="add_grain"),
    path('recipe/<int:pk>/add_hop', views.add_hop, name="add_hop"),
    path('recipe/edit_grain/<int:pk>', views.edit_grain, name="edit_grain"),
    path('recipe/edit_hop/<int:pk>', views.edit_hop, name="edit_hop"),
    path('stock', views.stock, name="stock"),
    path('stock/add', views.add_stock, name="add_stock"),
    path('stock/edit', views.edit_stock, name="edit_stock"),
    path('ingredients', views.ingredients, name="ingredients"),
    path('ingredients/add', views.add_ingredients, name="add_ingredients"),
    path('brew', views.brew, name="brew"),
]
