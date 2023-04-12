from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('recipe', views.recipe, name="recipe"),
    path('recipe/add', views.add_recipe, name="add_recipe"),
    path('recipe/<int:pk>', views.edit_recipe, name="edit_recipe"),
    path('recipe/<int:pk>/add_grain', views.add_grain, name="add_grain"),
    path('recipe/<int:pk>/add_hop', views.add_hop, name="add_hop"),
    path('recipe/<int:recipe_pk>/new_brew', views.new_brew, name="new_brew"),
    path('recipe/edit_grain/<int:pk>', views.edit_grain, name="edit_grain"),
    path('recipe/edit_hop/<int:pk>', views.edit_hop, name="edit_hop"),
    path('stock', views.stock, name="stock"),
    path('stock/add', views.add_stock, name="add_stock"),
    path('stock/edit', views.edit_stock, name="edit_stock"),
    path('ingredients', views.ingredients, name="ingredients"),
    path('ingredients/add', views.add_ingredients, name="add_ingredients"),
    path('brew', views.brew, name="brew"),
    path('brew/<int:pk>', views.edit_brew, name="edit_brew"),
    path('brew/<int:pk>/next_state', views.next_state_brew, name="next_state_brew"),
    path('brew/<int:pk>/previous_state', views.previous_state_brew, name="previous_state_brew"),
    path('brew/<int:pk>/save_prep', views.save_prep, name="save_prep"),
    path('brew/<int:pk>/save_mash', views.save_mash, name="save_mash"),
    path('brew/<int:pk>/save_boil', views.save_boil, name="save_boil"),
    path('brew/<int:pk>/save_fermenting', views.save_fermenting, name="save_fermenting"),
    path('brew/<int:pk>/save_completed', views.save_completed, name="save_completed"),
    path('brew/<int:pk>/consume_ingredients', views.consume_ingredients, name="consume_ingredients"),
]
