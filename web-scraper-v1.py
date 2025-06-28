# inital version that loads a single recipe into a json file

import requests 
from bs4 import BeautifulSoup
import json

def extract_recipe(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find JSON-LD data
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)
            # Sometimes JSON-LD is a list, not a dict
            if isinstance(data, list):
                data = next((item for item in data if item.get('@type') == 'Recipe'), None)
            elif data.get('@type') != 'Recipe':
                data = data.get('@graph', [None])[0]
            if data and data.get('@type') == 'Recipe':
                recipe = {
                    'title': data.get('name'),
                    'ingredients': data.get('recipeIngredient'),
                    'instructions': [step.get('text') if isinstance(step, dict) else step
                                     for step in data.get('recipeInstructions', [])],
                    'nutrition': data.get('nutrition', {})
                }
                return recipe
        except (json.JSONDecodeError, TypeError):
            continue
    return None

# Example usage
url = 'https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/'
recipe_data = extract_recipe(url)

if recipe_data:
    print("Title:", recipe_data['title'])
    print("\nIngredients:")
    for item in recipe_data['ingredients']:
        print("-", item)
    print("\nInstructions:")
    for step in recipe_data['instructions']:
        print("-", step)
    print("\nNutrition Info:")
    print(recipe_data['nutrition'])
else:
    print("Recipe not found or not in expected format.")
