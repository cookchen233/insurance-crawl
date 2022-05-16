# -*- coding: utf-8 -*-

from connecter import *
class Db(object):

    # Child class to be set
    connect_link = ''

    session = object
    engine = object

    def __init__(self, model):
        connection = Connecter.get_instance(self.connect_link)
        self.session = connection[0]
        self.engine = connection[1]

    def __enter__(self):
        return self

    def  __exit__(self, exc_type, exc_val, exc_tb):
        # pass
        self.session.commit()
        self.session.close()

