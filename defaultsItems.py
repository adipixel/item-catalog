#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category
(Base, )
Item

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

category1 = Category(name='Voice Assistants')

session.add(category1)
session.commit()

item1 = Item(name='Google Home',
             description='Google Assistant with voice powered smart home device',  # NOQA
             image='https://lh3.googleusercontent.com/igThvoKwToXtZOfTANWbgp2ZoLnPBV2KDt9oJuaK419yIHQIo24eIcsCbgWcnfwlFjs=w300',  # NOQA
             category=category1)

session.add(item1)
session.commit()

item2 = Item(name='Google Home Mini',
             description='Google Assistant with voice powered smart home device',  # NOQA
             image='https://brain-images-ssl.cdn.dixons.com/8/9/10171098/u_10171098.jpg',  # NOQA
             category=category1)
session.add(item2)
session.commit()

item3 = Item(name='Amazon Alexa Echo',
             description='Amazon Alexa with voice powered smart home device',
             image='', category=category1)
session.add(item3)
session.commit()

item4 = Item(name='Amazon Alexa Echo Dot',
             description='Compact version of Amazon Alexa Echo',
             image='', category=category1)
session.add(item4)
session.commit()

category2 = Category(name='Wearable')

session.add(category1)
session.commit()

item5 = Item(name='Samsung Gear S3',
             description='A smartwatch for tracking activity and managing quick tasks with heartrate sensor',  # NOQA
             image='', category=category2)
session.add(item5)
session.commit()

item6 = Item(name='Apple series 3 watch',
             description='A smartwatch for tracking activity and managing quick tasks with heartrate sensor,'  # NOQA
             image='', category=category2)
session.add(item6)
session.commit()

item7 = Item(name='Fossil Marshal',
             description='A smartwatch for tracking activity and managing quick tasks with heartrate sensor',  # NOQA
             image='', category=category2)
session.add(item7)
session.commit()

item8 = Item(name='Fitbit',
             description='Activity tracker with heartrate sensor',
             image='', category=category2)
session.add(item8)
session.commit()

print 'added menu items!'
