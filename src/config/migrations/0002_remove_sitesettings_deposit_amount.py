# Generated - remove deposit_amount (seña is now calculated from prices)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sitesettings',
            name='deposit_amount',
        ),
    ]
