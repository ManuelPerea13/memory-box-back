# Migración: reemplazar estado 'sent' por 'in_progress' (En curso)

from django.db import migrations, models


def sent_to_in_progress(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.filter(status='sent').update(status='in_progress')


def in_progress_to_sent(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.filter(status='in_progress').update(status='sent')


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_stock'),
    ]

    operations = [
        migrations.RunPython(sent_to_in_progress, in_progress_to_sent),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('in_progress', 'En curso'),
                    ('processing', 'Processing'),
                    ('delivered', 'Delivered'),
                ],
                default='draft',
                max_length=20,
            ),
        ),
    ]
