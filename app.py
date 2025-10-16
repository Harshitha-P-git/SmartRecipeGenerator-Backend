# app.py
import os
import re
import json
import base64
import difflib
import requests
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# ---------- CONFIG ----------
HF_TOKEN = os.getenv("HF_TOKEN")  # Set this in Render or your env; DO NOT commit token
HF_MODEL = "nlpconnect/vit-gpt2-image-captioning"  # browser-safe model for captioning
USER_FILE = Path("user_data.json")

# Create user file if missing
if not USER_FILE.exists():
    USER_FILE.write_text(json.dumps({"ratings": [], "favorites": []}, indent=2))

# ---------- APP ----------
app = Flask(__name__)
CORS(app)

# ---------- RECIPES (30 items) ----------
# Each recipe includes ingredients (list), instructions, calories, protein (g), diet, difficulty, time (min)
recipes = [
    {"name":"Veg Fried Rice","ingredients":["rice","carrot","peas","soy sauce","onion"],"instructions":"Cook rice, sauté veggies, add soy sauce, mix well.","calories":320,"protein":8,"diet":"vegetarian","difficulty":"medium","time":20},
    {"name":"Chicken Curry","ingredients":["chicken","onion","tomato","garam masala","oil"],"instructions":"Cook chicken with spices and onions until tender.","calories":450,"protein":30,"diet":"non-vegetarian","difficulty":"medium","time":40},
    {"name":"Fruit Salad","ingredients":["apple","banana","orange","yogurt","honey"],"instructions":"Chop fruits, mix with yogurt and honey.","calories":150,"protein":4,"diet":"vegetarian","difficulty":"easy","time":5},
    {"name":"Paneer Butter Masala","ingredients":["paneer","tomato","butter","cream","spices"],"instructions":"Cook paneer cubes in creamy tomato sauce with butter.","calories":400,"protein":18,"diet":"vegetarian","difficulty":"medium","time":35},
    {"name":"Egg Omelette","ingredients":["egg","onion","tomato","salt","pepper"],"instructions":"Beat eggs with chopped veggies, fry until golden.","calories":220,"protein":13,"diet":"non-vegetarian","difficulty":"easy","time":10},
    {"name":"Pasta Alfredo","ingredients":["pasta","cream","cheese","garlic","butter"],"instructions":"Cook pasta, mix with creamy cheese garlic sauce.","calories":480,"protein":12,"diet":"vegetarian","difficulty":"medium","time":25},
    {"name":"Grilled Chicken Salad","ingredients":["chicken","lettuce","tomato","cucumber","olive oil"],"instructions":"Grill chicken, toss with veggies and olive oil.","calories":310,"protein":28,"diet":"non-vegetarian","difficulty":"easy","time":15},
    {"name":"Mushroom Soup","ingredients":["mushroom","cream","onion","garlic","butter"],"instructions":"Cook mushrooms and blend with cream and spices.","calories":200,"protein":6,"diet":"vegetarian","difficulty":"easy","time":20},
    {"name":"Vegetable Sandwich","ingredients":["bread","tomato","onion","cheese","butter"],"instructions":"Assemble veggies and cheese between buttered bread slices.","calories":260,"protein":10,"diet":"vegetarian","difficulty":"easy","time":10},
    {"name":"Chicken Biryani","ingredients":["chicken","rice","onion","yogurt","spices"],"instructions":"Layer cooked rice with chicken masala and steam.","calories":520,"protein":35,"diet":"non-vegetarian","difficulty":"hard","time":60},
    {"name":"Masala Dosa","ingredients":["rice","potato","onion","chili","butter"],"instructions":"Make crispy dosa and fill with spiced mashed potatoes.","calories":350,"protein":6,"diet":"vegetarian","difficulty":"medium","time":30},
    {"name":"Idli Sambar","ingredients":["rice","lentils","onion","tomato","spices"],"instructions":"Steam idlis and serve with hot sambar and chutney.","calories":280,"protein":9,"diet":"vegetarian","difficulty":"medium","time":40},
    {"name":"Chole Bhature","ingredients":["chickpeas","flour","onion","tomato","spices"],"instructions":"Cook chickpeas in gravy, serve with fried bread.","calories":500,"protein":14,"diet":"vegetarian","difficulty":"medium","time":50},
    {"name":"Aloo Paratha","ingredients":["flour","potato","onion","chili","butter"],"instructions":"Stuff dough with spiced potato, cook on pan with butter.","calories":420,"protein":7,"diet":"vegetarian","difficulty":"easy","time":20},
    {"name":"Rajma Chawal","ingredients":["kidney beans","rice","onion","tomato","spices"],"instructions":"Cook kidney beans in gravy and serve with rice.","calories":440,"protein":15,"diet":"vegetarian","difficulty":"medium","time":45},
    {"name":"Fish Fry","ingredients":["fish","lemon","chili","salt","oil"],"instructions":"Marinate fish with spices, shallow fry until crispy.","calories":380,"protein":30,"diet":"non-vegetarian","difficulty":"medium","time":25},
    {"name":"Vegetable Pulao","ingredients":["rice","peas","carrot","onion","spices"],"instructions":"Cook rice with sautéed vegetables and spices.","calories":330,"protein":7,"diet":"vegetarian","difficulty":"easy","time":25},
    {"name":"Dal Tadka","ingredients":["lentils","garlic","onion","ghee","spices"],"instructions":"Boil lentils and temper with ghee, garlic, and spices.","calories":280,"protein":12,"diet":"vegetarian","difficulty":"easy","time":30},
    {"name":"Butter Chicken","ingredients":["chicken","butter","cream","tomato","spices"],"instructions":"Cook chicken in buttery tomato gravy with cream.","calories":480,"protein":33,"diet":"non-vegetarian","difficulty":"medium","time":45},
    {"name":"Vegetable Pizza","ingredients":["flour","tomato","cheese","onion","capsicum"],"instructions":"Prepare pizza base, add toppings, bake until golden.","calories":550,"protein":14,"diet":"vegetarian","difficulty":"medium","time":35},
    {"name":"Pancakes","ingredients":["flour","milk","egg","sugar","butter"],"instructions":"Mix ingredients, pour batter on pan, cook both sides.","calories":300,"protein":8,"diet":"non-vegetarian","difficulty":"easy","time":15},
    {"name":"Veg Momos","ingredients":["flour","cabbage","carrot","onion","soy sauce"],"instructions":"Steam stuffed dumplings with spiced veggies.","calories":280,"protein":6,"diet":"vegetarian","difficulty":"medium","time":35},
    {"name":"Rasgulla","ingredients":["milk","sugar","lemon","water"],"instructions":"Boil milk, make chenna, shape balls, and cook in syrup.","calories":180,"protein":6,"diet":"vegetarian","difficulty":"medium","time":50},
    {"name":"Palak Paneer","ingredients":["spinach","paneer","onion","garlic","cream"],"instructions":"Cook spinach puree with spices and paneer cubes.","calories":360,"protein":16,"diet":"vegetarian","difficulty":"medium","time":30},
    {"name":"Vegetable Upma","ingredients":["semolina","onion","carrot","peas","mustard seeds"],"instructions":"Roast semolina, cook with sautéed veggies and spices.","calories":260,"protein":6,"diet":"vegetarian","difficulty":"easy","time":20},
    {"name":"Egg Fried Rice","ingredients":["rice","egg","soy sauce","onion","carrot"],"instructions":"Scramble eggs, add rice and vegetables, mix with sauce.","calories":350,"protein":14,"diet":"non-vegetarian","difficulty":"easy","time":20},
    {"name":"Tomato Soup","ingredients":["tomato","onion","garlic","butter","cream"],"instructions":"Blend cooked tomatoes and simmer with cream.","calories":180,"protein":3,"diet":"vegetarian","difficulty":"easy","time":20},
    {"name":"Chocolate Cake","ingredients":["flour","cocoa","egg","sugar","butter"],"instructions":"Mix ingredients, bake at 180°C for 30 minutes.","calories":400,"protein":6,"diet":"non-vegetarian","difficulty":"medium","time":45},
    {"name":"Greek Salad","ingredients":["cucumber","tomato","feta cheese","olive oil","onion"],"instructions":"Mix chopped veggies with olive oil and feta cheese.","calories":220,"protein":8,"diet":"vegetarian","difficulty":"easy","time":10},
    {"name":"Samosa","ingredients":["flour","potato","peas","spices","oil"],"instructions":"Stuff dough with spiced potato and fry until golden.","calories":300,"protein":5,"diet":"vegetarian","difficulty":"medium","time":30},
    {"name":"Oats Porridge","ingredients":["oats","milk","honey","banana"],"instructions":"Cook oats in milk, top with banana and honey.","calories":250,"protein":7,"diet":"vegetarian","difficulty":"easy","time":10}
]

# Normalize ingredients to lists (if any recipe had a string)
for r in recipes:
    if isinstance(r.get("ingredients"), str):
        r["ingredients"] = [i.strip() for i in r["ingredients"].split(",")]

# ---------- UTILS ----------
def read_user_data():
    return json.loads(USER_FILE.read_text())

def write_user_data(obj):
    USER_FILE.write_text(json.dumps(obj, indent=2))

COMMON_INGREDIENTS = set([
    "tomato","carrot","onion","rice","apple","banana","chicken","milk","cheese",
    "bread","egg","potato","peas","paneer","spinach","garlic","ginger","mushroom",
    "cucumber","lettuce","pepper","corn","beans","yogurt","butter","cream","pasta",
    "flour","sugar","honey","lentils","kidney beans","fish","tofu","quinoa"
])

# ---------- ROUTES ----------
@app.route("/")
def home():
    return "Smart Recipe Generator Backend Running ✅"

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json() or {}
        user_ingredients = [i.lower() for i in data.get("ingredients", []) if i]
        diet_pref = (data.get("diet") or "").lower()
        difficulty = (data.get("difficulty") or "").lower()
        max_time = data.get("max_time")
        servings = int(data.get("servings", 1))

        if not user_ingredients:
            return jsonify({"error": "No ingredients provided"}), 400

        matches = []
        for recipe in recipes:
            rec_ing = [ing.lower() for ing in recipe.get("ingredients", [])]
            # match score: number of ingredients present (fuzzy match by close_matches)
            match_score = 0
            for ingr in rec_ing:
                if difflib.get_close_matches(ingr, user_ingredients, n=1, cutoff=0.6):
                    match_score += 1
            if match_score == 0:
                continue
            # filters
            if diet_pref and recipe.get("diet","").lower() != diet_pref:
                continue
            if difficulty and recipe.get("difficulty","").lower() != difficulty:
                continue
            if max_time:
                try:
                    if int(recipe.get("time",0)) > int(max_time):
                        continue
                except:
                    pass
            # prepare output
            rcopy = recipe.copy()
            rcopy["match_score"] = match_score
            rcopy["servings"] = servings
            # naive calorie scaling by servings
            rcopy["calories_adjusted"] = int(rcopy.get("calories",0) * servings)
            matches.append(rcopy)

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return jsonify(matches)

    except Exception as e:
        return jsonify({"error":"server error", "detail": str(e)}), 500

@app.route("/substitute", methods=["POST"])
def substitute():
    try:
        subs = {
            "milk": ["almond milk", "soya milk"],
            "butter": ["olive oil", "coconut oil"],
            "egg": ["flaxseed powder (1 tbsp) + water (3 tbsp)"],
            "rice": ["quinoa", "couscous"],
            "paneer": ["tofu"],
            "sugar": ["honey", "maple syrup"],
            "cheese": ["nutritional yeast (in some recipes)"]
        }
        data = request.get_json() or {}
        ingr = (data.get("ingredient") or "").lower()
        if not ingr:
            return jsonify({"error":"no ingredient provided"}), 400
        suggestions = subs.get(ingr, [])
        return jsonify({"ingredient": ingr, "substitutions": suggestions})
    except Exception as e:
        return jsonify({"error":"server error","detail":str(e)}), 500

@app.route("/save", methods=["POST"])
def save_recipe():
    try:
        payload = request.get_json() or {}
        email = payload.get("email", "anonymous")
        recipe_name = payload.get("recipe", "")
        if not recipe_name:
            return jsonify({"error":"No recipe provided"}), 400
        data = read_user_data()
        data["favorites"].append({"email": email, "recipe": recipe_name})
        write_user_data(data)
        return jsonify({"message":"Saved"})
    except Exception as e:
        return jsonify({"error":"server error","detail":str(e)}), 500

@app.route("/rate", methods=["POST"])
def rate_recipe():
    try:
        payload = request.get_json() or {}
        email = payload.get("email", "anonymous")
        recipe_name = payload.get("recipe", "")
        rating = int(payload.get("rating", 0))
        if not recipe_name or rating < 1 or rating > 5:
            return jsonify({"error":"Invalid rating or recipe"}), 400
        data = read_user_data()
        data["ratings"].append({"email": email, "recipe": recipe_name, "rating": rating})
        write_user_data(data)
        return jsonify({"message":"Rating saved"})
    except Exception as e:
        return jsonify({"error":"server error","detail":str(e)}), 500

@app.route("/suggestions", methods=["GET"])
def suggestions():
    try:
        email = request.args.get("email", "anonymous")
        data = read_user_data()
        rated = [r for r in data.get("ratings", []) if r.get("email")==email and r.get("rating",0) >= 4]
        high_names = set(r["recipe"] for r in rated)
        high_ings = set()
        for rec in recipes:
            if rec["name"] in high_names:
                for ing in rec.get("ingredients", []):
                    high_ings.add(ing.lower())
        suggestions = []
        for rec in recipes:
            if rec["name"] in high_names:
                continue
            rec_ings = set(i.lower() for i in rec.get("ingredients", []))
            if rec_ings & high_ings:
                suggestions.append(rec)
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error":"server error","detail":str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze_image():
    """
    Accept multipart/form-data with file field 'file'.
    Uses Hugging Face inference API. Requires HF_TOKEN environment variable.
    Returns: {"caption": "...", "ingredients": [...] } or error
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error":"No file provided"}), 400
        if not HF_TOKEN:
            return jsonify({"error":"HF_TOKEN not configured on server"}), 500

        file = request.files['file']
        img_bytes = file.read()
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        payload = {"inputs": b64, "options": {"wait_for_model": True}}
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}

        resp = requests.post(f"https://api-inference.huggingface.co/models/{HF_MODEL}", headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            return jsonify({"error":"model error","detail":resp.text}), 502

        data = resp.json()
        # data often is list with generated_text
        caption = ""
        if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("generated_text"):
            caption = data[0]["generated_text"]
        elif isinstance(data, dict) and data.get("generated_text"):
            caption = data.get("generated_text")
        else:
            # sometimes the model returns plain structure
            caption = str(data)

        # extract ingredients using COMMON_INGREDIENTS set
        words = re.findall(r'\b[a-zA-Z]+\b', caption.lower())
        matches = []
        seen = set()
        for w in words:
            if w in COMMON_INGREDIENTS and w not in seen:
                seen.add(w)
                matches.append(w)

        return jsonify({"caption": caption, "ingredients": matches})
    except requests.exceptions.ReadTimeout:
        return jsonify({"error":"Model timeout, try again later"}), 504
    except Exception as e:
        return jsonify({"error":"server error","detail":str(e)}), 500

# ---------- RUN ----------
if __name__ == "__main__":
    # For local testing only; Render uses gunicorn
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
