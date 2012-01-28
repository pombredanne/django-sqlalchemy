# -*- coding: utf-8 -*-



"""
Posible database dict configuration:

SQLALCHEMY_DATABASES = {
    'default': {
        'connect_string': 'postgresql://user@host/dbname',
        'options': { 
            'server_side_cursors': True,
        }
    },
}

"""

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

from .events import on_pool_connection_checkout

class EngineManager(object):
    def __init__(self, databases):
        self.databases = databases
        self._engines = {}

    def _mk_engine(self, alias):
        """
        Creates on demand local engine for alias.
        """

        if alias not in self.databases:
            raise ImproperlyConfigured("Alias '%s' is not found in database configuration." % (alias))
        
        connection_string = self.databases[alias]['connect_string']
        options = self.databases[alias].get('options', {})
        self._engines[alias] = create_engine(connection_string, **options)
        event.listen(self._engines[alias], 'checkout', on_pool_connection_checkout)

    def __getitem__(self, alias):
        if alias in self._engines:
            return self._engines[alias]
        
        self._mk_engine(alias)
        return self._engines[alias]


from sqlalchemy.orm import scoped_session

class SessionManager(object):
    def __init__(self):
        self._sessions = {}

    def _mk_session(self, alias):
        engine = engines[alias]
        self._sessions[alias] = scoped_session(sessionmaker(bind=engine))

    def __getitem__(self, key):
        if key in self._sessions:
            return self._sessions[key]

        self._mk_session(key)
        return self._sessions[key]

    def __delitem__(self, key):
        if key in self:
            self[key].remove()

    def __contains__(self, key):
        return key in self._sessions

engines = EngineManager(settings.SQLALCHEMY_DATABASES)
engine = engines['default']
sessions = SessionManager()

def create_session(alias='default', *args, **kwargs):
    session_class = sessions[alias]
    return session_class(*args, **kwargs)

def remove_session(alias='default'):
    del sessions[alias]
