import streamlit as st
import pandas as pd
import numpy as np
import joblib
import ast
import re
import requests
import html


# =====================================
# 1. CONFIGURATION
# =====================================
st.set_page_config(
    page_title="FoodMind",
    page_icon="🍲",
    layout="wide"
)


# =====================================
# THEME FOODMIND : BEIGE CARAMEL
# =====================================
st.markdown("""
<style>
/* Arrière-plan général */
.stApp {
    background-color: #F5EFE6;
    color: #493324;
}

/* Zone principale */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Titres */
h1, h2, h3 {
    color: #704B2B !important;
    font-weight: 700 !important;
}

/* Paragraphes */
p, label, .stMarkdown {
    color: #493324;
}

/* Champs de sélection */
.stMultiSelect [data-baseweb="select"] {
    background-color: #FFF9F1;
    border-radius: 12px;
}

/* Boutons */
.stButton > button {
    background-color: #956B43;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.5rem;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    background-color: #704B2B;
    color: white;
    border: none;
}

/* Curseur */
.stSlider [data-baseweb="slider"] {
    color: #956B43;
}

/* Cartes */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFF9F1;
    border: 1px solid #E8D5BD;
    border-radius: 16px;
    padding: 15px;
}

/* Images */
.stImage img {
    border-radius: 14px;
}

/* Barre de progression */
.stProgress > div > div > div {
    background-color: #956B43;
}

/* Séparateurs */
hr {
    border-color: #D9C2A8;
}
</style>
""", unsafe_allow_html=True)


# =====================================
# 2. CHARGEMENT DU MODELE
# =====================================
@st.cache_resource
def load_model():
    model = joblib.load("models/best_model.pkl")
    vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
    return model, vectorizer


# =====================================
# 3. CHARGEMENT DU DATASET
# =====================================
@st.cache_data
def load_data():
    data = pd.read_csv(
        "Dataset_ProjetIA_food/moroccan_recipes_model_ready.csv"
    )

    def parse_ingredients(value):
        try:
            return ast.literal_eval(value) if isinstance(value, str) else []
        except (ValueError, SyntaxError):
            return []

    data["Ingredients_List"] = data["Ingredients_List"].apply(
        parse_ingredients
    )
    return data


model, vectorizer = load_model()
data = load_data()


# =====================================
# 4. NETTOYAGE DES INGREDIENTS
# =====================================
def clean_ingredient_name(ingredient):
    """Retourne le nom de l'ingrédient sans quantité ni unité."""
    if not isinstance(ingredient, str):
        return None

    ingredient = html.unescape(ingredient)
    ingredient = ingredient.replace("\xa0", " ").lower().strip()
    ingredient = re.sub(r"<[^>]*>", "", ingredient)
    ingredient = re.sub(r"\([^)]*\)", " ", ingredient)
    ingredient = re.sub(r"[\"'“”‘’]", "", ingredient)
    ingredient = re.sub(r"^[\s*•\-–]+", "", ingredient)

    # Quantités avec unité : 15-ounce, 16 oz., 0.5 tsp, 1/2 cup...
    quantity = r"(?:(?:\d+\s+)?\d+(?:\.\d+)?(?:\s*/\s*\d+)?|½|¼|¾)"
    ingredient = re.sub(
        rf"^\s*{quantity}\s*-?\s*(?:ounces?|oz\.?|pounds?|lbs?\.?|grams?|g|kg|ml|cups?|tablespoons?|tbsp|teaspoons?|tsp|liters?|litres?)\s+",
        "", ingredient
    )
    # Quantité seule : 2 avocados, 16 onions
    ingredient = re.sub(rf"^\s*{quantity}\s+", "", ingredient)

    # Conditionnements et unités restantes
    ingredient = re.sub(
        r"^(?:cans?|cartons?|bags?|packages?|pkgs?\.?|boxes?|jars?|bottles?|containers?|cloves?|slices?|bunches?|pinches?)\s+",
        "", ingredient
    )
    ingredient = re.sub(
        r"^(?:ounces?|oz\.?|pounds?|lbs?\.?|grams?|g|kg|ml|cups?|tablespoons?|tbsp|teaspoons?|tsp)\s+",
        "", ingredient
    )

    # Indications de préparation au début et précisions à la fin
    ingredient = re.sub(
        r"^(?:freshly\s+)?(?:finely\s+|roughly\s+)?(?:chopped|diced|minced|mashed|sliced|roasted|grated|crushed|shredded)\s+",
        "", ingredient
    )
    ingredient = re.sub(
        r",?\s*(?:drained|rinsed|divided|for serving|for garnish)\s*$",
        "", ingredient
    )
    ingredient = re.sub(r"\s+", " ", ingredient).strip(" \t\n,;:.-*")

    if not ingredient:
        return None

    invalid_phrases = (
        "can also", "can be added", "added to", "to the vegetables",
        "optional", "for serving", "for garnish", "according to taste", "about",
    )
    if any(phrase in ingredient for phrase in invalid_phrases):
        return None

    invalid_only = {
        "freshly", "roasted", "chopped", "diced", "minced",
        "sliced", "mashed", "grated", "drained", "rinsed",
    }
    if ingredient in invalid_only or len(ingredient.split()) > 6:
        return None

    return ingredient


# =====================================
# 5. GENERATION DE LA LISTE
# =====================================
ingredient_options = set()

for ingredients in data["Ingredients_List"]:
    if isinstance(ingredients, list):
        for ingredient in ingredients:
            name = clean_ingredient_name(ingredient)
            if name and len(name) > 1:
                ingredient_options.add(name)

ingredient_options = sorted(ingredient_options)


# =====================================
# 6. INTERFACE FOODMIND
# =====================================
st.title("🍲 FoodMind")
st.subheader("Votre assistant intelligent de recettes")
st.write(
    "Découvrez des recettes selon les ingrédients "
    "que vous avez disponibles."
)

st.markdown("---")
st.header("🥕 Quels ingrédients avez-vous ?")

selected_ingredients = st.multiselect(
    "Sélectionnez vos ingrédients :",
    options=ingredient_options,
    placeholder="Rechercher un ingrédient...",
)

st.caption(
    f"{len(selected_ingredients)} ingrédient(s) sélectionné(s)"
)

number_recipes = st.slider(
    "Nombre de recettes à afficher",
    min_value=1,
    max_value=10,
    value=5
)


# =====================================
# 7. RECUPERATION DES IMAGES
# =====================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_recipe_image(recipe_name):
    """Cherche une image sur TheMealDB, puis Wikimedia Commons."""
    if not isinstance(recipe_name, str) or not recipe_name.strip():
        return None

    # 1) TheMealDB
    mealdb_url = "https://www.themealdb.com/api/json/v1/1/search.php"
    try:
        response = requests.get(
            mealdb_url, params={"s": recipe_name.strip()}, timeout=8
        )
        response.raise_for_status()
        meals = response.json().get("meals")
        if meals and meals[0].get("strMealThumb"):
            return meals[0]["strMealThumb"]
    except (requests.RequestException, ValueError, TypeError):
        pass

    # 2) Secours : recherche d'image sur Wikimedia Commons
    commons_url = "https://commons.wikimedia.org/w/api.php"
    try:
        response = requests.get(
            commons_url,
            params={
                "action": "query", "generator": "search",
                "gsrsearch": f"{recipe_name.strip()} food",
                "gsrnamespace": 6, "gsrlimit": 5,
                "prop": "imageinfo", "iiprop": "url",
                "iiurlwidth": 700, "format": "json",
            },
            headers={"User-Agent": "FoodMindRecipeApp/1.0"},
            timeout=8,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [])
            if info:
                return info[0].get("thumburl") or info[0].get("url")
    except (requests.RequestException, ValueError, TypeError):
        pass

    return None


# =====================================
# 8. RECHERCHE DES RECETTES
# =====================================
if st.button("🔎 Rechercher des recettes", type="primary"):
    if not selected_ingredients:
        st.warning("Veuillez sélectionner au moins un ingrédient.")
    else:
        panier = selected_ingredients
        results = []

        with st.spinner("Recherche des meilleures recettes..."):
            for _, row in data.iterrows():
                recipe_ingredients = row["Ingredients_List"]

                if not recipe_ingredients:
                    continue

                # Les ingrédients du dataset sont conservés pour le modèle
                texte = (
                    "panier " + " ".join(panier)
                    + " recette " + " ".join(recipe_ingredients)
                )

                X = vectorizer.transform([texte])
                score = model.predict(X)[0]
                score = float(np.clip(score, 0, 1))

                results.append({
                    "Recipe_Name": row["Recipe_Name"],
                    "Description": row["Description"],
                    "Ingredients": recipe_ingredients,
                    "Score": score
                })

        results = sorted(
            results,
            key=lambda x: x["Score"],
            reverse=True
        )

        st.success("Recherche terminée !")
        st.subheader("🍽️ Vos recettes recommandées")

        if not results:
            st.info("Aucune recette contenant des ingrédients exploitables n'a été trouvée.")
        else:
            for recipe in results[:number_recipes]:
                with st.container():
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        image_url = get_recipe_image(recipe["Recipe_Name"])

                        if image_url:
                            st.image(
                                image_url,
                                use_container_width=True
                            )
                        else:
                            st.info("Image non disponible pour ce plat.")

                    with col2:
                        st.subheader(recipe["Recipe_Name"])

                        description = recipe["Description"]
                        if pd.notna(description):
                            st.write(description)
                        else:
                            st.write("Aucune description disponible.")

                        st.write("**Ingrédients nécessaires :**")
                        for ingredient in recipe["Ingredients"]:
                            clean_name = clean_ingredient_name(ingredient)
                            if clean_name:
                                st.write(f"• {clean_name}")

                        st.progress(recipe["Score"])
                        st.write(
                            f"Score prédit : {recipe['Score'] * 100:.1f} %"
                        )

                st.markdown("---")
