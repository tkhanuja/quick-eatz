"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from .common import session, T, cache, auth, logger, authenticated, unauthenticated, flash
from pydal.restapi import RestAPI, Policy
from .models import db
from py4web.utils.url_signer import URLSigner
from py4web.core import Template
from .settings import APP_FOLDER
from py4web.utils.form import Form, FormStyleBulma
import json, os
import urllib
from io import StringIO
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

policy = Policy()
policy.set("ingredients", 'GET', authorize=True)
policy.set('recipes', "GET", authorize=True)
policy.set('ownership', "GET", authorize=True)


@unauthenticated("index")
def index(): 
    return 


@action('api/forms', method=["GET", "POST"])
@action.uses(db, session, auth, auth.user, 'home.html')
def forms():
    form = Form([Field('ingredient1'), Field('ingredient2'), Field('ingredient3'), Field('ingredient4'), Field('ingredient5'), Field('ingredient6'), Field('ingredient7'), Field('ingredient8'), Field('ingredient9'), Field('ingredient10'), Field('ingredient11'), Field('ingredient12'), Field('ingredient13'), Field('ingredient14'), Field('ingredient15'), Field('ingredient16'), Field('ingredient17'), Field('ingredient18'), Field('ingredient19'), Field('ingredient20') ],formstyle=FormStyleBulma)
    ingredients= ''
    if form.accepted:
        for i in range(1,21):
            ingredient = request.params.get('ingredient'+str(i))
            if(str(ingredient) != ''):
                ingredients = ingredients + ingredient +','
        redirect(URL('api/ingredients', str(ingredients) ) )
    return dict(form = form) 

##########################################
# Function ingredients accepts a string of
# ingredients and returns all possible recipes
# made by those ingredients
##########################################

# def clean_data(ingredients):
    
#     return ingredients



@action('api/ingredients/<ingredients>', method=['GET', 'POST'])
@action.uses(db,'index.html')
def ingredients(ingredients):

    # get list 
    ingredients = ingredients.split(',')
    #remove last empty space
    ingredients.pop(len(ingredients)-1)

    recipes = {}
    doable = []
    totalResults = 0
    results = {}
    
    # search list of ingredients
    
    for ingredient in ingredients:
        ing1 = db(db.ingredients.ingredients == ingredient).select()
        ing2 = db(db.ingredients.keyword1 == ingredient).select()
        ing3 = db(db.ingredients.keyword2 == ingredient).select()
        
        rows = ing1+ing2+ing3
       
        if (len(rows) > 0):
            # if ingredient or keywords exists, use ingredient's id to get recipe ownership
            #if keyword is being used(ing2 & ing3) then set substitute table to true
            # sub = []
            if(len(ing1) != 0):
                own1 = db(db.ownership.ingredient == ing1[0]['id']).select()
                if(len(own1) != 0):
                    rows2 = own1
                    # sub = [False] * len(own1)
            if(len(ing2) != 0):
                own2 = db(db.ownership.ingredient == ing2[0]['id']).select()
                if(len(own1) != 0):
                    rows2 = own1 +own2
                    # sub = sub + [True]* len(own2)
            if(len(ing3) != 0):
                own3 = db(db.ownership.ingredient == ing3[0]['id']).select()
                if(len(own3) != 0):
                    rows2 = own1 +own2+ own3
                    # sub = sub + [True] * len(own3)
            for row in rows2:
                rows3 = db(db.recipes.id == row['recipe']).select()
                # keep track of number of ingredients found for each recipe
                if (rows3[0]['name'] not in recipes):
                    recipes[rows3[0]['name']] = 1
                else:
                    recipes[rows3[0]['name']] += 1
                # save data if recipe is doable with ingredients found
                if (recipes[rows3[0]['name']] == rows3[0]['number']):

                    doable.append(rows3[0]['name'])
                    totalResults += 1
                    # rows4 = db(db.ownership.recipe == rows3[0]['id']).select()
                    # ingredient_list = {}
                    # for i in range(0, len(rows4)):
                    #     rows5 = db(db.ingredients.id ==
                    #                rows4[i]['id']).select()
                    #     ingredient_list[list(rows5)[0]['ingredients']] = rows4[i]['amount']
                    # results[rows3[0]['name']] = ingredient_list
               
    return dict(names= doable, numResults = totalResults )


@action('api/information/<name>', method=['GET'])
@action.uses(db, 'recipe.html')
def information(name):
    ingredient_information = {}
    row = db(db.recipes.name == name ).select()
    
    row2 = db(db.ownership.recipe == row[0]['id']).select()
    
    for rows in row2:
        row3 = db(db.ingredients.id == rows['ingredient']).select()
        ingredient_information[row3[0]['ingredients']]= rows['amount']

    instructions= strip_tags(row[0]['instructions'])
    description = strip_tags(row[0]['description'])

    return dict(recipe=row, ingredients=ingredient_information.keys(), amounts=ingredient_information, instructions=instructions, descriptions=description)


@action('api/cuisine/<cuisine>', method=['GET'])
@action.uses(db)
def cuisine(cuisine):
    rows = db(db.recipes.cuisine == cuisine).select()
    return rows.json()


@action('api/cooktime/<cooktime>', method=['GET'])
@action.uses(db)
def cooktime(cooktime):
    rows = db(db.recipes.cooktime == cooktime).select()
    return rows.json()


@action('api/ingredient/<ingredient>', method=['GET'])
@action.uses(db)
def single_ingredient(ingredient):
    doable = []
    rows = db(db.ingredients.ingredients == ingredient).select()
    if (len(rows) > 0):
        # if ingredient exists, use ingredient's id to get recipe ownership
        rows2 = db(db.ownership.ingredient == rows[0]['id']).select()
        for row in rows2:
            # get and save recipe
            rows3 = db(db.recipes.id == row['recipe']).select()
            doable.append(rows3.json())
    # print(doable[0][0]['id'])
    return doable


@action('api/name/<name>', method=['GET'])
@action.uses(db)
def name(name):
    results = []
    totalResults = 0
    rows = db(db.recipes.name == name).select()
    if (rows):
        totalResults += len(rows)
        results.append(rows.json())
    # key1
    rows = db(db.recipes.keyword1 == name).select()
    if (rows):
        totalResults += len(rows)
        results.append(rows.json())
    # key2
    rows = db(db.recipes.keyword2 == name).select()
    if(rows):
        results.append(rows.json())
    # key3
    rows = db(db.recipes.keyword3 == name).select()
    if (rows):
        totalResults += len(rows)
        results.append(rows.json())

    return results
