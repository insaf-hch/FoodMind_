import streamlit as st
import pandas as pd
import numpy as np
import joblib
import ast
import re
import html
import requests
from concurrent.futures import ThreadPoolExecutor


# =====================================
# 1. CONFIGURATION
# =====================================
st.set_page_config(page_title="FoodMind", page_icon="🍲", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=Figtree:wght@400;500;600&display=swap');

:root {
    --bg: #F7F6F2;
    --surface: #FFFFFF;
    --ink: #17302F;
    --muted: #5E7170;
    --line: #E3E8E5;
    --green: #0F4C4A;
    --green-dark: #0A3534;
    --saffron: #F0A82B;
    --mint: #DCEFE8;
}

html, body, .stApp, [class*="css"] {
    font-family: 'Figtree', sans-serif;
    color: var(--ink);
}
.stApp { background: var(--bg); }

/* Masquer l'interface Streamlit par défaut */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { max-width: 1100px; padding-top: 1.5rem; padding-bottom: 4rem; }

/* ---------- Hero ---------- */
.fm-hero {
    background: var(--green);
    border-radius: 28px;
    padding: 3rem 3rem 2.6rem 3rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.fm-hero::after {
    content: "";
    position: absolute; right: -60px; top: -60px;
    width: 260px; height: 260px; border-radius: 50%;
    border: 38px solid var(--saffron);
    opacity: .9;
}
.fm-hero h1 {
    font-family: 'Bricolage Grotesque', sans-serif;
    color: #fff !important;
    font-size: 3.4rem; font-weight: 800 !important;
    letter-spacing: -0.02em; margin: 0 0 .5rem 0; padding: 0;
}
.fm-hero p {
    color: #CFE3DD; font-size: 1.15rem; max-width: 520px;
    margin: 0; line-height: 1.55;
}

/* ---------- Titres ---------- */
h2, h3 {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    color: var(--ink) !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em;
}

/* ---------- Panneau de contrôle ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border: 1px solid var(--line) !important;
    border-radius: 22px;
    padding: 1.2rem 1.4rem;
}
.stMultiSelect [data-baseweb="select"] > div {
    background: var(--bg);
    border: 1px solid var(--line);
    border-radius: 14px;
    min-height: 52px;
}
.stMultiSelect [data-baseweb="select"] > div:focus-within {
    border-color: var(--green);
    box-shadow: 0 0 0 3px rgba(15, 76, 74, .15);
}
span[data-baseweb="tag"] {
    background: var(--green) !important;
    color: #fff !important;
    border-radius: 999px !important;
    padding: 2px 10px !important;
}
span[data-baseweb="tag"] span { color: #fff !important; }

/* Curseur */
div[data-baseweb="slider"] [role="slider"] { background: var(--green) !important; }
div[data-testid="stSliderThumbValue"] { color: var(--green) !important; }

/* Bouton */
.stButton > button {
    background: var(--saffron);
    color: var(--ink);
    border: none;
    border-radius: 14px;
    padding: .8rem 2rem;
    font-weight: 700;
    font-size: 1.02rem;
    transition: transform .15s, background .15s;
}
.stButton > button:hover {
    background: #E39A18; color: var(--ink); border: none;
    transform: translateY(-1px);
}
.stButton > button:focus-visible { outline: 3px solid var(--green); }

/* ---------- Cartes recette ---------- */
.fm-card {
    display: flex; gap: 0;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 24px;
    overflow: hidden;
    margin-bottom: 1.4rem;
}
.fm-img {
    flex: 0 0 300px; min-height: 260px;
    background: var(--mint);
    display: flex; align-items: center; justify-content: center;
    font-size: 4rem;
}
.fm-img img {
    width: 100%; height: 100%; object-fit: cover; display: block;
}
.fm-body { flex: 1; padding: 1.5rem 1.8rem; min-width: 0; }
.fm-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.fm-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.5rem; font-weight: 700; line-height: 1.2;
    margin: 0; color: var(--ink);
}
.fm-score {
    flex: 0 0 auto; text-align: center;
    background: var(--green); color: #fff;
    border-radius: 16px; padding: .45rem .9rem;
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700; font-size: 1.25rem; line-height: 1.1;
}
.fm-score small { display: block; font-family: 'Figtree', sans-serif; font-weight: 500; font-size: .7rem; color: #BCD8D0; }
.fm-desc {
    color: var(--muted); margin: .7rem 0 1rem 0; line-height: 1.55;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.fm-bar { height: 6px; background: var(--line); border-radius: 99px; margin-bottom: 1rem; overflow: hidden; }
.fm-bar span { display: block; height: 100%; background: var(--saffron); border-radius: 99px; }
.fm-label { font-weight: 600; font-size: .92rem; margin-bottom: .5rem; color: var(--ink); }
.fm-chips { display: flex; flex-wrap: wrap; gap: .4rem; }
.fm-chip {
    background: var(--bg); border: 1px solid var(--line);
    color: var(--muted); font-size: .84rem;
    padding: .22rem .7rem; border-radius: 999px;
}
.fm-chip.hit { background: var(--mint); border-color: #A9D5C7; color: var(--green-dark); font-weight: 600; }

@media (max-width: 760px) {
    .fm-hero { padding: 2rem 1.5rem; }
    .fm-hero h1 { font-size: 2.5rem; }
    .fm-card { flex-direction: column; }
    .fm-img { flex-basis: 200px; min-height: 200px; }
}
@media (prefers-reduced-motion: reduce) { .stButton > button { transition: none; } }
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
    data = pd.read_csv("Dataset_ProjetIA_food/moroccan_recipes_model_ready.csv")

    def parse_ingredients(value):
        try:
            return ast.literal_eval(value) if isinstance(value, str) else []
        except (ValueError, SyntaxError):
            return []

    data["Ingredients_List"] = data["Ingredients_List"].apply(parse_ingredients)
    return data


model, vectorizer = load_model()
data = load_data()


# =====================================
# 4. NETTOYAGE DES INGREDIENTS (liste de recherche uniquement)
# =====================================
_QTY = r"(?:\d+\s+\d+\s*/\s*\d+|\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?|[½¼¾⅓⅔])(?:\s*(?:-|–|to)\s*\d+(?:[.,]\d+)?)?"
_UNIT = (r"(?:ounces?|oz|pounds?|lbs?|grams?|gr|g|kg|ml|cl|l|cups?|tablespoons?|tbsps?|"
         r"teaspoons?|tsps?|liters?|litres?|quarts?|pints?)")
_CONTAINER = (r"(?:cans?|cartons?|bags?|packages?|packets?|pkgs?|boxes?|jars?|bottles?|"
              r"containers?|tins?|cloves?|slices?|bunch(?:es)?|pinch(?:es)?|sprigs?|"
              r"heads?|stalks?|handfuls?|dashes?|sticks?)")
_WORDS = (r"(?:large|medium|small|big|whole|prepared|fresh|freshly|dried|canned|frozen|"
          r"ripe|raw|cooked|chopped|diced|minced|mashed|sliced|roasted|grated|crushed|"
          r"shredded|finely|roughly|thinly|peeled|pitted|packed|heaping|level)")

_LEADING = re.compile(
    rf"^\s*(?:{_QTY}\s*-?\s*)?"
    rf"(?:{_UNIT}\b\.?\s*-?\s*)?"
    rf"(?:{_CONTAINER}\b\.?\s+(?=\S))?"
    rf"(?:of\s+)?"
    rf"(?:{_WORDS}\b\s+(?=\S))*"
)


def clean_ingredient_name(ingredient):
    """Retourne uniquement le nom de l'ingrédient (sans quantité, unité,
    conditionnement ni précision de préparation)."""
    if not isinstance(ingredient, str):
        return None

    text = html.unescape(ingredient).replace("\xa0", " ").lower().strip()
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[\"'“”‘’]", "", text)
    text = re.sub(r"^[\s*•\-–]+", "", text)

    # Tout ce qui suit la première virgule est une précision (drained, to taste...)
    text = text.split(",")[0]
    # "butter or margarine" -> "butter"
    text = re.split(r"\s+(?:or|plus)\s+", text)[0]

    # On retire plusieurs fois le début (quantité, unité, boîte, adjectifs)
    for _ in range(4):
        new = _LEADING.sub("", text).strip()
        if new == text:
            break
        text = new

    # Fins de phrase inutiles
    text = re.sub(r"\s+(?:to taste|for serving|for garnish|as needed|divided|drained|rinsed)$", "", text)
    text = re.sub(r"\s+", " ", text).strip(" \t\n,;:.-*")

    if not text or len(text) < 2 or re.search(r"\d", text):
        return None

    invalid_phrases = (
        "can also", "can be added", "added to", "to the vegetables",
        "optional", "according to taste", "about",
    )
    if any(p in text for p in invalid_phrases) or len(text.split()) > 5:
        return None

    return text


def display_ingredient(ingredient):
    """Ingrédient complet (avec quantité) pour l'affichage dans la carte."""
    if not isinstance(ingredient, str):
        return ""
    text = html.unescape(ingredient).replace("\xa0", " ")
    text = re.sub(r"<[^>]*>", "", text)
    return re.sub(r"\s+", " ", text).strip(" \t\n,;:.-*•")


# =====================================
# 5. GENERATION DE LA LISTE DE RECHERCHE
# =====================================
@st.cache_data
def build_options(_data):
    names = set()
    for ingredients in _data["Ingredients_List"]:
        if isinstance(ingredients, list):
            for ing in ingredients:
                name = clean_ingredient_name(ing)
                if name:
                    names.add(name)
    return sorted(names)


ingredient_options = build_options(data)


# =====================================
# 6. RECUPERATION DES IMAGES
# =====================================
HEADERS = {"User-Agent": "FoodMindRecipeApp/1.0 (student project)"}


def _search_queries(recipe_name):
    """Variantes de recherche : nom complet, puis versions simplifiées."""
    name = re.sub(r"\([^)]*\)", " ", recipe_name)
    name = re.sub(r"\b(easy|best|simple|quick|homemade|authentic|traditional|recipe)\b", " ", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip(" -,")
    short = re.split(r"\s+(?:with|and|&)\s+|,|\s-\s", name, flags=re.I)[0].strip()
    words = name.split()
    variants = [name, short]
    if len(words) > 2:
        variants += [" ".join(words[-2:]), " ".join(words[:2])]
    seen, result = set(), []
    for v in variants:
        if v and v.lower() not in seen:
            seen.add(v.lower())
            result.append(v)
    return result


def _mealdb(query):
    try:
        r = requests.get("https://www.themealdb.com/api/json/v1/1/search.php",
                         params={"s": query}, timeout=6)
        r.raise_for_status()
        meals = r.json().get("meals")
        if meals and meals[0].get("strMealThumb"):
            return meals[0]["strMealThumb"]
    except (requests.RequestException, ValueError, TypeError):
        pass
    return None


def _wikipedia(query):
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "generator": "search", "gsrsearch": query,
                    "gsrlimit": 3, "prop": "pageimages", "piprop": "thumbnail",
                    "pithumbsize": 700, "format": "json"},
            headers=HEADERS, timeout=6)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in sorted(pages.values(), key=lambda p: p.get("index", 99)):
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except (requests.RequestException, ValueError, TypeError):
        pass
    return None


def _commons(query):
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={"action": "query", "generator": "search",
                    "gsrsearch": f"{query} food", "gsrnamespace": 6, "gsrlimit": 5,
                    "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 700, "format": "json"},
            headers=HEADERS, timeout=6)
        r.raise_for_status()
        for page in r.json().get("query", {}).get("pages", {}).values():
            info = page.get("imageinfo", [])
            if info:
                return info[0].get("thumburl") or info[0].get("url")
    except (requests.RequestException, ValueError, TypeError):
        pass
    return None


def fetch_image(recipe_name):
    """Essaie plusieurs sources et plusieurs formulations du nom du plat."""
    if not isinstance(recipe_name, str) or not recipe_name.strip():
        return None
    queries = _search_queries(recipe_name)
    for q in queries:
        url = _mealdb(q)
        if url:
            return url
    for q in queries[:2]:
        url = _wikipedia(f"{q} dish")
        if url:
            return url
    return _commons(queries[0])


def get_images(names):
    """Récupère les images en parallèle. Les échecs ne sont PAS mis en cache,
    donc un plat sans image sera retenté à la prochaine recherche."""
    cache = st.session_state.setdefault("img_cache", {})
    missing = [n for n in names if n not in cache]
    if missing:
        with ThreadPoolExecutor(max_workers=6) as pool:
            for n, url in zip(missing, pool.map(fetch_image, missing)):
                if url:
                    cache[n] = url
    return {n: cache.get(n) for n in names}


# =====================================
# 7. INTERFACE
# =====================================
st.markdown("""
<div class="fm-hero">
  <h1>FoodMind</h1>
  <p>Dites-nous ce que vous avez dans le frigo, on vous propose les recettes les plus adaptées.</p>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### Vos ingrédients")
    selected_ingredients = st.multiselect(
        "Sélectionnez vos ingrédients",
        options=ingredient_options,
        placeholder="Tapez pour rechercher : tomato, lentils, onion...",
        label_visibility="collapsed",
    )
    c1, c2 = st.columns([2, 1])
    with c1:
        number_recipes = st.slider("Nombre de recettes à afficher", 1, 10, 5)
    with c2:
        st.write("")
        st.write("")
        search = st.button("Trouver des recettes", type="primary", use_container_width=True)


# =====================================
# 8. RECHERCHE DES RECETTES
# =====================================
def render_card(recipe, image_url, selected):
    esc = html.escape
    desc = recipe["Description"]
    desc = esc(str(desc)) if pd.notna(desc) else "Aucune description disponible."

    chips = []
    for ing in recipe["Ingredients"]:
        label = display_ingredient(ing)
        if not label:
            continue
        hit = any(s in label.lower() for s in selected)
        chips.append(f'<span class="fm-chip{" hit" if hit else ""}">{esc(label)}</span>')

    media = (f'<img src="{esc(image_url, quote=True)}" alt="{esc(recipe["Recipe_Name"])}" loading="lazy">'
             if image_url else "🍲")
    pct = recipe["Score"] * 100

    return (
        '<div class="fm-card">'
        f'<div class="fm-img">{media}</div>'
        '<div class="fm-body">'
        '<div class="fm-top">'
        f'<h3 class="fm-title">{esc(str(recipe["Recipe_Name"]))}</h3>'
        f'<div class="fm-score">{pct:.0f}%<small>compatibilité</small></div>'
        '</div>'
        f'<p class="fm-desc">{desc}</p>'
        f'<div class="fm-bar"><span style="width:{pct:.0f}%"></span></div>'
        '<div class="fm-label">Ingrédients</div>'
        f'<div class="fm-chips">{"".join(chips)}</div>'
        '</div></div>'
    )


if search:
    if not selected_ingredients:
        st.warning("Sélectionnez au moins un ingrédient pour lancer la recherche.")
    else:
        panier = " ".join(selected_ingredients)
        rows = [r for _, r in data.iterrows() if r["Ingredients_List"]]

        with st.spinner("Recherche des meilleures recettes..."):
            texts = ["panier " + panier + " recette " + " ".join(r["Ingredients_List"]) for r in rows]
            if texts:
                scores = np.clip(model.predict(vectorizer.transform(texts)), 0, 1)
            else:
                scores = []

            results = sorted(
                [{
                    "Recipe_Name": r["Recipe_Name"],
                    "Description": r["Description"],
                    "Ingredients": r["Ingredients_List"],
                    "Score": float(s),
                } for r, s in zip(rows, scores)],
                key=lambda x: x["Score"], reverse=True,
            )[:number_recipes]

            images = get_images([r["Recipe_Name"] for r in results])

        st.markdown("## Vos recettes recommandées")
        if not results:
            st.info("Aucune recette exploitable n'a été trouvée. Essayez d'autres ingrédients.")
        else:
            selected_lower = [s.lower() for s in selected_ingredients]
            for recipe in results:
                st.markdown(render_card(recipe, images.get(recipe["Recipe_Name"]), selected_lower),
                            unsafe_allow_html=True)