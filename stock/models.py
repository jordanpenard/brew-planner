from django.db import models
from polymorphic.models import PolymorphicModel


class Ingredient(PolymorphicModel):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Grain(Ingredient):
    color_lovibond = models.FloatField(default=0)
    ppg = models.FloatField(default=0)
    diastatic_power = models.FloatField(default=0)

    def __str__(self):
        return self.name+" - "+str(self.color_lovibond)+"L - "+str(self.ppg)+"PPG - "+str(self.diastatic_power)+"DP"


class Hop(Ingredient):
    alpha_acid = models.FloatField(default=0)
    whole_not_pellet = models.BooleanField(default=False)

    def __str__(self):
        return self.name+" - "+str(self.alpha_acid)+"AA - "+("Whole" if self.whole_not_pellet else "Pellet")


class Yeast(Ingredient):
    liquid_not_dry = models.BooleanField(default=False)

    def __str__(self):
        return self.name+" - "+("Liquid" if self.liquid_not_dry else "Dry")


class Stock(models.Model):
    owner = models.CharField(max_length=200)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_g = models.IntegerField(default=0)

    def __str__(self):
        return str(self.ingredient)+" - "+str(self.quantity_g)+"g"
