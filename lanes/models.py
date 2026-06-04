from django.db import models
from address.models import Address

class Lanes(models.Model):
    lanes = models.CharField(
        max_length=55,
        blank=True,
        null=True,
        verbose_name="Bowling Lanes Name"
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Lanes Address"
    )

    def __str__(self):
        return str(self.lanes)  
    
    class Meta:
        verbose_name = "Lanes"
        verbose_name_plural = "Lanes"
        ordering = ["lanes"]
