from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import difflib

app = Flask(__name__)
CORS(app)

# --- Load recipe data (sample) ---
recipes = [
    {
        "name": "Veg Fried Rice",
        "ingredients": ["rice", "carrot", "peas", "soy sauce", "onion"],
        "instructions": "Cook rice, sauté veggies, add soy sauce, mix well.",
        "calories": 320,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 20
    },
    {
        "name": "Chicken Curry",
        "ingredients": ["chicken", "onion", "tomato", "garam masala", "oil"],
        "instructions": "Cook chicken with spices and onions until tender.",
        "calories": 450,
        "diet": "non-vegetarian",
        "difficulty": "medium",
        "time": 40
    },
    {
        "name": "Fruit Salad",
        "ingredients": ["apple", "banana", "orange", "yogurt", "honey"],
        "instructions": "Chop fruits, mix with yogurt and honey.",
        "calories": 150,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 5
    },
    {
        "name": "Paneer Butter Masala",
        "ingredients": ["paneer", "tomato", "butter", "cream", "spices"],
        "instructions": "Cook paneer cubes in creamy tomato sauce with butter.",
        "calories": 400,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 35
    },
    {
        "name": "Egg Omelette",
        "ingredients": ["egg", "onion", "tomato", "salt", "pepper"],
        "instructions": "Beat eggs with chopped veggies, fry until golden.",
        "calories": 220,
        "diet": "non-vegetarian",
        "difficulty": "easy",
        "time": 10
    },
    {
        "name": "Pasta Alfredo",
        "ingredients": ["pasta", "cream", "cheese", "garlic", "butter"],
        "instructions": "Cook pasta, mix with creamy cheese garlic sauce.",
        "calories": 480,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 25
    },
    {
        "name": "Grilled Chicken Salad",
        "ingredients": ["chicken", "lettuce", "tomato", "cucumber", "olive oil"],
        "instructions": "Grill chicken, toss with veggies and olive oil.",
        "calories": 310,
        "diet": "non-vegetarian",
        "difficulty": "easy",
        "time": 15
    },
    {
        "name": "Mushroom Soup",
        "ingredients": ["mushroom", "cream", "onion", "garlic", "butter"],
        "instructions": "Cook mushrooms and blend with cream and spices.",
        "calories": 200,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 20
    },
    {
        "name": "Vegetable Sandwich",
        "ingredients": ["bread", "tomato", "onion", "cheese", "butter"],
        "instructions": "Assemble veggies and cheese between buttered bread slices.",
        "calories": 260,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 10
    },
    {
        "name": "Chicken Biryani",
        "ingredients": ["chicken", "rice", "onion", "yogurt", "spices"],
        "instructions": "Layer cooked rice with chicken masala and steam.",
        "calories": 520,
        "diet": "non-vegetarian",
        "difficulty": "hard",
        "time": 60
    },
    {
        "name": "Masala Dosa",
        "ingredients": ["rice", "potato", "onion", "chili", "butter"],
        "instructions": "Make crispy dosa and fill with spiced mashed potatoes.",
        "calories": 350,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 30
    },
    {
        "name": "Idli Sambar",
        "ingredients": ["rice", "lentils", "onion", "tomato", "spices"],
        "instructions": "Steam idlis and serve with hot sambar and chutney.",
        "calories": 280,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 40
    },
    {
        "name": "Chole Bhature",
        "ingredients": ["chickpeas", "flour", "onion", "tomato", "spices"],
        "instructions": "Cook chickpeas in gravy, serve with fried bread.",
        "calories": 500,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 50
    },
    {
        "name": "Aloo Paratha",
        "ingredients": ["flour", "potato", "onion", "chili", "butter"],
        "instructions": "Stuff dough with spiced potato, cook on pan with butter.",
        "calories": 420,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 20
    },
    {
        "name": "Rajma Chawal",
        "ingredients": ["kidney beans", "rice", "onion", "tomato", "spices"],
        "instructions": "Cook kidney beans in gravy and serve with rice.",
        "calories": 440,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 45
    },
    {
        "name": "Fish Fry",
        "ingredients": ["fish", "lemon", "chili", "salt", "oil"],
        "instructions": "Marinate fish with spices, shallow fry until crispy.",
        "calories": 380,
        "diet": "non-vegetarian",
        "difficulty": "medium",
        "time": 25
    },
    {
        "name": "Vegetable Pulao",
        "ingredients": ["rice", "peas", "carrot", "onion", "spices"],
        "instructions": "Cook rice with sautéed vegetables and spices.",
        "calories": 330,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 25
    },
    {
        "name": "Dal Tadka",
        "ingredients": ["lentils", "garlic", "onion", "ghee", "spices"],
        "instructions": "Boil lentils and temper with ghee, garlic, and spices.",
        "calories": 280,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 30
    },
    {
        "name": "Butter Chicken",
        "ingredients": ["chicken", "butter", "cream", "tomato", "spices"],
        "instructions": "Cook chicken in buttery tomato gravy with cream.",
        "calories": 480,
        "diet": "non-vegetarian",
        "difficulty": "medium",
        "time": 45
    },
    {
        "name": "Vegetable Pizza",
        "ingredients": ["flour", "tomato", "cheese", "onion", "capsicum"],
        "instructions": "Prepare pizza base, add toppings, bake until golden.",
        "calories": 550,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 35
    },
    {
        "name": "Pancakes",
        "ingredients": ["flour", "milk", "egg", "sugar", "butter"],
        "instructions": "Mix ingredients, pour batter on pan, cook both sides.",
        "calories": 300,
        "diet": "non-vegetarian",
        "difficulty": "easy",
        "time": 15
    },
    {
        "name": "Veg Momos",
        "ingredients": ["flour", "cabbage", "carrot", "onion", "soy sauce"],
        "instructions": "Steam stuffed dumplings with spiced veggies.",
        "calories": 280,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 35
    },
    {
        "name": "Rasgulla",
        "ingredients": ["milk", "sugar", "lemon", "water"],
        "instructions": "Boil milk, make chenna, shape balls, and cook in syrup.",
        "calories": 180,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 50
    },
    {
        "name": "Palak Paneer",
        "ingredients": ["spinach", "paneer", "onion", "garlic", "cream"],
        "instructions": "Cook spinach puree with spices and paneer cubes.",
        "calories": 360,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 30
    },
    {
        "name": "Vegetable Upma",
        "ingredients": ["semolina", "onion", "carrot", "peas", "mustard seeds"],
        "instructions": "Roast semolina, cook with sautéed veggies and spices.",
        "calories": 260,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 20
    },
    {
        "name": "Egg Fried Rice",
        "ingredients": ["rice", "egg", "soy sauce", "onion", "carrot"],
        "instructions": "Scramble eggs, add rice and vegetables, mix with sauce.",
        "calories": 350,
        "diet": "non-vegetarian",
        "difficulty": "easy",
        "time": 20
    },
    {
        "name": "Tomato Soup",
        "ingredients": ["tomato", "onion", "garlic", "butter", "cream"],
        "instructions": "Blend cooked tomatoes and simmer with cream.",
        "calories": 180,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 20
    },
    {
        "name": "Chocolate Cake",
        "ingredients": ["flour", "cocoa", "egg", "sugar", "butter"],
        "instructions": "Mix ingredients, bake at 180°C for 30 minutes.",
        "calories": 400,
        "diet": "non-vegetarian",
        "difficulty": "medium",
        "time": 45
    },
    {
        "name": "Greek Salad",
        "ingredients": ["cucumber", "tomato", "feta cheese", "olive oil", "onion"],
        "instructions": "Mix chopped veggies with olive oil and feta cheese.",
        "calories": 220,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 10
    },
    {
        "name": "Samosa",
        "ingredients": ["flour", "potato", "peas", "spices", "oil"],
        "instructions": "Stuff dough with spiced potato and fry until golden.",
        "calories": 300,
        "diet": "vegetarian",
        "difficulty": "medium",
        "time": 30
    },
    {
        "name": "Oats Porridge",
        "ingredients": ["oats", "milk", "honey", "banana"],
        "instructions": "Cook oats in milk, top with banana and honey.",
        "calories": 250,
        "diet": "vegetarian",
        "difficulty": "easy",
        "time": 10
    }
]


@app.route('/')
def home():
    return "Smart Recipe Generator Backend Running ✅"

# --- Recipe generation route ---
@app.route('/generate', methods=['POST'])
def generate_recipes():
    data = request.json
    user_ingredients = [i.lower() for i in data.get("ingredients", [])]
    diet_pref = data.get("diet", "").lower()

    matches = []
    for recipe in recipes:
        match_score = sum(1 for ingr in recipe["ingredients"]
                          if difflib.get_close_matches(ingr, user_ingredients, n=1, cutoff=0.6))
        if match_score > 0:
            if diet_pref and recipe["diet"] != diet_pref:
                continue
            recipe_copy = recipe.copy()
            recipe_copy["match_score"] = match_score
            matches.append(recipe_copy)

    matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)
    return jsonify(matches if matches else {"message": "No recipes found"})


# --- Substitution suggestions ---
@app.route('/substitute', methods=['POST'])
def substitute():
    subs = {
        "milk": "almond milk",
        "butter": "olive oil",
        "egg": "flaxseed powder",
        "rice": "quinoa"
    }
    data = request.json
    ingr = data.get("ingredient", "").lower()
    suggestion = subs.get(ingr, "No substitution found")
    return jsonify({"substitute": suggestion})

if __name__ == '__main__':
    app.run(debug=True)
