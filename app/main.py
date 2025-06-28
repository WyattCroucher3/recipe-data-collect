# main.py
# run with bash - python main.py


import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QListWidget, QLineEdit,
    QFormLayout, QMessageBox, QSpinBox, QPlainTextEdit
)
from PyQt5.QtGui import QPixmap
from recipe_collector import collect_recipes 
from recipe_manager import load_recipes, save_recipe_to_file, export_all_to_csv 


class RecipeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recipe Collector & Viewer")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.view_tab = QWidget()
        self.collect_tab = QWidget()

        self.init_view_tab()
        self.init_collect_tab()

        self.tabs.addTab(self.view_tab, "📖 View Recipes")
        self.tabs.addTab(self.collect_tab, "📡 Collect Recipes")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def init_view_tab(self):
        layout = QHBoxLayout()

        self.recipe_list = QListWidget()
        self.recipe_list.itemClicked.connect(self.load_selected_recipe)

        self.image_label = QLabel("Image Preview")
        self.image_label.setFixedWidth(250)
        self.image_label.setScaledContents(True)

        # Editable fields
        self.edit_title = QLineEdit()
        self.edit_ingredients = QPlainTextEdit()
        self.edit_instructions = QPlainTextEdit()
        self.edit_nutrition = QPlainTextEdit()
        self.save_edit_btn = QPushButton("💾 Save Changes")
        self.save_edit_btn.clicked.connect(self.save_edited_recipe)

        self.export_csv_btn = QPushButton("📄 Export All to CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Saved Recipes"))
        left_layout.addWidget(self.recipe_list)
        left_layout.addWidget(self.export_csv_btn)

        form_layout = QFormLayout()
        form_layout.addRow("Title:", self.edit_title)
        form_layout.addRow("Ingredients:", self.edit_ingredients)
        form_layout.addRow("Instructions:", self.edit_instructions)
        form_layout.addRow("Nutrition (JSON):", self.edit_nutrition)
        form_layout.addWidget(self.save_edit_btn)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.image_label)
        right_layout.addLayout(form_layout)

        layout.addLayout(left_layout, 3)
        layout.addLayout(right_layout, 5)

        self.view_tab.setLayout(layout)

        self.load_all_recipes()

    def load_all_recipes(self):
        self.recipes = load_recipes()
        self.recipe_list.clear()
        for recipe in self.recipes:
            self.recipe_list.addItem(recipe['title'])

    def load_selected_recipe(self, item):
        title = item.text()
        for recipe in self.recipes:
            if recipe['title'] == title:
                self.selected_recipe = recipe
                self.edit_title.setText(recipe['title'])
                self.edit_ingredients.setPlainText("\n".join(recipe['ingredients']))
                self.edit_instructions.setPlainText("\n".join(recipe['instructions']))
                nutrition = recipe.get("nutrition", {})
                self.edit_nutrition.setPlainText(json.dumps(nutrition, indent=2))

                if 'image_path' in recipe:
                    pixmap = QPixmap(recipe['image_path'])
                    self.image_label.setPixmap(pixmap)
                else:
                    self.image_label.setPixmap(QPixmap())
                break

    def save_edited_recipe(self):
        if not hasattr(self, 'selected_recipe'):
            return

        self.selected_recipe['title'] = self.edit_title.text()
        self.selected_recipe['ingredients'] = self.edit_ingredients.toPlainText().splitlines()
        self.selected_recipe['instructions'] = self.edit_instructions.toPlainText().splitlines()

        try:
            nutrition_data = json.loads(self.edit_nutrition.toPlainText())
            self.selected_recipe['nutrition'] = nutrition_data
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Invalid nutrition JSON: {e}")
            return

        save_recipe_to_file(self.selected_recipe)

        QMessageBox.information(self, "Saved", "Recipe updated.")
        self.load_all_recipes()

    def export_csv(self):
        export_all_to_csv(self.recipes)
        QMessageBox.information(self, "Exported", "CSV updated.")

    def init_collect_tab(self):
        layout = QVBoxLayout()

        form = QFormLayout()
        self.search_input = QLineEdit()
        self.num_input = QSpinBox()
        self.num_input.setRange(1, 50)
        self.num_input.setValue(5)

        self.exclude_input = QLineEdit()
        self.protein_min = QSpinBox()
        self.protein_min.setRange(0, 100)
        self.fat_max = QSpinBox()
        self.fat_max.setRange(0, 100)
        self.carbs_max = QSpinBox()
        self.carbs_max.setRange(0, 100)

        form.addRow("Search Term:", self.search_input)
        form.addRow("Number of Recipes:", self.num_input)
        form.addRow("Exclude Ingredients (comma):", self.exclude_input)
        form.addRow("Min Protein (g):", self.protein_min)
        form.addRow("Max Fat (g):", self.fat_max)
        form.addRow("Max Carbs (g):", self.carbs_max)

        self.collect_btn = QPushButton("Collect Recipes")
        self.collect_btn.clicked.connect(self.run_collection)

        layout.addLayout(form)
        layout.addWidget(self.collect_btn)
        self.collect_tab.setLayout(layout)

    def run_collection(self):
        search = self.search_input.text()
        num = self.num_input.value()
        excludes = [x.strip().lower() for x in self.exclude_input.text().split(",") if x.strip()]
        filters = {
            "proteinContent": lambda x: x >= self.protein_min.value(),
            "fatContent": lambda x: x <= self.fat_max.value(),
            "carbohydrateContent": lambda x: x <= self.carbs_max.value(),
        }

        collected = collect_recipes(search, num, excludes, filters)
        QMessageBox.information(self, "Done", f"Collected {len(collected)} recipes.")
        self.load_all_recipes()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecipeApp()
    window.show()
    sys.exit(app.exec_())