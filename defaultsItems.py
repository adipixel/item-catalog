#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, User, Item

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


user1 = User(name='Aditya', email='adi@gmail.com', picture='')

category1 = Category(name='Voice Assistants', user_id=user1.id)

session.add(category1)
session.commit()

item1 = Item(name='Google Home',
             description='Google Assistant with voice powered smart home device',  # NOQA
             image='https://lh3.googleusercontent.com/igThvoKwToXtZOfTANWbgp2ZoLnPBV2KDt9oJuaK419yIHQIo24eIcsCbgWcnfwlFjs=w1000',  # NOQA
             category=category1,
             user_id=user1.id)

session.add(item1)
session.commit()

item2 = Item(name='Google Home Mini',
             description='Google Assistant with voice powered smart home device',  # NOQA
             image='https://lh3.googleusercontent.com/proxy/18eqsg2QP7rKGTRh1hgZZcxAuSt0vDfU0wNh8OW7ivJKce5apCKyh0OlEoYhoYXxudmjjbXVr3IlgILYos_xMEb2DClCi7wwprP3ftNsfTm8MBQKeEUPhtV53LM22q37D24SHS8RSGRP65_TEwB-PSHFkq3Fz7MSILCxdiReVCYwncFm05pqcVonpcG8istg8M8zuyeXrrcwJ0zFccBJ4g7vjKHYphQk8A=s450-p-k',  # NOQA
             category=category1,
             user_id=user1.id)
session.add(item2)
session.commit()


print 'added menu items!'
