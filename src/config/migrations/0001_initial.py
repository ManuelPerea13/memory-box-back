# Generated for SiteSettings (precios y datos de pago)

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_mercadolibre', models.PositiveIntegerField(default=35000)),
                ('price_sin_luz', models.PositiveIntegerField(default=24000)),
                ('price_con_luz', models.PositiveIntegerField(default=42000)),
                ('price_pilas', models.PositiveIntegerField(default=2500)),
                ('deposit_amount', models.PositiveIntegerField(default=12000)),
                ('transfer_alias', models.CharField(default='manu.perea13', max_length=100)),
                ('transfer_bank', models.CharField(default='Mercado Pago', max_length=100)),
                ('transfer_holder', models.CharField(default='Manuel Perea', max_length=200)),
                ('contact_whatsapp', models.CharField(default='+54 9 351 392 3790', max_length=50)),
                ('contact_email', models.CharField(default='copiiworld@gmail.com', max_length=254)),
                ('link_mercadolibre', models.URLField(blank=True, max_length=500)),
            ],
            options={
                'verbose_name': 'Configuración del sitio',
                'verbose_name_plural': 'Configuración del sitio',
            },
        ),
    ]
