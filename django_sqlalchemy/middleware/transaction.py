# -*- coding: utf-8 -*-

from .core import create_session, remove_session
import threading

from django.conf import settings

SQLALCHEMY_SESSION_AUTOCOMMIT = getattr(settings, 'SQLALCHEMY_SESSION_AUTOCOMMIT', False)


class EnsureSession(object):
    def process_request(self, request):
        global local
        local.session = request.s = create_session(
            autocommit=SQLALCHEMY_SESSION_AUTOCOMMIT
        )

    def process_exception(self, request, exception):
        request.s.rollback()
        request.s.close()
        remove_session()

    def process_response(self, request, response):
        try:
            request.s.commit()
        except:
            request.s.rollback()

        request.s.close()
        remove_session()
        return response
