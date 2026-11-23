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
    if not isinstance(ingredient, str):
        return None

    # Décoder HTML et nettoyer les espaces
    ingredient = html.unescape(ingredient)
    ingredient = ingredient.replace("\xa0", " ").lower().strip()

    # Supprimer les balises HTML, le contenu entre parenthèses
    # et les caractères décoratifs au début
    ingredient = re.sub(r"<[^>]*>", "", ingredient)
    ingredient = re.sub(r"\([^)]*\)", "", ingredient)
    ingredient = re.sub(r"^[\s*•\-–]+", "", ingredient)

    # Supprimer les guillemets
    ingredient = re.sub(r"[\"'“”‘’]", "", ingredient)

    # Supprimer les quantités : 1/2, 0.5, 1 1/2, etc.
    ingredient = re.sub(
        r"^\s*(?:(?:\d+\s+)?\d+\s*/\s*\d+|\d+(?:\.\d+)?|½|¼|¾)\s*",
        "",
        ingredient
    )

    # Supprimer les unités de mesure
    ingredient = re.sub(
        r"^(cups?|tablespoons?|tbsp|teaspoons?|tsp|"
        r"ounces?|oz|pounds?|lbs?|grams?|g|kg|ml|"
        r"liters?|pints?|quarts?|cloves?|cans?|packets?|"
        r"slices?|bunches?|pinches?)\s+",
        "",
        ingredient
    )

    # Supprimer les indications de préparation au début
    ingredient = re.sub(
        r"^(freshly roasted|freshly grated|finely chopped|"
        r"roughly chopped|chopped|diced|minced|mashed|"
        r"sliced|roasted|grated)\s+",
        "",
        ingredient
    )

    ingredient = re.sub(r"\s+", " ", ingredient)
    ingredient = ingredient.strip(" \t\n,;:.-*")

    if not ingredient:
        return None

    # Rejeter les phrases et commentaires
    invalid_phrases = [
        "can also", "can be added", "added to",
        "to the vegetables", "optional", "for serving",
        "for garnish", "according to taste", "about"
    ]
    if any(phrase in ingredient for phrase in invalid_phrases):
        return None

    # Rejeter les fragments qui ne sont pas des ingrédients
    invalid_only = {
        "freshly", "roasted", "chopped", "diced",
        "minced", "sliced", "mashed", "grated"
    }
    if ingredient in invalid_only:
        return None

    # Éviter les descriptions trop longues
    if len(ingredient.split()) > 5:
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
@st.cache_data

def get_recipe_image(recipe_name):
    url = "https://www.themealdb.com/api/json/v1/1/search.php"

    try:
        response = requests.get(
            url,
            params={"s": recipe_name},
            timeout=10
        )
        response.raise_for_status()

        image_data = response.json()
        meals = image_data.get("meals")

        if meals:
            return meals[0].get("strMealThumb")

    except (requests.RequestException, ValueError):
        return None

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
