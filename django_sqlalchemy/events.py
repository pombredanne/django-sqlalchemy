# -*- coding: utf-8 -*-

from django.conf import settings

def on_pool_connection_checkout(dbapi_connection, connection_record, connection_proxy): 
    #TODO: fix this
    #TODO: set only timezone on postgresql backends.
    cursor = connection_proxy.cursor()
    cursor.execute('SET TIME ZONE %s;', [settings.TIME_ZONE])
