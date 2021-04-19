"""
This file defines the database models
"""

from py4web import DAL, Field


db = DAL(uri='sqlite://recipes.db')

db.define_table('recipes',
                Field('name', type='string'),
                Field('cooktime', type='integer'),
                Field('cuisine', type='string', default= "American"),
                Field("instructions", type="string"),
                Field('description', type='string'),
                Field('image', type="string"),
                Field('number', type = "integer")
                )

db.define_table('ingredients',
                Field('ingredients', type='string'))

db.define_table('ownership',
                Field('recipe', type='reference recipes'),
                Field('ingredient', type='reference ingredients'),
                Field('amount', type='string'))
db.commit()
recipes_and_ingredients = db((db.recipes.id == db.ownership.recipe) and (
    db.ingredients.id == db.ownership.ingredient))







