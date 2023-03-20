from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('stock', views.stock, name="stock"),
    path('stock/add', views.add_stock, name="add_stock"),
    path('ingredients', views.ingredients, name="ingredients"),
    path('ingredients/add', views.add_ingredients, name="add_ingredients"),
]
