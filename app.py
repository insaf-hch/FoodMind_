
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import ast

# Configuration de la page
st.set_page_config(
    page_title="FoodMind",
    page_icon="🍲",
    layout="wide"
)

# Chargement du modèle
@st.cache_resource
def load_model():
    model = joblib.load("Models/best_model.pkl")
    vectorizer = joblib.load("Models/tfidf_vectorizer.pkl")
    return model, vectorizer

# Chargement du dataset
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

# Interface
st.title("🍲 FoodMind")
st.subheader("Votre assistant intelligent de recettes")

st.write(
    "Découvrez des recettes selon les ingrédients "
    "que vous avez disponibles."
)

# Saisie des ingrédients
ingredients_input = st.text_input(
    "Quels ingrédients avez-vous ?",
    placeholder="Exemple : chicken, onion, garlic, olive oil"
)

# Nombre de recettes
number_recipes = st.slider(
    "Nombre de recettes à afficher",
    min_value=1,
    max_value=10,
    value=5
)

# Recherche des recettes
if st.button("Rechercher des recettes"):

    if not ingredients_input.strip():
        st.warning("Veuillez saisir au moins un ingrédient.")

    else:
        panier = [
            item.strip().lower()
            for item in ingredients_input.split(",")
            if item.strip()
        ]

        results = []

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

        for recipe in results[:number_recipes]:

            st.markdown("---")

            st.subheader(recipe["Recipe_Name"])

            st.write(recipe["Description"])

            st.write(
                "**Ingrédients nécessaires :**",
                ", ".join(recipe["Ingredients"])
            )

            st.progress(recipe["Score"])

            st.write(
                f"Score prédit : {recipe['Score'] * 100:.1f} %"
            )
