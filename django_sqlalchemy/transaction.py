# -*- coding: utf-8 -*-

class _CommitOnSuccess(object):
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        self.transaction = self.session.begin_nested()

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_value is not None:
                self.transaction.rollback()
            else:
                self.transaction.commit()
        except:
            self.transaction.rollback()
            raise


commit_on_success = _CommitOnSuccess
