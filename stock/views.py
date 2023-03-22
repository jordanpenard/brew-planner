from django.shortcuts import render, redirect
from .models import Ingredient, Grain, Hop, Yeast, Stock, Recipe, GrainRecipe, HopRecipe, Brew
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
        current_recipe.mash_temperature_c = request.POST['mash_temperature_c']
        current_recipe.fermentation_temperature_c = request.POST['fermentation_temperature_c']
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


def brew(request):

    context = {'brews': Brew.objects.all()}

    return render(request, 'brew.html', context)


def new_brew(request, recipe_pk):

    new_entry = Brew(recipe=Recipe.objects.get(pk=recipe_pk), owner=request.user.username)
    new_entry.save()
    new_entry.name = "#" + str(new_entry.pk)
    new_entry.save()

    return redirect("brew")


def edit_brew(request, pk):
    current_brew = Brew.objects.get(pk=pk)

    grain_mass_g = 0
    for grain in GrainRecipe.objects.filter(recipe=current_brew.recipe):
        grain_mass_g += grain.quantity_g

    mash_volume_l = current_brew.mash_thickness_lpkg * grain_mass_g/1000
    evaporation_l = current_brew.evaporation_lph * current_brew.recipe.boil_time_min/60
    target_pre_boil_volume_l = current_brew.recipe.batch_size_l + evaporation_l
    sparge_volume_l = target_pre_boil_volume_l - mash_volume_l

    target_pre_boil_gravity = 1 + (float(current_brew.recipe.stats()['og'])-1) * (current_brew.recipe.batch_size_l/target_pre_boil_volume_l)

    # Mash strike temperature is the temperature at which the water needs to be so once we added the grain we hit
    #  our target mash temperature (Assuming the grains are at 18 degree C)
    # Formula from https://homebrewanswers.com/document/calculating-strike-water-temperature-for-mashing
    mash_strike_temperature_c = (0.41/current_brew.mash_thickness_lpkg) * (current_brew.recipe.mash_temperature_c - 18) + current_brew.recipe.mash_temperature_c

    total_mash_mass_kg = (grain_mass_g/1000)+mash_volume_l
    sparge_strike_temperature_c = (current_brew.mash_out_temp_c * (total_mash_mass_kg+sparge_volume_l) - total_mash_mass_kg * current_brew.recipe.mash_temperature_c)/sparge_volume_l

    if current_brew.pre_boil_volume_l > 0:
        estimated_volume_l = current_brew.pre_boil_volume_l - evaporation_l
        estimated_og = 1 + current_brew.pre_boil_volume_l * (current_brew.pre_boil_gravity - 1) / estimated_volume_l
    else:
        estimated_og = float(current_brew.recipe.stats()['og'])
        estimated_volume_l = current_brew.recipe.batch_size_l

    context = {'brew': current_brew,
               'grain_recipes': GrainRecipe.objects.filter(recipe=current_brew.recipe.pk),
               'hop_recipes': HopRecipe.objects.filter(recipe=current_brew.recipe.pk),
               'mash_volume_l': mash_volume_l,
               'target_pre_boil_volume_l': target_pre_boil_volume_l,
               'target_pre_boil_gravity': '{:.3f}'.format(target_pre_boil_gravity),
               'mash_strike_temperature_c': '{:.1f}'.format(mash_strike_temperature_c),
               'sparge_strike_temperature_c': '{:.1f}'.format(sparge_strike_temperature_c),
               'estimated_volume_l': '{:.1f}'.format(estimated_volume_l),
               'estimated_og': '{:.3f}'.format(estimated_og),
               'sparge_volume_l': sparge_volume_l}

    return render(request, 'edit_brew.html', context)


def next_state_brew(request, pk):

    current_brew = Brew.objects.get(pk=pk)

    if not request.user.is_authenticated:
        return redirect("login")

    if current_brew.owner != request.user.username:
        messages.success(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    if current_brew.state == Brew.BrewState.PREP:
        current_brew.state = Brew.BrewState.MASH
    elif current_brew.state == Brew.BrewState.MASH:
        current_brew.state = Brew.BrewState.BOIL
    elif current_brew.state == Brew.BrewState.BOIL:
        current_brew.state = Brew.BrewState.FERMENTING
    elif current_brew.state == Brew.BrewState.FERMENTING:
        current_brew.state = Brew.BrewState.COMPLETED
    current_brew.save()

    return redirect("edit_brew", pk=pk)


def previous_state_brew(request, pk):

    current_brew = Brew.objects.get(pk=pk)

    if not request.user.is_authenticated:
        return redirect("login")

    if current_brew.owner != request.user.username:
        messages.success(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    if current_brew.state == Brew.BrewState.MASH:
        current_brew.state = Brew.BrewState.PREP
    elif current_brew.state == Brew.BrewState.BOIL:
        current_brew.state = Brew.BrewState.MASH
    elif current_brew.state == Brew.BrewState.FERMENTING:
        current_brew.state = Brew.BrewState.BOIL
    elif current_brew.state == Brew.BrewState.COMPLETED:
        current_brew.state = Brew.BrewState.FERMENTING
    current_brew.save()

    return redirect("edit_brew", pk=pk)


def save_prep(request, pk):

    current_brew = Brew.objects.get(pk=pk)

    if not request.user.is_authenticated:
        return redirect("login")

    if current_brew.owner != request.user.username:
        messages.success(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    current_brew.brew_date = request.POST['brew_date']
    current_brew.mash_thickness_lpkg = request.POST['mash_thickness_lpkg']
    current_brew.evaporation_lph = request.POST['evaporation_lph']
    current_brew.mash_out_temp_c = request.POST['mash_out_temp_c']
    current_brew.save()

    return redirect("edit_brew", pk=pk)


def save_mash(request, pk):

    current_brew = Brew.objects.get(pk=pk)

    if not request.user.is_authenticated:
        return redirect("login")

    if current_brew.owner != request.user.username:
        messages.success(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    current_brew.measured_mash_temp_c = request.POST['measured_mash_temp_c']
    current_brew.measured_mash_ph = request.POST['measured_mash_ph']
    current_brew.save()

    return redirect("edit_brew", pk=pk)


def save_boil(request, pk):

    current_brew = Brew.objects.get(pk=pk)

    if not request.user.is_authenticated:
        return redirect("login")

    if current_brew.owner != request.user.username:
        messages.success(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    current_brew.pre_boil_volume_l = request.POST['pre_boil_volume_l']
    current_brew.pre_boil_gravity = request.POST['pre_boil_gravity']
    current_brew.measured_og = request.POST['measured_og']
    current_brew.fermenter_volume_l = request.POST['fermenter_volume_l']
    current_brew.save()

    return redirect("edit_brew", pk=pk)


def save_completed(request, pk):

    current_brew = Brew.objects.get(pk=pk)

    if not request.user.is_authenticated:
        return redirect("login")

    if current_brew.owner != request.user.username:
        messages.success(request, "You can't edit someone else's brew")
        return redirect("edit_brew", pk=pk)

    current_brew.bottling_date = request.POST['bottling_date']
    current_brew.measured_fg = request.POST['measured_fg']
    current_brew.bottling_volume_l = request.POST['bottling_volume_l']
    current_brew.save()

    return redirect("edit_brew", pk=pk)
