from django.shortcuts import render, redirect
from .models import Ingredient, Grain, Hop, Yeast, Stock, Recipe, GrainRecipe, HopRecipe
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


def recipe(request):
    context = {'recipes': Recipe.objects.all(),
               'grain_recipes': GrainRecipe.objects.all(),
               'hop_recipes': HopRecipe.objects.all(),
               'yeasts': Yeast.objects.all()}
    return render(request, 'recipe.html', context)


def add_recipe(request):
    if request.method != "POST":
        return redirect("recipe")
    if not request.user.is_authenticated:
        return redirect("login")

    new_entry = Recipe(owner=request.user.username)
    new_entry.save()
    new_entry.name = "Recipe "+str(new_entry.pk)
    new_entry.save()

    return redirect("edit_recipe", pk=new_entry.pk)


def edit_recipe(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    current_recipe = Recipe.objects.get(pk=pk)

    if request.method == "POST":
        if current_recipe.owner != request.user.username:
            messages.success(request, "You can't edit someone else's recipe")
            return redirect("edit_recipe", pk)

        current_recipe.name = request.POST['name']
        current_recipe.batch_size_l = request.POST['batch_size_l']
        current_recipe.yeast = Yeast.objects.get(pk=request.POST['yeast'])
        current_recipe.comments = request.POST['comments']
        current_recipe.save()
        return redirect("edit_recipe", pk)

    else:
        if current_recipe.owner != request.user.username:
            messages.success(request, "Read only as someone else owns this recipe")
            disabled_state = "disabled"
        else:
            disabled_state = ""

        used_grains = GrainRecipe.objects.filter(recipe=current_recipe).values_list("grain")

        context = {'recipe': current_recipe,
                   'disabled_state': disabled_state,
                   'grain_recipes': GrainRecipe.objects.filter(recipe=pk),
                   'hop_recipes': HopRecipe.objects.filter(recipe=pk),
                   'all_grain': Grain.objects.all(),
                   'all_hop': Hop.objects.all(),
                   'unused_grain': Grain.objects.all().exclude(pk__in=used_grains),
                   'all_yeast': Yeast.objects.all()}
        return render(request, 'edit_recipe.html', context)


def add_grain(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    current_recipe = Recipe.objects.get(pk=pk)
    if current_recipe.owner != request.user.username:
        messages.success(request, "You can't edit someone else's recipe")
        return redirect("edit_recipe", pk)

    if request.method != "POST":
        return redirect("recipe")

    grain = request.POST['grain']
    quantity_g = request.POST['quantity_g']

    new_entry = GrainRecipe(recipe=current_recipe, grain=Grain.objects.get(pk=grain), quantity_g=quantity_g)
    new_entry.save()

    return redirect("edit_recipe", pk)


def add_hop(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    current_recipe = Recipe.objects.get(pk=pk)
    if current_recipe.owner != request.user.username:
        messages.success(request, "You can't edit someone else's recipe")
        return redirect("edit_recipe", pk)

    if request.method != "POST":
        return redirect("recipe")

    hop = request.POST['hop']
    quantity_g = request.POST['quantity_g']
    time_min = request.POST['time_min']

    if request.POST.get('dry_hop', False):
        dry_hop = True
        time_min = 0
    else:
        dry_hop = False

    new_entry = HopRecipe(recipe=current_recipe, hop=Hop.objects.get(pk=hop), quantity_g=quantity_g, time_min=time_min, dry_hop=dry_hop)
    new_entry.save()

    return redirect("edit_recipe", pk)


def edit_grain(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    current_recipe = GrainRecipe.objects.get(pk=pk)
    if current_recipe.recipe.owner != request.user.username:
        messages.success(request, "You can't edit someone else's recipe")
        return redirect("edit_recipe", pk)

    if request.method != "POST":
        return redirect("recipe")

    current_recipe.grain = Grain.objects.get(pk=request.POST['grain'])
    current_recipe.quantity_g = request.POST['quantity_g']
    current_recipe.save()
    return redirect("edit_recipe", pk=current_recipe.recipe.pk)


def edit_hop(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    current_recipe = HopRecipe.objects.get(pk=pk)
    if current_recipe.recipe.owner != request.user.username:
        messages.success(request, "You can't edit someone else's recipe")
        return redirect("edit_recipe", pk)

    if request.method != "POST":
        return redirect("recipe")

    current_recipe.hop = Hop.objects.get(pk=request.POST['hop'])
    current_recipe.quantity_g = request.POST['quantity_g']
    current_recipe.time_min = request.POST['time_min']

    if request.POST.get('dry_hop', False):
        current_recipe.dry_hop = True
        current_recipe.time_min = 0
    else:
        current_recipe.dry_hop = False

    current_recipe.save()

    return redirect("edit_recipe", pk=current_recipe.recipe.pk)
