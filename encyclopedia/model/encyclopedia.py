# -*- coding: utf-8 -*-

import datetime,time,sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer,SmallInteger, String, Text, ForeignKey, DateTime, UniqueConstraint, Index, sql, text
from ..common.func import *
from ..common import func

Base = declarative_base()
class Encyclopedia(Base):

    __tablename__ = 't_article'

    sys_id = Column(Integer, primary_key=True, autoincrement=True)
    # sys_ctime = Column(DateTime(timezone=True), server_default=sql.func.now())
    # sys_utime = Column(DateTime(timezone=True), onupdate=sql.func.now())
    sys_ctime = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    sys_utime = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    ctime = Column(Integer, default=time.time)
    uuid = Column(String(50), default=func.tuuid)
    title = Column(String(50), index=True, nullable=False)
    #category = Column(String(50), index=True, nullable=False)
    picture = Column(String(500), index=True, nullable=False)
    source_url = Column(String(500), index=True, nullable=False)
    source = Column(String(50), index=True, nullable=False)
    content = Column(Text, nullable=True)

    # __table_args__ = (
        # UniqueConstraint('id', 'name', name='uix_id_name'),   # 联合唯一索引
        # Index('ix_id_name', 'name', 'email'),                 # 联合索引
    # )

