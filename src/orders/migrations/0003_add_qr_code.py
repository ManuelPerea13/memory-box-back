# Generated manually for add_qr_code field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_email_address_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='qrcodes/%Y/%m/%d/'),
        ),
    ]
