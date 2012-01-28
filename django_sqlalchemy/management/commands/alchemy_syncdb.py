# -*- coding: utf-8 -*-

from optparse import make_option
import sys
import traceback

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.management.color import no_style
from django.utils.datastructures import SortedDict
from django.utils.importlib import import_module

from django_sqlalchemy.core import engines


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to synchronize. '
                'Defaults to the "default" database.'),
    )
    help = "Create the database tables for all apps in INSTALLED_APPS whose tables haven't already been created."

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity'))
        interactive = options.get('interactive')
        show_traceback = options.get('traceback')
        self.style = no_style()

        db = options.get('database')
        engine = engines[db]

        for app_path in settings.INSTALLED_APPS:
            try:
                app_mod = import_module(app_path + '.models'
            except ImportError:
                continue

            base_klass = getattr(app_mod, 'Base', None)
            if not base_klass:
                continue

            if verbosity >= 1:
                print "SQLALchemy: Installing tables from %s..." % (app_path)

            base_klass.metadata.create_all(engine)


        ## Install custom SQL for the app (but only if this
        ## is a model we've just created)
        #if verbosity >= 1:
        #    print "Installing custom SQL ..."
        #for app_name, model_list in manifest.items():
        #    for model in model_list:
        #        if model in created_models:
        #            custom_sql = custom_sql_for_model(model, self.style, connection)
        #            if custom_sql:
        #                if verbosity >= 2:
        #                    print "Installing custom SQL for %s.%s model" % (app_name, model._meta.object_name)
        #                try:
        #                    for sql in custom_sql:
        #                        cursor.execute(sql)
        #                except Exception, e:
        #                    sys.stderr.write("Failed to install custom SQL for %s.%s model: %s\n" % \
        #                                        (app_name, model._meta.object_name, e))
        #                    if show_traceback:
        #                        traceback.print_exc()
        #                    transaction.rollback_unless_managed(using=db)
        #                else:
        #                    transaction.commit_unless_managed(using=db)
        #            else:
        #                if verbosity >= 3:
        #                    print "No custom SQL for %s.%s model" % (app_name, model._meta.object_name)

        #if verbosity >= 1:
        #    print "Installing indexes ..."
        ## Install SQL indices for all newly created models
        #for app_name, model_list in manifest.items():
        #    for model in model_list:
        #        if model in created_models:
        #            index_sql = connection.creation.sql_indexes_for_model(model, self.style)
        #            if index_sql:
        #                if verbosity >= 2:
        #                    print "Installing index for %s.%s model" % (app_name, model._meta.object_name)
        #                try:
        #                    for sql in index_sql:
        #                        cursor.execute(sql)
        #                except Exception, e:
        #                    sys.stderr.write("Failed to install index for %s.%s model: %s\n" % \
        #                                        (app_name, model._meta.object_name, e))
        #                    transaction.rollback_unless_managed(using=db)
        #                else:
        #                    transaction.commit_unless_managed(using=db)

        ## Load initial_data fixtures (unless that has been disabled)
        #if load_initial_data:
        #    from django.core.management import call_command
        #    call_command('loaddata', 'initial_data', verbosity=verbosity, database=db)
