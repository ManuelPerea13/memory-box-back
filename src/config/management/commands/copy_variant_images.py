"""
Comando obsoleto: BoxVariantImage ya no tiene external_url; solo se usa File.
Cargá las imágenes manualmente desde Django Admin (Site configuration > Imágenes de variantes)
o desde el front (Admin > Variantes > + Agregar imagen).
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Obsoleto: las imágenes de variantes se cargan solo por archivo (File) en el admin.'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                'external_url fue eliminado del modelo. Cargá las imágenes manualmente desde '
                'Django Admin (Imágenes de variantes) o desde el front (Admin > Variantes).'
            )
        )
