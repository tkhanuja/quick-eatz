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
from .models import get_user_email


policy = Policy()
policy.set("ingredients", 'GET', authorize=True)
policy.set('recipes', "GET", authorize=True)
policy.set('ownership', "GET", authorize=True)


@unauthenticated("index")
def index(): 
    redirect(URL('api/forms'))
    return 

@action('user_error', method = ['GET'])
def user_error():
    return 'ERROR- PLEASE SIGN IN'

##########################################
# Search forms for authorized users
##########################################
@action('api/forms/auth', method=["GET", "POST"])
@action.uses(db, session, auth, auth.user, 'home_auth.html')
def forms():
    form = Form([Field('search_name'), Field('search_cuisine'), Field('search_cooktime'), Field('ingredient1'), Field('ingredient2'), Field('ingredient3'), Field('ingredient4'), Field('ingredient5'), Field('ingredient6'), Field('ingredient7'), Field('ingredient8'), Field('ingredient9'), Field('ingredient10'), Field('ingredient11'), Field(
        'ingredient12'), Field('ingredient13'), Field('ingredient14'), Field('ingredient15'), Field('ingredient16'), Field('ingredient17'), Field('ingredient18'), Field('ingredient19'), Field('ingredient20'), Field('ingredient21'), Field('ingredient22'), Field('ingredient23'), Field('ingredient24'), Field('ingredient25'), Field('ingredient26'), Field('ingredient27'), Field('ingredient28'), Field('ingredient29'), Field('ingredient30')], formstyle=FormStyleBulma, form_name='ingredients')
    ingredients = ''
    if form.accepted:
        search = request.params.get(
            'search_name') + ',' + request.params.get('search_cuisine') + ',' + request.params.get('search_cooktime')

        for i in range(1, 21):
            ingredient = request.params.get('ingredient'+str(i))
            
            if(str(ingredient) != ''):
                rows = db(db.user_groceries.email == get_user_email() and db.user_groceries.groceries == ingredient).select()
                if len(rows) ==0:
                    db.user_groceries.insert(email=get_user_email(), groceries=ingredient)
                ingredients = ingredients + ingredient + ','

        parameters = str(search) + ',' + str(ingredients)
        redirect(URL('api/search', str(parameters)))
    return dict(form=form)

##########################################
# Search forms for unauthorized users
##########################################
@action('api/forms', method=["GET", "POST"])
@action.uses(db, session,  'home.html')
def forms():
    if get_user_email() != None:
        redirect(URL('api/forms/auth'))
    form = Form([Field('search_name'), Field('search_cuisine'), Field('search_cooktime'), Field('ingredient1'), Field('ingredient2'), Field('ingredient3'), Field('ingredient4'), Field('ingredient5'), Field('ingredient6'), Field('ingredient7'), Field('ingredient8'), Field('ingredient9'), Field('ingredient10'), Field('ingredient11'), Field(
        'ingredient12'), Field('ingredient13'), Field('ingredient14'), Field('ingredient15'), Field('ingredient16'), Field('ingredient17'), Field('ingredient18'), Field('ingredient19'), Field('ingredient20'), Field('ingredient21'), Field('ingredient22'), Field('ingredient23'), Field('ingredient24'), Field('ingredient25'), Field('ingredient26'), Field('ingredient27'), Field('ingredient28'), Field('ingredient29'), Field('ingredient30')], formstyle=FormStyleBulma, form_name='ingredients')
    ingredients = ''
    if form.accepted:

        search = request.params.get(
            'search_name') + ',' + request.params.get('search_cuisine') + ',' + request.params.get('search_cooktime')

        for i in range(1, 21):
            ingredient = request.params.get('ingredient'+str(i))
            if(str(ingredient) != ''):
                ingredients = ingredients + ingredient + ','

        parameters = str(search) + ',' + str(ingredients)
        redirect(URL('api/search', str(parameters)))
    return dict(form=form)

##########################################
# Search funcs to filter results with several params
# x4 search filtering funcs

def filter_name(db, recipe, name):
    totalResults = 0
    results = db(db.recipes.name == '').select()
    if(len(recipe) != 0):

        for n in recipe:
            rows = db(db.recipes.name == n).select()

            rows += db(db.recipes.keyword1 == name).select()
            rows += db(db.recipes.keyword2 == name).select()
            rows += db(db.recipes.keyword3 == name).select()
            for r in rows:
                if r['name'] == name or r['keyword1'] == name or r['keyword2'] == name or r['keyword3'] == name:
                    totalResults += 1
                else:
                    if(r['name'] in recipe):
                        recipe.remove(r['name'])
    else:

        names = []
        rows = db(db.recipes.name == name).select()
        rows += db(db.recipes.keyword1 == name).select()
        rows += db(db.recipes.keyword2 == name).select()
        rows += db(db.recipes.keyword3 == name).select()
        totalResults = len(rows)
        for r in rows:
            recipe.append(r['name'])
    return recipe, totalResults


def filter_cuisine(db, names, cuisine):
    totalResults = 0
    results = db(db.recipes.name == '').select()
    if(len(names) != 0):
        for n in names:
            rows = db(db.recipes.name == n).select()
            if rows[0]['cuisine'] == cuisine:
                totalResults += 1
            else:
                names.remove(rows[0]['name'])
    else:
        names = []
        rows = db(db.recipe.cuisine == cuisine).select()
        totalResults = len(rows)
        for r in rows:
            names.append(r['name'])
    return names, totalResults


def filter_cooktime(db, names, cooktime):

    totalResults = 0
    results = db(db.recipes.name == '').select()
    if(len(names) != 0):

        for n in names:
            rows = db(db.recipes.name == n).select()
            if int(rows[0]['cooktime']) <= int(cooktime):
                totalResults += 1
            else:
                names.remove(rows[0]['name'])
    else:
        names = []
        rows = db(db.recipes.cooktime <= cooktime).select()
        totalResults = len(rows)
        for r in rows:
            names.append(r['name'])
    return names, totalResults


def filter_ingredients(db, recipes, ingredients):
    ingredients = ingredients.split(',')
    recipes = {}
    doable = []
    totalResults = 0
    results = {}
    # search list of ingredients
    for ingredient in ingredients:
        # ingredient

        ing1 = db(db.ingredients.ingredients == ingredient).select()
        #keywords in ingredients
        ing2 = db(db.ingredients.keyword1 == ingredient).select()
        ing3 = db(db.ingredients.keyword2 == ingredient).select()
        rows = ing1+ing2+ing3

        if (len(rows) > 0):
            # if ingredient or keywords exists, use ingredient's id to get recipe ownership
            # if keyword is being used(ing2 & ing3) then set substitute table to true
            # sub = []
            rows2 = db(db.ownership.ingredient == '').select()
            if(len(ing1) != 0):
                own1 = db(db.ownership.ingredient == ing1[0]['id']).select()
                if(len(own1) != 0):
                    rows2 += own1
                    # sub = [False] * len(own1)
            if(len(ing2) != 0):
                own2 = db(db.ownership.ingredient == ing2[0]['id']).select()
                if(len(own2) != 0):
                    rows2 += own2
                    # sub = sub + [True]* len(own2)
            if(len(ing3) != 0):
                own3 = db(db.ownership.ingredient == ing3[0]['id']).select()
                if(len(own3) != 0):
                    rows2 += own3
                    # sub = sub + [True] * len(own3)
            # select recipes from ownership
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
    return doable, totalResults

# End of search filtering funcs
##########################################

##########################################
# Search Function for finding recipes 
# that match the parameters
##########################################
@action('api/search/<parameters>', method=['GET'])
@action.uses(db, session, auth, 'index.html')
def searches(parameters):
    # parse the data
   
    parameters = parameters.split(',')
    ingredients = ''
    for i in range(3, len(parameters)):
        ingredients += str(parameters[i])+','
    # index 1 = name
    # index 2 = cuisine
    # index 3 = cooktime

    # only ingredients
    if (parameters[0] == '' and parameters[1] == '' and parameters[2] == '' and ingredients != ''):
        redirect(URL('api/ingredients', str(ingredients)))
    # only name
    elif (str(parameters[0]) != '' and parameters[1] == '' and parameters[2] == '' and ingredients == ','):
        redirect(URL('api/name', str(parameters[0])))
    # only cuisine
    elif (parameters[0] == '' and parameters[1] != '' and parameters[2] == '' and ingredients == ','):
        redirect(URL('api/cuisine', str(parameters[1])))
    # only cooktime
    elif (parameters[0] == '' and parameters[1] == '' and parameters[2] != '' and ingredients == ','):

        redirect(URL('api/cooktime', int(parameters[2])))
    else:
        recipes = []
        totalResults = 0
        if(len(ingredients) > 1):

            data = filter_ingredients(db, recipes, ingredients)
            recipes = data[0]
            totalResults = data[1]
            if(len(recipes) == 0):
                return "Error no recipes"
        if(parameters[0] != ''):
            data = filter_name(db, recipes, parameters[0])
            recipes = data[0]
            totalResults = data[1]
            if(len(recipes) == 0):
                return "Error no recipes"
        if(parameters[1] != ''):
            data = filter_cuisine(db, recipes, parameters[1])
            recipes = data[0]
            totalResults = data[1]
            if(len(recipes) == 0):
                return "Error no recipes"
        if(parameters[2] != ''):
            data = filter_cooktime(db, recipes, parameters[2])
            recipes = data[0]
            totalResults = data[1]
            if(len(recipes) == 0):
                return "Error no recipes"
    
    return dict(numResults=totalResults, names=recipes)

##########################################
# Class to remove all html tags from string
# used in data cleaning for recipe information

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
##########################################

##########################################
# Get recipe information to display
# on a single page
##########################################

@action('api/information/<name>', method=['GET'])
@action.uses(db, session, auth, 'recipe.html')
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

##########################################
# 2 funcs to save and display the users 
# saved recipes
# for authorized users only
@action('api/save_recipe/<recipe_id>', method = ['GET'])
@action.uses(db, session, auth,'recipe.html' )
def save_recipe(recipe_id):
    assert recipe_id is not None
    if get_user_email()== None:
        return jsonify('error')
    db.user_recipes.insert(email = get_user_email(),recipe = recipe_id )
    q = db.recipes[recipe_id]
    redirect(URL('api/information', q.name))

@action('api/user_recipes', method = ["GET"])
@action.uses(db, session, auth, auth.user, 'index.html')
def user_recipes():
   
    rows = db(db.user_recipes.email == get_user_email()).select()
    names = []
    ct = 0
    for r in rows:
        rows2 = db(db.recipes.id == r.id).select()
        names.append(rows2[0].name)
        ct+=1
    print (names)
    return dict(numResults = ct, names = names)

##########################################


##########################################
# Saved Grocery list for authorized users
##########################################
@action('api/grocery', method=["GET", "POST"])
@action.uses(db, session, auth, auth.user,  'grocery_list.html')
def forms():
    
    user = get_user_email()

    form = Form([Field('search_name'), Field('search_cuisine'), Field('search_cooktime')], formstyle=FormStyleBulma)
    rows = db(db.user_groceries.email == user).select()
    search = ''
    if form.accepted:
        search = request.params.get(
            'search_name') + ',' + request.params.get('search_cuisine') + ',' + request.params.get('search_cooktime')+','
        for r in rows:
            search+= str(r['groceries'])+','
        redirect(URL('api/search', str(search)))
    return dict(groceries=rows, form = form)

##########################################
# Update grocery list for auth users

@action('add', method=['GET', 'POST'])
@action.uses(db, auth,auth.user 'add.html')
def add():
    form = Form([Field('Ingredient')], formstyle=FormStyleBulma)
    if form.accepted:
        i = request.params.get('Ingredient')
        db.user_groceries.insert(email = get_user_email(), groceries = i )
        redirect(URL('api/grocery'))
    return dict(form=form)

@action('edit/<ing_id>', method=['GET', 'POST'])
@action.uses(db, auth,auth.user 'edit.html')
def edit(ing_id=None):

    assert ing_id is not None
    p = db.user_groceries[ing_id]

    if p is None or p.email != get_user_email():
        return jsonify({'message': 'Please sign in'})
        redirect(URL('api/grocery'))
    form = Form(db.user_groceries, record=p,csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('api/grocery'))
    return dict(form=form)
# End of Grocery list updating funcs
##########################################

@action('api/mealplan', method=['GET', 'POST'])
@action.uses(db)
def meal_plan():
    return

##########################################
# Functions that serve to comply additional
# search parameters the user may want
# x5 funcs 

@action('api/cuisine/<cuisine>', method=['GET'])
@action.uses(db, 'index.html')
def cuisine(cuisine):
    rows = db(db.recipes.cuisine == cuisine).select()
    totalResults = len(rows)
    names = []
    for r in rows:
        names.append(r['name'])
    return dict(numResults=totalResults, names=names)


@action('api/cooktime/<cooktime>', method=['GET'])
@action.uses(db, 'index.html')
def cooktime(cooktime):
    rows = db(db.recipes.cooktime <= cooktime).select()
    totalResults = len(rows)
    names = []
    for r in rows:
        names.append(r['name'])
    return dict(numResults=totalResults, names=names)


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
    return doable


@action('api/name/<name>', method=['GET'])
@action.uses(db, 'index.html')
def name(name):

    totalResults = 0

    rows = db(db.recipes.name == name).select()
    results = rows
    totalResults += len(rows)

    # key1
    rows = db(db.recipes.keyword1 == name).select()
    totalResults += len(rows)
    results += rows

    # key2
    rows = db(db.recipes.keyword2 == name).select()
    totalResults += len(rows)
    results += rows
    # key3
    rows = db(db.recipes.keyword3 == name).select()
    totalResults += len(rows)
    results += rows

    names = []
    for r in results:

        names.append(r['name'])
    return dict(numResults=totalResults, names=names)

# End of search funcs
##########################################