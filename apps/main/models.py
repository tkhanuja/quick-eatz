"""
This file defines the database models
"""

# from .common import Field
import datetime
from py4web import DAL, Field
from pydal.validators import *
import os
from .common import db, auth


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


def get_time():
    return datetime.datetime.utcnow()
db.define_table('recipes',
                Field('name', type='string', unique = True),
                Field('cooktime', type='integer'),
                Field('cuisine', type='string', default="American"),
                Field("instructions", type="string"),
                Field('description', type='string'),
                Field('image', type="string"),
                Field('number', type="integer"),
                Field('keyword1', type='string'),
                Field('keyword2', type='string'),
                Field('keyword3', type = 'string')
                )

db.define_table('ingredients',
                Field('ingredients', type='string', unique =True),
                Field('keyword1', type='string'),
                Field('keyword2', type='string'))

db.define_table('ownership',
                Field('recipe', type='reference recipes'),
                Field('ingredient', type='reference ingredients'),
                Field('amount', type='string'))
db.define_table('user_groceries',
                Field('email', writable = False),
                Field('groceries'))
db.commit()
recipes_and_ingredients = db((db.recipes.id == db.ownership.recipe) and (
    db.ingredients.id == db.ownership.ingredient))
