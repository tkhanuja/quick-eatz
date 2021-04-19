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

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import session, T, cache, auth, logger, authenticated, unauthenticated, flash
from pydal.restapi import RestAPI, Policy
from .models import db
from py4web.utils.url_signer import URLSigner
from py4web.core import Template
from .settings import APP_FOLDER
import json, os
import urllib

policy = Policy()
policy.set("ingredients", 'GET', authorize=True)
policy.set('recipes', "GET", authorize=True)
policy.set('ownership', "GET", authorize=True)


@unauthenticated("index", "index.html")
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    return dict(message=message)


def format_data(response):
    ret = [response[0]['image'], response[0]['name'],
           response[0]['cooktime'], response[0]['cuisine'], response[0]['description'], response[0]['instructions']]

    # url = response[0]['image']
    # ret['image'] = Image.open(urllib.urlopen(url))
    # ret['image'] = response[0]['image']
    # ret['name'] = response[0]['name']
    # ret['cooktime'] = response[0]['cooktime']
    # ret['cuisine'] = response[0]['cuisine']
    # ret['description'] = response[0]['description']
    # ret['instructions'] = response[0]['instructions']
    # print(response[0]['description'])
    return ret


##########################################
# Function ingredients accepts a string of
# ingredients and returns all possible recipes
# made by those ingredients
##########################################
@action('api/ingredients/<ingredient>', method=['GET'])
@action.uses(db,'index.html')
def ingredients(ingredient):
    recipes = {}
    doable = []
    totalResults = 0
    results = {}
    # get list split
    ingredients = ingredient.split(',')
    # search list of ingredients
    for ingredient in ingredients:
        rows = db(db.ingredients.ingredients == ingredient).select()
        if (len(rows) > 0):
            # if ingredient exists, use ingredient's id to get recipe ownership
            rows2 = db(db.ownership.ingredient == rows[0]['id']).select()
            for row in rows2:
                # get recipe
                rows3 = db(db.recipes.id == row['recipe']).select()
                # data.append(rows3.json())
                # keep track of number of ingredients found for each recipe
                if (rows3[0]['name'] not in recipes):
                    recipes[rows3[0]['name']] = 1
                else:
                    recipes[rows3[0]['name']] += 1
                # save data if recipe is doable with ingredients found
                if (recipes[rows3[0]['name']] == rows3[0]['number']):
                    # rows3 = format_data(rows3)
                    
                    doable.append(list(rows3))
                    # print(doable[0][0])
                    totalResults += 1
                    rows4 = db(db.ownership.recipe == rows3[0]['id']).select()
                    ingredient_list = {}
                    for i in range(0, len(rows4)):
                        rows5 = db(db.ingredients.id ==
                                   rows4[i]['id']).select()
                        ingredient_list[list(rows5)[0]['ingredients']] = rows4[i]['amount']
                    results[rows3[0]['name']] = ingredient_list
                    # print(ingredient_list)
    # results: ingredient/ownership info
    # doable: recipe info
    # print(doable[0][0]['id'])
    #doable[i][i][field]= field
    # print(results)
    # print(doable)
    return dict(ingredients = results, information= doable )


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
