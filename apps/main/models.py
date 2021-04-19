"""
This file defines the database models
"""

# from .common import Field
from py4web import DAL, Field
from pydal.validators import *
from py4web.core import required_folder
import os
APP_FOLDER = os.path.dirname(__file__)
APP_NAME = os.path.split(APP_FOLDER)[-1]
DB_FOLDER = required_folder(APP_FOLDER, "databases")
DB_URI = "sqlite://recipes.db"
DB_POOL_SIZE = 1
DB_MIGRATE = True
DB_FAKE_MIGRATE = False
db = DAL(
    DB_URI,
    folder=DB_FOLDER,
    pool_size=DB_POOL_SIZE,
    migrate=DB_MIGRATE,
    fake_migrate=DB_FAKE_MIGRATE,
)


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
db.commit()
recipes_and_ingredients = db((db.recipes.id == db.ownership.recipe) and (
    db.ingredients.id == db.ownership.ingredient))
