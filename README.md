# recipe-data-collect
A tool used to collect recipes from publicly available data websites and parse the information into a JSON and/or CSV file..

# Goal - Create a program that scrapes a recipe webpage to collect:
Recipe title
Ingredients and their amounts
Steps/instructions
Nutrition facts (if available)

# getting started
Python
requests – to fetch the webpage (pip install requests)
BeautifulSoup (from bs4) – for HTML parsing
json – to parse structured data like JSON-LD, common in recipe pages
Optional: re for regular expressions (if needed)

# Building a GUI App Using PyQt5
Step 1 - Environment Setup
    pip install pyqt5 beautifulsoup4 requests
Step 2 - App Folder Structure
    recipe_app/
    ├── main.py
    ├── recipe_manager.py
    ├── recipe_collector.py
    ├── data/
    │   ├── recipes/
    │   ├── images/
    │   └── recipes_summary.csv
Step 3 - Core Modules Overview
    recipe_collector.py: (Handles searching, scraping, filtering, downloading)
        Scrape recipes
        Download images
        Save to JSON & CSV
    recipe_manager.py: (Handles loading/saving/editing)
        Load JSON recipes
        Edit & update recipes
        Handle image associations
    main.py: (GUI app using PyQt5)
        GUI for viewing/editing/searching recipes
        Two modes: "View Recipes" and "Collect Recipes"