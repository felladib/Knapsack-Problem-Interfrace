from django.db import models

# Create your models here.
# your database
class sacados(models.Model):
    ids_ac = models.IntegerField(primary_key=True)
    capacity_sac = models.IntegerField()

    def __str__(self):
        return str(self.ids_ac)  


class objet(models.Model):
    id_obj = models.IntegerField(primary_key=True)
    poid_obj = models.IntegerField()
    value_obj = models.IntegerField()

    def __str__(self):
        return str(self.id_obj)  