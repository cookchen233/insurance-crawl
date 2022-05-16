# -*- coding: utf-8 -*-

import datetime, time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer,SmallInteger, String, Text, ForeignKey, DateTime, UniqueConstraint, Index, sql, text

Base = declarative_base()
class Shop(Base):

    __tablename__ = 'tb_shop_test_2'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # sys_ctime = Column(DateTime(timezone=True), server_default=sql.func.now())
    # sys_utime = Column(DateTime(timezone=True), onupdate=sql.func.now())
    sys_ctime = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    sys_utime = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    # ctime = Column(Integer, default=datetime.datetime.now)
    ctime = Column(Integer, default=text(str(time.time())))
    name = Column(String(50), index=True, nullable=False)
    qq = Column(String(50), server_default=text('""'))
    tel = Column(String(50), server_default=text('""'))
    img_tel = Column(Text, nullable=True)
    address = Column(String(500), server_default=text('""'))
    origin_address = Column(String(500), server_default=text('""'))
    province = Column(String(50), server_default=text('""'))
    city = Column(String(50), server_default=text('""'))
    district = Column(String(50), server_default=text('""'))
    shop_url = Column(String(500), server_default=text('""'))
    source_url = Column(String(500), server_default=text('""'))
    source = Column(String(50), server_default=text('""'))
    # extra = Column(Text, nullable=True)
    # extra2 = Column(SmallInteger, nullable=True, index=True, unique=True, server_default=text('""'))

    # __table_args__ = (
        # UniqueConstraint('id', 'name', name='uix_id_name'),   # 联合唯一索引
        # Index('ix_id_name', 'name', 'email'),                 # 联合索引
    # )

