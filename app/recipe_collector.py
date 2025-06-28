# recipe_collector.py

import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from recipe_manager import save_recipe_to_file

DATA_DIR = os.path.join("data", "recipes")
IMAGE_DIR = os.path.join("data", "images")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

def clean_nutrition_value(value):
    try:
        return float(value.replace(" g", "").replace("kcal", "").strip())
    except:
        return None

def download_image(url, title):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = sanitize_filename(title) + ".jpg"
            path = os.path.join(IMAGE_DIR, filename)
            with open(path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return path
    except:
        return None
    return None

def extract_recipe(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception:
        return None

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

                image_url = data.get('image')
                if isinstance(image_url, list):
                    image_url = image_url[0]

                recipe = {
                    'title': data.get('name'),
                    'ingredients': data.get('recipeIngredient', []),
                    'instructions': instructions,
                    'nutrition': data.get('nutrition', {}),
                    'url': url
                }

                if image_url:
                    img_path = download_image(image_url, recipe['title'])
                    if img_path:
                        recipe['image_path'] = img_path

                return recipe
        except Exception:
            continue
    return None

def recipe_matches_filters(recipe, banned_ingredients, nutrition_filters):
    ingredients = " ".join(ingredient.lower() for ingredient in recipe.get('ingredients', []))
    for banned in banned_ingredients:
        if banned in ingredients:
            return False

    nutrition = recipe.get('nutrition', {})
    for field, condition in nutrition_filters.items():
        val = clean_nutrition_value(nutrition.get(field, "0 g"))
        if val is None or not condition(val):
            return False
    return True

def find_recipe_urls(search_query, max_count):
    encoded = quote(search_query)
    base_url = f"https://www.allrecipes.com/search?q={encoded}"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.select("a[href*='/recipe/']")
    urls = []
    seen = set()
    for link in links:
        href = link.get("href")
        if href and href not in seen and "/recipe/" in href:
            seen.add(href)
            urls.append(href)
            if len(urls) >= max_count:
                break
    return urls

def collect_recipes(search, max_results, banned_ingredients, nutrition_filters):
    urls = find_recipe_urls(search, max_results * 2)
    collected = []

    for url in urls:
        if len(collected) >= max_results:
            break
        recipe = extract_recipe(url)
        if recipe and recipe_matches_filters(recipe, banned_ingredients, nutrition_filters):
            save_recipe_to_file(recipe)
            collected.append(recipe)

    return collected