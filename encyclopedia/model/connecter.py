# -*- coding: utf-8 -*-

import sqlalchemy
from sqlalchemy.orm import sessionmaker

class Connecter(object):

    connections = {}

    @staticmethod
    def connect(connect_link):
        engine = sqlalchemy.create_engine(
            connect_link,
            max_overflow=0,  # 超过连接池大小外最多创建的连接
            pool_size=5,  # 连接池大小
            pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
            pool_recycle=-1,  # 多久之后对线程池中的线程进行一次连接的回收（重置）
            echo=False
        )
        Session = sessionmaker(bind=engine)
        session = Session()
        # session._model_changes = {}
        return [session, engine]

    @staticmethod
    def get_instance(connect_link):
        if not connect_link in Connecter.connections:
            Connecter.connections[connect_link] = Connecter.connect(connect_link)
        return Connecter.connections[connect_link]


