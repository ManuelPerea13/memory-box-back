# Generated initial migration - Pedido, RecorteImagen

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, db_index=True, max_length=40, null=True)),
                ('nombre_cliente', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('telefono', models.CharField(blank=True, max_length=50)),
                ('direccion', models.TextField(blank=True)),
                ('notas', models.TextField(blank=True)),
                ('estado', models.CharField(choices=[('borrador', 'Borrador'), ('enviado', 'Enviado'), ('procesando', 'Procesando'), ('entregado', 'Entregado')], default='borrador', max_length=20)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-creado'],
            },
        ),
        migrations.CreateModel(
            name='RecorteImagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.PositiveSmallIntegerField(help_text='Índice del slot (0-9)')),
                ('orden', models.PositiveSmallIntegerField(default=0, help_text='Orden de visualización')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='recortes/%Y/%m/%d/')),
                ('crop_data', models.JSONField(blank=True, null=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recortes', to='pedidos.pedido')),
            ],
            options={
                'ordering': ['pedido', 'orden', 'slot'],
                'unique_together': {('pedido', 'slot')},
            },
        ),
    ]
