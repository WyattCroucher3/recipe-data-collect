# code was updated to handle csv export

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import csv

def extract_recipe(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            data = json.loads(script.string)

            if isinstance(data, list):
                data = next((item for item in data if item.get('@type') == 'Recipe'), None)
            elif data.get('@type') != 'Recipe':
                data = data.get('@graph', [None])[0]

            if data and data.get('@type') == 'Recipe':
                instructions = data.get('recipeInstructions', [])
                if isinstance(instructions, list):
                    instructions = [step.get('text') if isinstance(step, dict) else step for step in instructions]
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

def save_recipe_json(recipe, folder='recipes'):
    os.makedirs(folder, exist_ok=True)
    title = recipe.get('title') or "untitled_recipe"
    filename = sanitize_filename(title) + ".json"
    path = os.path.join(folder, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(recipe, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {filename}")

def save_recipes_csv(recipe_list, filename='recipes_summary.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'URL', 'Ingredients', 'Instructions', 'Calories', 'Fat', 'Protein']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for recipe in recipe_list:
            nutrition = recipe.get('nutrition', {})
            writer.writerow({
                'Title': recipe.get('title'),
                'URL': recipe.get('url'),
                'Ingredients': "; ".join(recipe.get('ingredients', [])),
                'Instructions': " ".join(recipe.get('instructions', [])),
                'Calories': nutrition.get('calories', ''),
                'Fat': nutrition.get('fatContent', ''),
                'Protein': nutrition.get('proteinContent', '')
            })
    print(f"CSV export complete: {filename}")

def process_urls(url_list):
    collected_recipes = []
    for url in url_list:
        print(f"\nProcessing: {url}")
        recipe = extract_recipe(url)
        if recipe:
            collected_recipes.append(recipe)
            save_recipe_json(recipe)
        else:
            print("Recipe not found or not in expected format.")
    if collected_recipes:
        save_recipes_csv(collected_recipes)

# Example URLs
urls = [
    "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/",
    "https://www.allrecipes.com/recipe/229960/quick-beef-stir-fry/"
]

process_urls(urls)
