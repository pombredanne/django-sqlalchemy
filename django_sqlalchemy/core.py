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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
        
        connection_string = self.database[alias]['connect_string']
        options = self.database[alias].get('options', {})
        self._engines[alias] = create_engine(connection_string, **options)

    def __getitem__(self, alias):
        if alias in self._engines:
            return self._engines[alias]
        
        self._mk_engine()
        return self._engines[alias]


class SessionManager(object):
    def __init__(self):
        self._sessions = {}

    def _mk_session(self, alias):
        engine = engines[alias]
        self._sessions[alias] = sessionmaker(bind=engine)

    def __getitem__(self, alias):
        if alias in self._sessions:
            return self._sessions[alias]()

        self._mk_session(alias)
        return self._sessions[alias]()


engines = EngineManager()
engine = engines['default']
sessions = SessionManager()

def create_session(alias):
    return sessions[alias]
