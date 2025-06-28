# recipe_manager.py

import os
import json
import csv
from glob import glob

DATA_DIR = os.path.join("data", "recipes")
CSV_PATH = os.path.join("data", "recipes_summary.csv")

def sanitize_filename(name):
    import re
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

def load_recipes():
    recipes = []
    for filepath in glob(os.path.join(DATA_DIR, "*.json")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                recipe = json.load(f)
                recipes.append(recipe)
        except:
            continue
    return recipes

def save_recipe_to_file(recipe):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    title = recipe.get('title', 'untitled')
    filename = os.path.join(DATA_DIR, f"{sanitize_filename(title)}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(recipe, f, ensure_ascii=False, indent=2)

def export_all_to_csv(recipes):
    if not os.path.exists(os.path.dirname(CSV_PATH)):
        os.makedirs(os.path.dirname(CSV_PATH))

    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'URL', 'Ingredients', 'Instructions', 'Calories', 'Fat', 'Protein', 'Carbs']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for recipe in recipes:
            nutrition = recipe.get('nutrition', {})
            writer.writerow({
                'Title': recipe.get('title'),
                'URL': recipe.get('url', ''),
                'Ingredients': "; ".join(recipe.get('ingredients', [])),
                'Instructions': " ".join(recipe.get('instructions', [])),
                'Calories': nutrition.get('calories', ''),
                'Fat': nutrition.get('fatContent', ''),
                'Protein': nutrition.get('proteinContent', ''),
                'Carbs': nutrition.get('carbohydrateContent', '')
            })