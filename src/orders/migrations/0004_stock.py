# Generated manually for Stock model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_add_qr_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variant', models.CharField(choices=[('graphite', 'graphite'), ('wood', 'wood'), ('black', 'black'), ('marble', 'marble')], max_length=50, unique=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Stock',
            },
        ),
    ]
