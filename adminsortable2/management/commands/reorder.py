# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string


class Command(BaseCommand):
    args = '<model model ...>'
    help = 'Restore the primary ordering fields of a model containing a special ordering field'

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='+', type=str)

    def handle(self, *args, **options):
        for modelname in options['models']:
            try:
                Model = import_string(modelname)
            except ImportError:
                raise CommandError('Unable to load model "%s"' % modelname)
            if not hasattr(Model._meta, 'ordering') or len(Model._meta.ordering) == 0:
                raise CommandError('Model "{0}" does not define field "ordering" in its Meta class'.format(modelname))
            orderfield = Model._meta.ordering[0]
            if orderfield[0] == '-':
                orderfield = orderfield[1:]
            for order, obj in enumerate(Model.objects.iterator(), start=1):
                setattr(obj, orderfield, order)
                obj.save()
            self.stdout.write('Successfully reordered model "{0}"'.format(modelname))
