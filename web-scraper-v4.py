# altered version that discovers URLs automatically and applies filters 

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import csv
from urllib.parse import quote

# --------------------------
# CONFIGURATION
# --------------------------

SEARCH_QUERY = "chicken"
NUM_RECIPES_TO_FETCH = 5

BANNED_INGREDIENTS = ["milk", "peanuts", "walnuts"]
NUTRITION_FILTERS = {
    "fatContent": lambda x: float(x.rstrip(" g")) < 15,
    "proteinContent": lambda x: float(x.rstrip(" g")) >= 20,
    "carbohydrateContent": lambda x: float(x.rstrip(" g")) <= 30,
}

# --------------------------
# UTILITY FUNCTIONS
# --------------------------

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

def clean_nutrition_value(value):
    try:
        return float(value.replace(" g", "").replace("kcal", "").strip())
    except:
        return None

def recipe_matches_filters(recipe):
    # Ingredient check
    ingredients = " ".join(ingredient.lower() for ingredient in recipe.get('ingredients', []))
    for banned in BANNED_INGREDIENTS:
        if banned.lower() in ingredients:
            return False

    # Nutrition check
    nutrition = recipe.get('nutrition', {})
    for field, condition in NUTRITION_FILTERS.items():
        val = clean_nutrition_value(nutrition.get(field, "0 g"))
        if val is None or not condition(val):
            return False
    return True

# --------------------------
# RECIPE SCRAPER
# --------------------------

def extract_recipe(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
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

                recipe = {
                    'title': data.get('name'),
                    'ingredients': data.get('recipeIngredient', []),
                    'instructions': instructions,
                    'nutrition': data.get('nutrition', {}),
                    'url': url
                }
                return recipe
        except Exception:
            continue
    return None

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

# --------------------------
# OUTPUT FUNCTIONS
# --------------------------

def save_recipe_json(recipe, folder='recipes'):
    os.makedirs(folder, exist_ok=True)
    title = recipe.get('title') or "untitled_recipe"
    filename = sanitize_filename(title) + ".json"
    path = os.path.join(folder, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(recipe, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved JSON: {filename}")

def save_recipes_csv(recipe_list, filename='recipes_summary.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'URL', 'Ingredients', 'Instructions', 'Calories', 'Fat', 'Protein', 'Carbs']
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
                'Protein': nutrition.get('proteinContent', ''),
                'Carbs': nutrition.get('carbohydrateContent', '')
            })
    print(f"📄 CSV export complete: {filename}")

# --------------------------
# MAIN WORKFLOW
# --------------------------

def main():
    print(f"\n🔍 Searching for: '{SEARCH_QUERY}'...")
    urls = find_recipe_urls(SEARCH_QUERY, NUM_RECIPES_TO_FETCH * 2)  # fetch extras for filtering
    print(f"🔗 Found {len(urls)} recipe URLs. Processing...")

    saved = []
    for url in urls:
        if len(saved) >= NUM_RECIPES_TO_FETCH:
            break
        print(f"\n➡️ Checking: {url}")
        recipe = extract_recipe(url)
        if recipe and recipe_matches_filters(recipe):
            save_recipe_json(recipe)
            saved.append(recipe)
        else:
            print("❌ Skipped: Doesn't match filters.")

    if saved:
        save_recipes_csv(saved)
    else:
        print("⚠️ No recipes matched the criteria.")

if __name__ == "__main__":
    main()
