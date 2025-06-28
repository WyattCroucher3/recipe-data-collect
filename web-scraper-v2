# This version was updated to save the recipes in a json file, as well as handle multiple recipes at once

import requests
from bs4 import BeautifulSoup
import json
import os
import re

def extract_recipe(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)

            # Normalize JSON structure
            if isinstance(data, list):
                data = next((item for item in data if item.get('@type') == 'Recipe'), None)
            elif data.get('@type') != 'Recipe':
                data = data.get('@graph', [None])[0]

            if data and data.get('@type') == 'Recipe':
                instructions = data.get('recipeInstructions', [])
                # Flatten and clean instructions
                if instructions and isinstance(instructions[0], dict):
                    instructions = [step.get('text') for step in instructions]
                elif isinstance(instructions, str):
                    instructions = [instructions]

                recipe = {
                    'title': data.get('name'),
                    'ingredients': data.get('recipeIngredient'),
                    'instructions': instructions,
                    'nutrition': data.get('nutrition', {}),
                    'url': url
                }
                return recipe
        except (json.JSONDecodeError, TypeError):
            continue
    return None

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

def save_recipe(recipe, folder='recipes'):
    os.makedirs(folder, exist_ok=True)
    title = recipe.get('title') or "untitled_recipe"
    filename = sanitize_filename(title) + ".json"
    path = os.path.join(folder, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(recipe, f, ensure_ascii=False, indent=2)
    print(f"Saved: {filename}")

def process_urls(url_list):
    for url in url_list:
        print(f"\nProcessing: {url}")
        recipe = extract_recipe(url)
        if recipe:
            save_recipe(recipe)
        else:
            print("Recipe not found or not in expected format.")

# Example list of recipe URLs
urls = [
    "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/",
    "https://www.allrecipes.com/recipe/229960/quick-beef-stir-fry/"
]

process_urls(urls)
