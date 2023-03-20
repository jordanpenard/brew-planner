from django.shortcuts import render, redirect
from .models import Ingredient, Grain, Hop, Yeast, Stock
from django.contrib import messages


def index(request):
    return render(request, 'index.html')


def stock(request):
    # Filtering the list of ingredients so the list to add a new entry in the stock only shows ingredients that aren't yet in the stock
    used_ingredients = Stock.objects.filter(owner=request.user.username).values_list("ingredient")
    context = {'stock': Stock.objects.all(),
               'unused_ingredients': Ingredient.objects.all().exclude(pk__in=used_ingredients)}
    return render(request, 'stock.html', context)


def add_stock(request):
    if request.method != "POST":
        return redirect("stock")
    if not request.user.is_authenticated:
        return redirect("login")

    ingredient = request.POST['ingredient']
    quantity_g = request.POST['quantity_g']

    new_entry = Stock(ingredient=Ingredient.objects.get(pk=ingredient), quantity_g=quantity_g, owner=request.user.username)
    new_entry.save()
    return redirect("stock")


def edit_stock(request):
    if request.method != "POST":
        return redirect("stock")
    if not request.user.is_authenticated:
        return redirect("login")

    pk = request.POST['pk']
    quantity_g = request.POST['quantity_g']

    Stock.objects.filter(pk=pk, owner=request.user.username).update(quantity_g=quantity_g)
    return redirect("stock")


def ingredients(request):
    context = {'grain': Grain.objects.all(), 'hop': Hop.objects.all(), 'yeast': Yeast.objects.all()}
    return render(request, 'ingredients.html', context)


def add_ingredients(request):
    if request.method != "POST":
        return redirect("ingredients")
    if not request.user.is_authenticated:
        return redirect("login")

    name = request.POST['name']
    if request.POST['ingredient_type'] == "yeast":
        liquid_not_dry = request.POST['liquid_not_dry']

        new_entry = Yeast(name=name, liquid_not_dry=liquid_not_dry)
        new_entry.save()

    elif request.POST['ingredient_type'] == "hop":
        alpha_acid = request.POST['alpha_acid']
        whole_not_pellet = request.POST['whole_not_pellet']

        new_entry = Hop(name=name, alpha_acid=alpha_acid, whole_not_pellet=whole_not_pellet)
        new_entry.save()

    elif request.POST['ingredient_type'] == "grain":
        color_lovibond = request.POST['color_lovibond']
        ppg = request.POST['ppg']
        diastatic_power = request.POST['diastatic_power']

        new_entry = Grain(name=name, color_lovibond=color_lovibond, ppg=ppg, diastatic_power=diastatic_power)
        new_entry.save()

    else:
        messages.success(request, "Malformed request")

    return redirect("ingredients")
