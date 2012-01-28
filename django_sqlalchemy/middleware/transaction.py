# -*- coding: utf-8 -*-

from .core import create_session
import threading

local = threading.local()
local.transaction = None

from django.conf import settings

SQLALCHEMY_SESSION_AUTOCOMMIT = getattr(settings, 'SQLALCHEMY_SESSION_AUTOCOMMIT', False)


class EnsureSession(object):
    def process_request(self, request):
        global local
        local.session = request.s = create_session(
            autocommit=SQLALCHEMY_SESSION_AUTOCOMMIT
        )

    def process_exception(self, request, exception):
        if request.s.transaction.is_active:
            request.s.transaction.rollback()
        request.s.__class__.remove()

    def process_response(self, request, response):
        if request.s.transaction.is_active:
            request.s.transaction.commit()
        
        global local
        request.s.transaction.close()
        request.s.__class__.remove()
        return response
