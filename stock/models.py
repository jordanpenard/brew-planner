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

    def lovibondToRgb(self, lovibond):
        # From http://brew-engine.com/engines/beer_color_calculator.html

        srm = (1.3546*lovibond)-0.76

        r = 0
        g = 0
        b = 0

        if 0 <= srm <= 1:
            r = 240
            g = 239
            b = 181
        
        elif 1 < srm <= 2:
            r = 233
            g = 215
            b = 108

        elif srm > 2:
            # Set red decimal
            if srm < 70.6843:
                r = 243.8327-6.4040 * srm+0.0453 * srm * srm
            else:
                r = 17.5014
            
            # Set green decimal
            if srm < 35.0674:
                g = 230.929-12.484 * srm+0.178 * srm * srm
            else:
                g = 12.0382
            
            # Set blue decimal
            if srm < 4:
                b = -54 * srm+216
            elif 4 <= srm < 7:
                b = 0
            elif 7 <= srm < 9:
                b = 13 * srm-91
            elif 9 <= srm < 13:
                b = 2 * srm+8
            elif 13 <= srm < 17:
                b = -1.5 * srm+53.5
            elif 17 <= srm < 22:
                b = 0.6 * srm+17.8
            elif 22 <= srm < 27:
                b = -2.2 * srm+79.4
            elif 27 <= srm < 34:
                b = -0.4285 * srm + 31.5714
            else:
                b = 17

        return "rgb(" + str(r) + ", " + str(g) + ", " + str(b) + ")"

    def stats(self):

        # PPG = grain gravity points per pound per gallon
        # PTS = PPG * grain weight in pound * efficiency
        # OG = PTS / batch size in gallon

        efficiency = 0.7
        batch_size_g = self.batch_size_l * 0.219969
        pts = 0

        total_weight = 0
        total_color = 0
        total_dp = 0
        for grain_recipe in GrainRecipe.objects.filter(recipe=self.pk):
            ppg = grain_recipe.grain.ppg
            grain_weight_lbs = grain_recipe.quantity_g * 0.00220462
            pts += ppg * grain_weight_lbs * efficiency

            total_dp += grain_recipe.grain.diastatic_power * grain_recipe.quantity_g
            total_color += grain_recipe.grain.color_lovibond * grain_recipe.quantity_g
            total_weight += grain_recipe.quantity_g

        if batch_size_g == 0:
            og = 1
        else:
            og = 1 + (pts / batch_size_g) / 1000

        if total_weight == 0:
            diastatic_power = 0
            color_l = 0
        else:
            diastatic_power = total_dp / total_weight
            color_l = total_color / total_weight

        # Tinseth’s IBU Formula (https://homebrewacademy.com/ibu-calculator/)
        #
        # AAU = Weight of hops (g) * % Alpha Acid rating of the hops * 1000
        # Bigness factor = 1.65 * 0.000125^(wort gravity – 1)
        # Boil Time factor = (1 – e^(-0.04 * time in mins) )/4.15
        # U = Bigness Factor * Boil Time Factor
        # IBU = AAU x U / Vol (l)

        ibu = 0

        for hop_recipe in HopRecipe.objects.filter(recipe=self.pk):
            if not hop_recipe.dry_hop:
                aau = hop_recipe.quantity_g * hop_recipe.hop.alpha_acid * 10
                bf = 1.65 * 0.000125 ** (og - 1)
                btf = (1 - 2.71828 ** (-0.04 * hop_recipe.time_min)) / 4.15
                hop_ibu = aau * bf * btf / self.batch_size_l

                # Pellet provides a 10% IBU increase
                if not hop_recipe.hop.whole_not_pellet:
                    hop_ibu += 0.1 * hop_ibu

                ibu += hop_ibu

        # For the FG, taking 2 reference points as follow and doing a linear extrapolation
        # Ref : https://brulosophy.com/2015/10/12/the-mash-high-vs-low-temperature-exbeeriment-results/

        if self.mash_temperature_c < 64:
            fg = 1.005

        elif self.mash_temperature_c > 72:
            fg = 1.014

        else:
            fg = 1.005 + (self.mash_temperature_c-64)*(1.014-1.005)/(72 - 64)

        abv = (og - fg) * 131.25

        ret = {'og': '{:.3f}'.format(og),
               'fg': '{:.3f}'.format(fg),
               'abv': '{:.1f}'.format(abv),
               'diastatic_power': '{:.0f}'.format(diastatic_power),
               'color_l': '{:.1f}'.format(color_l),
               'color_rgb': self.lovibondToRgb(color_l),
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
    name = models.CharField(max_length=200)
    recipe = models.ForeignKey(Recipe, on_delete=models.DO_NOTHING)

    brew_date = models.DateTimeField()
    bottling_date = models.DateTimeField()

    measured_og = models.FloatField(default=1)
    measured_fg = models.FloatField(default=1)
    measured_mash_ph = models.FloatField(default=0)

    def __str__(self):
        return self.name