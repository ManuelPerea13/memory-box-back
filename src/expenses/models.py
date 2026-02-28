from decimal import Decimal
from django.db import models


class CostSettings(models.Model):
    """
    Reference cost configuration (JSON). Singleton (id=1).
    Used with Purchase (including PLA roll purchases) for expense and cost tracking.
    """
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Cost settings (reference)'
        verbose_name_plural = 'Cost settings (reference)'

    def __str__(self):
        return 'Reference costs'


class PurchaseCategory(models.TextChoices):
    BURBUJAS = 'burbujas', 'Bubble roll'
    CAJA_CARTON = 'caja_carton', 'Cardboard box (shipping)'
    BOLSA_ECOMMERCE = 'bolsa_ecommerce', 'Ecommerce bag'
    PUBLICIDAD_INSTAGRAM = 'publicidad_instagram', 'Instagram ads'
    IMAGENES = 'imagenes', 'Images'
    PLA_ROLL = 'pla_roll', 'PLA rollo'
    OTRO = 'otro', 'Other'


class Purchase(models.Model):
    """Expense record (variable quantities and costs by date). For PLA rolls: cost per gram = (total_cost/quantity)/grams_per_roll."""
    category = models.CharField(max_length=40, choices=PurchaseCategory.choices)
    date = models.DateField()
    quantity = models.PositiveIntegerField(default=1, help_text='Units purchased (e.g. 10 boxes, or number of PLA rolls)')
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    days = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='Period days (e.g. Instagram ads per week)'
    )
    notes = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # PLA roll only: variant (color), brand, grams per roll for cost_per_gram = (total_cost/quantity)/grams_per_roll
    variant = models.CharField(max_length=80, blank=True, help_text='PLA only: color/variant (e.g. Graphite, Wood)')
    brand = models.CharField(max_length=120, blank=True, help_text='PLA only: roll brand')
    grams_per_roll = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='PLA only: grams per roll (e.g. 1000). Cost per gram = (total_cost/quantity)/grams_per_roll'
    )

    class Meta:
        ordering = ['-date', '-id']
        verbose_name = 'Purchase / expense'
        verbose_name_plural = 'Purchases / expenses'

    def __str__(self):
        if self.category == PurchaseCategory.PLA_ROLL and self.variant:
            return f"{self.get_category_display()} {self.variant} - {self.date} - ${self.total_cost}"
        return f"{self.get_category_display()} - {self.date} - ${self.total_cost}"

    def pla_cost_per_gram(self):
        """For PLA_ROLL: cost per gram = (total_cost / quantity) / grams_per_roll. Returns None if not applicable."""
        if self.category != PurchaseCategory.PLA_ROLL or not self.quantity or not self.grams_per_roll:
            return None
        if self.total_cost is None:
            return None
        return (self.total_cost / self.quantity) / self.grams_per_roll

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.category in (PurchaseCategory.CAJA_CARTON, PurchaseCategory.BOLSA_ECOMMERCE):
            from orders.models import PackagingStock
            item_type = (
                PackagingStock.CAJA_CARTON if self.category == PurchaseCategory.CAJA_CARTON
                else PackagingStock.BOLSA_ECOMMERCE
            )
            stock, _ = PackagingStock.objects.get_or_create(item_type=item_type, defaults={'quantity': 0})
            stock.quantity += self.quantity
            stock.save(update_fields=['quantity'])
