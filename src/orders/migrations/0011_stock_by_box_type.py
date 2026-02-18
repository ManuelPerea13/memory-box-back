# Stock: add box_type and unique_together (variant, box_type)

from django.db import migrations, models

STOCK_VARIANTS = ['graphite', 'wood', 'black', 'marble']
BOX_TYPE_WITH_LIGHT = 'with_light'


def create_with_light_stock(apps, schema_editor):
    Stock = apps.get_model('orders', 'Stock')
    for v in STOCK_VARIANTS:
        Stock.objects.get_or_create(
            variant=v,
            box_type=BOX_TYPE_WITH_LIGHT,
            defaults={'quantity': 0}
        )


def reverse_create_with_light(apps, schema_editor):
    Stock = apps.get_model('orders', 'Stock')
    Stock.objects.filter(box_type=BOX_TYPE_WITH_LIGHT).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_rename_hidden_from_dashboard_to_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='box_type',
            field=models.CharField(
                choices=[('no_light', 'No light'), ('with_light', 'With light')],
                default='no_light',
                help_text='no_light | with_light',
                max_length=20,
            ),
        ),
        # Remove unique on variant so we can have (graphite, no_light) and (graphite, with_light)
        migrations.AlterField(
            model_name='stock',
            name='variant',
            field=models.CharField(
                choices=[('graphite', 'graphite'), ('wood', 'wood'), ('black', 'black'), ('marble', 'marble')],
                max_length=50,
                unique=False,
            ),
        ),
        migrations.RunPython(create_with_light_stock, reverse_create_with_light),
        migrations.AddConstraint(
            model_name='stock',
            constraint=models.UniqueConstraint(
                fields=['variant', 'box_type'],
                name='orders_stock_variant_box_type_uniq',
            ),
        ),
    ]
