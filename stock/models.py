from django.db import models
from polymorphic.models import PolymorphicModel
from .beer_tools import og_from_grain_bill, color_l_from_grain_bill, dp_from_grain_bill, lovibond_to_rgb, \
    ibu_from_hop_bill, compute_abv


class Ingredient(PolymorphicModel):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Grain(Ingredient):
    color_lovibond = models.FloatField(default=0)
    ppg = models.FloatField(default=0)
    diastatic_power = models.FloatField(default=0)

    def __str__(self):
        return self.name+" - "+str(self.color_lovibond)+"°L - "+str(self.ppg)+"PPG - "+str(self.diastatic_power)+"DP"


class Hop(Ingredient):
    alpha_acid = models.FloatField(default=0)
    whole_not_pellet = models.BooleanField(default=False)

    def __str__(self):
        return self.name+" - "+str(self.alpha_acid)+"% - "+("Whole" if self.whole_not_pellet else "Pellet")


class Yeast(Ingredient):
    liquid_not_dry = models.BooleanField(default=False)

    def __str__(self):
        return self.name+" - "+("Liquid" if self.liquid_not_dry else "Dry")


class Stock(models.Model):
    owner = models.CharField(max_length=200)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.DO_NOTHING)
    quantity_g = models.IntegerField(default=0)

    def __str__(self):
        return str(self.ingredient)+" - "+str(self.quantity_g)+"g"


class Recipe(models.Model):
    owner = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    batch_size_l = models.FloatField(default=0)
    comments = models.CharField(max_length=1000, blank=True)
    yeast = models.ForeignKey(Ingredient, on_delete=models.DO_NOTHING, null=True)
    mash_temperature_c = models.FloatField(default=0)

    def stats(self):

        grain_bill = GrainRecipe.objects.filter(recipe=self.pk)
        og = og_from_grain_bill(grain_bill, self.batch_size_l)
        diastatic_power = dp_from_grain_bill(grain_bill)
        color_l = color_l_from_grain_bill(grain_bill)
        ibu = ibu_from_hop_bill(HopRecipe.objects.filter(recipe=self.pk), self.batch_size_l, og)

        # For the FG, taking 2 reference points as follow and doing a linear extrapolation
        # Ref : https://brulosophy.com/2015/10/12/the-mash-high-vs-low-temperature-exbeeriment-results/
        if self.mash_temperature_c < 64:
            fg = 1.005
        elif self.mash_temperature_c > 72:
            fg = 1.014
        else:
            fg = 1.005 + (self.mash_temperature_c-64)*(1.014-1.005)/(72 - 64)

        abv = compute_abv(og, fg)

        nb_brew = len(Brew.objects.filter(recipe=self.pk))

        ret = {'og': '{:.3f}'.format(og),
               'fg': '{:.3f}'.format(fg),
               'abv': '{:.1f}'.format(abv),
               'nb_brew': nb_brew,
               'diastatic_power': '{:.0f}'.format(diastatic_power),
               'color_l': '{:.1f}'.format(color_l),
               'color_rgb': lovibond_to_rgb(color_l),
               'ibu': '{:.1f}'.format(ibu)}
        return ret


class GrainRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    grain = models.ForeignKey(Grain, on_delete=models.DO_NOTHING)
    quantity_g = models.IntegerField(default=0)


class HopRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    hop = models.ForeignKey(Hop, on_delete=models.DO_NOTHING)
    quantity_g = models.IntegerField(default=0)
    time_min = models.IntegerField(default=0)
    dry_hop = models.BooleanField(default=False)


class Brew(models.Model):

    class BrewState(models.TextChoices):
        PREP = "Prep"
        BREWING = "Brewing"
        FERMENTING = "Fermenting"
        COMPLETED = "Completed"

    name = models.CharField(max_length=200)
    owner = models.CharField(max_length=200)
    recipe = models.ForeignKey(Recipe, on_delete=models.DO_NOTHING)
    state = models.CharField(max_length=20, choices=BrewState.choices, default=BrewState.PREP)

    brew_date = models.DateTimeField(null=True)
    bottling_date = models.DateTimeField(null=True)

    measured_og = models.FloatField(default=1)
    measured_fg = models.FloatField(default=1)
    measured_mash_ph = models.FloatField(default=0)

    def __str__(self):
        return self.name + " - " + self.recipe.name + " - " + self.state

    def stats(self):

        og = self.measured_og
        fg = self.measured_fg
        abv = compute_abv(og, fg)

        grain_bill = GrainRecipe.objects.filter(recipe=self.recipe.pk)
        diastatic_power = dp_from_grain_bill(grain_bill)
        color_l = color_l_from_grain_bill(grain_bill)
        ibu = ibu_from_hop_bill(HopRecipe.objects.filter(recipe=self.recipe.pk), self.recipe.batch_size_l, og)

        ret = {'og': '{:.3f}'.format(og),
               'fg': '{:.3f}'.format(fg),
               'abv': '{:.1f}'.format(abv),
               'diastatic_power': '{:.0f}'.format(diastatic_power),
               'color_l': '{:.1f}'.format(color_l),
               'color_rgb': lovibond_to_rgb(color_l),
               'ibu': '{:.1f}'.format(ibu)}
        return ret
