
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import ast
import re

# =====================================
# 1. CONFIGURATION
# =====================================

st.set_page_config(
    page_title="FoodMind",
    page_icon="🍲",
    layout="wide"
)

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

    ingredient = str(ingredient).lower().strip()

    ingredient = re.sub(r"\([^)]*\)", "", ingredient)

    ingredient = ingredient.split(",")[0]

    ingredient = re.sub(
        r"^\s*(?:\d+\s+)?\d+(?:\s*/\s*\d+)?\s*",
        "",
        ingredient
    )

    ingredient = re.sub(
        r"^(cups?|tablespoons?|tbsp|teaspoons?|tsp|"
        r"ounces?|oz|pounds?|lbs?|grams?|g|kg|ml|"
        r"cloves?|cans?|packets?|slices?|bunches?)\s+",
        "",
        ingredient
    )

    ingredient = re.sub(
        r"^(finely chopped|chopped|diced|minced|mashed|sliced)\s+",
        "",
        ingredient
    )

    return ingredient.strip()


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
# 7. RECHERCHE DES RECETTES
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

        st.subheader("🍽️ Recettes recommandées")

        for recipe in results[:number_recipes]:

            st.markdown("---")

            st.subheader(recipe["Recipe_Name"])

            if pd.notna(recipe["Description"]):
                st.write(recipe["Description"])
            else:
                st.write("Aucune description disponible.")

            st.write("**Ingrédients nécessaires :**")

            for ingredient in recipe["Ingredients"]:
                st.write(f"• {ingredient}")

            st.progress(recipe["Score"])

            st.write(
                f"Score prédit : {recipe['Score'] * 100:.1f} %"
            )
