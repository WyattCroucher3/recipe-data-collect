# test_scraper.py
# run with bash - python test_scraper.py

import unittest
from recipe_collector import extract_recipe

class TestRecipeScraping(unittest.TestCase):

    def test_extract_recipe_valid_url(self):
        url = "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/"
        recipe = extract_recipe(url)
        self.assertIsNotNone(recipe)
        self.assertIn("title", recipe)
        self.assertGreater(len(recipe.get("ingredients", [])), 0)
        self.assertGreater(len(recipe.get("instructions", [])), 0)

    def test_extract_recipe_invalid_url(self):
        url = "https://www.allrecipes.com/recipe/notarealrecipe/"
        recipe = extract_recipe(url)
        self.assertIsNone(recipe)

if __name__ == '__main__':
    unittest.main()