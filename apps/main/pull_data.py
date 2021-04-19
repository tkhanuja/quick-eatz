# from .models import db
# import spoonacular as sp
import requests
from models import db
headers = {
    'apikey': "41c5375312354ae1befe373d0f7f7fb8"
}


class API(object):

    def complex_search(self, query, number):
        url = 'https://api.spoonacular.com/recipes/complexSearch?apiKey=' + headers['apikey']
        querystring = {'query': query, 'number': number,'instructionsRequired': True}
        response = requests.request("GET", url, headers=headers, params=querystring)
        response = response.json()
        if response['totalResults']==0:
            return None
        return response

    def recipe_information(self, id):
        querystring = {'id': id}
        id = str(id)
        url = "https://api.spoonacular.com/recipes/"+id + "/information?apiKey="+ headers['apikey']+ "&includeNutrition=true"
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        response = response.json()
        return response

    def get_ID(self, response):
        return (response['results'][0]['id'])

    def get_name(self, response):
        return response['title'].lower()

    def get_instructions(self, response):
        return response['instructions']

    def get_cuisine(self, response):
        if len(response['cuisines'])==0 :
            return "American"
        return response['cuisines']

    def get_cooktime(self, response):
        if 'readyInMinutes' not in response:
            return ""
        return response['readyInMinutes']

    def get_image(self, response):
        if 'image' not in response:
            return ""
        return response['image']

    def get_description(self, response):
        return response['summary']

    def get_number_ingredients(self, response):
        return (len(response['extendedIngredients']))

    def get_ingredients(self, response):
        ingredients = {}
        # print(response)
        for i in range(0, len(response['extendedIngredients'])):
            ingredients[(response['extendedIngredients'][i]['name'])] = str(response['extendedIngredients'][i]
                                                                            ['measures']['us']['amount']) + " " + response['extendedIngredients'][i]['measures']['us']['unitLong']
        return ingredients
    def get_multiple_id(self, response):
        id_list = []
        for i in range(0, len(response['results'])):
            id_list.append(response['results'][i]['id'])
        return id_list

    def request_populate(self, query, number):
        data = self.complex_search(query, number)
        #if response exists
        if(data != None):
            id_list = self.get_multiple_id(data)
            #get request for each id
            for id in id_list:
                data = self.recipe_information(id)
                try:
                    self.populate_ingredients_table(data)
                    self.populate_recipes_table(data)
                    self.populate_ownership_table(data)
                except Exception as e:
                    print("Error populate_tables")
                    print(e)
                    print('---------------------')
        

    def make_requests_id(self, id):
        # data = self.complex_search(query)
        try:
            # id = self.get_ID(data)
            data = self.recipe_information(id)
            return data
        except:
            print("Error make_requests")
        
        

    def populate_tables_id(self, id):
        data = self.make_requests_id(id)
        # print(data)
        try:
            self.populate_ingredients_table(data)
            self.populate_recipes_table(data )
            self.populate_ownership_table(data)
        except Exception as e:
            print(e)
            print("Error populate_tables")
       

    def populate_ingredients_table(self, data):
        ingredients_table = self.get_ingredients(data)
        # print(ingredients_table)
        ingredients_list = ingredients_table.keys()
        
        for ingredient in ingredients_list:
            key1 = "None"
            key2 = "None"
            ingredient = ingredient.lower()
            #make sure its unique
            if(len(db(db.ingredients.ingredients == ingredient).select())== 0):
                if(' ' in ingredient):
                    ing = ingredient.rsplit(' ')
                    if (ing[1] and ing[0]):
                        key1 = ing[0]
                        key2 = ing[1]
                # print(ingredient)
                db.ingredients.insert(ingredients=ingredient, keyword1 = key1, keyword2 = key2)
                row = db(db.ingredients.ingredients == ingredient).select()
            # print(row)
                db.commit()
        return

    def populate_recipes_table(self, data):
        instructions = self.get_instructions(data)
        if(len(instructions)!= 0):
            name = self.get_name(data)
            key1 = "None"
            key2 = "None"
            key3 = "None"
            if(' ' in name):
                keywords = name.rsplit(' ')
                if (keywords[1] and keywords[0] ):
                    key1 = keywords[0]
                    key2 = keywords[1]
                    if(keywords[2]):
                        key3 = keywords[2]
            cooktime = self.get_cooktime(data)
            description = self.get_description(data)
            image = self.get_image(data)
            cuisine = self.get_cuisine(data)
            number = self.get_number_ingredients(data)
            db.recipes.insert(name=name, cooktime=cooktime, cuisine=cuisine,
                            instructions=instructions, description=description, image=image, number=number, keyword1 = key1, keyword2 = key2, keyword3 = key3)
            db.commit()

    def populate_ownership_table(self, data):
        name = self.get_name(data)
        row = db(db.recipes.name == name).select()
        if(len(row) != 0):
            name_id = row[0]['id']
            ingredients_table = self.get_ingredients(data)
            ingredients_list = ingredients_table.keys()
            for ingredients in ingredients_list:
                amount = ingredients_table[ingredients]
                row = db(db.ingredients.ingredients == ingredients).select()
                ingredient_id = row[0]['id']
                db.ownership.insert(recipe=name_id, ingredient=ingredient_id, amount=amount)
                db.commit()

    


response = API()
foods = ['seafood', 'sandwiches']
i = 0
for food in foods:
    i+=1
    print(i)
    response.request_populate(food, 100)
# #range(1000000, 1000150)
# for food in range(100, 101):
#     print(food)
#     response.populate_tables(food)
