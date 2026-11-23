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

/* Forcer le thème clair, même si le navigateur est en mode sombre */
.stApp label, .stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stWidgetLabel"] {
    color: var(--ink) !important;
}
.stApp [data-baseweb="select"] > div, .stApp [data-baseweb="select"] input {
    background-color: var(--bg) !important;
    color: var(--ink) !important;
}
[data-baseweb="tag"] { background-color: var(--green) !important; color: #fff !important; border-radius: 999px !important; }
[data-baseweb="tag"] * { color: #fff !important; }
[data-baseweb="popover"] ul, [data-baseweb="popover"] li, [data-baseweb="menu"] {
    background-color: #fff !important; color: var(--ink) !important;
}
[data-baseweb="popover"] li:hover { background-color: var(--mint) !important; }
.stApp [data-baseweb="select"] svg { fill: var(--muted) !important; }

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
    flex: 0 0 300px; min-height: 260px; align-self: stretch;
    background: var(--mint);
    display: flex; align-items: center; justify-content: center;
    font-size: 4.5rem; line-height: 1;
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


/* Forcer des champs clairs (même si le thème Streamlit est sombre) */
.stApp, .stApp p, .stApp label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label { color: var(--ink) !important; }
[data-testid="stWidgetLabel"] p { font-weight: 600; }
.stMultiSelect [data-baseweb="select"] > div { background: #fff !important; color: var(--ink) !important; }
.stMultiSelect input { color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; }
.stMultiSelect svg { fill: var(--muted) !important; }
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li { background: #fff !important; color: var(--ink) !important; }
div[data-baseweb="popover"] li:hover { background: var(--mint) !important; }
div[data-baseweb="slider"] > div > div { background: var(--line); }
div[data-baseweb="slider"] > div > div > div { background: var(--green) !important; }
div[data-testid="stSliderTickBarMin"], div[data-testid="stSliderTickBarMax"] { color: var(--muted) !important; }
.fm-img.ph { flex-direction: column; gap: .6rem; font-size: 4.2rem; }
.fm-img.ph span { font-family: 'Figtree', sans-serif; font-size: .9rem; font-weight: 600; color: var(--green); }

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
          r"shredded|finely|roughly|thinly|peeled|pitted|packed|heaping|level|cubed|cut|"
          r"halved|quartered|trimmed|boneless|skinless|toasted|rinsed|drained|softened|melted|ground|extra|virgin|cold|warm|hot|boiling|lukewarm|ice|tap|filtered|"
          r"unsalted|salted|light|dark|organic|plain|kosher|sea|coarse|coarsely|cracked|good|quality|"
          r"low-sodium|reduced-sodium)")

_LEADING = re.compile(
    rf"^\s*(?:(?:and|or|plus|with|of|the|a|an)\s+)?"
    rf"(?:{_QTY}\s*-?\s*)?"
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

    # Mots parasites issus du scraping (publicités, etc.)
    text = re.sub(r"\b(?:advertisement|advertising|ad)\b", " ", text)

    # Tout ce qui suit la première virgule est une précision (drained, to taste...)
    text = text.split(",")[0]
    # "butter or margarine" -> "butter"
    text = re.split(r"\s+(?:or|plus)\s+", text)[0]

    # Mots parasites issus du scraping (publicités, liens...)
    text = re.sub(r"\b(?:advertisement|advertising|sponsored)\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # On retire plusieurs fois le début (quantité, unité, boîte, adjectifs, "and"...)
    for _ in range(5):
        new = _LEADING.sub("", text).strip()
        new = re.sub(r"^(?:and|or|plus|with|of|a|an|the)\s+(?=\S)", "", new)
        if new == text:
            break
        text = new
    text = re.sub(r"\s+(?:and|or|with)$", "", text)

    # Fins de phrase inutiles
    text = re.sub(r"\s+(?:to taste|for serving|for garnish|as needed|divided|drained|rinsed)$", "", text)
    text = re.sub(r"\s+", " ", text).strip(" \t\n,;:.-*")

    text = re.split(r"\s+(?:such as|like|e\.g\.)\s+", text)[0]

    if not text or len(text) < 2 or re.search(r"\d", text):
        return None

    # Regrouper les variantes d'un même ingrédient de base
    if text == "pepper":
        text = "black pepper"
    if re.fullmatch(r"(?:[a-z-]+ )?water", text):          # cold water, warm water...
        text = "water"
    if text.endswith("olive oil"):
        text = "olive oil"
    if text.endswith(" salt") or text == "salt":
        text = "salt"

    invalid_phrases = (
        "can also", "can be added", "added to", "to the vegetables",
        "optional", "according to taste", "about",
    )
    if any(p in text for p in invalid_phrases) or len(text.split()) > 4:
        return None

    return text


# =====================================
# 4b. TRADUCTION FRANCAISE DES INGREDIENTS
# =====================================
FR = {
 # phrases
 "ground black pepper":"poivre noir moulu","black pepper":"poivre noir","sweet potatoes":"patates douces",
 "sweet potato":"patate douce","olive oil":"huile d'olive","vegetable oil":"huile végétale",
 "coconut oil":"huile de coco","sesame oil":"huile de sésame","chicken broth":"bouillon de poulet",
 "vegetable broth":"bouillon de légumes","beef broth":"bouillon de bœuf","chicken stock":"bouillon de poulet",
 "vegetable stock":"bouillon de légumes","cherry tomatoes":"tomates cerises","tomato paste":"concentré de tomate",
 "tomato sauce":"sauce tomate","diced tomatoes":"tomates en dés","crushed tomatoes":"tomates concassées",
 "lemon juice":"jus de citron","lemon zest":"zeste de citron","orange juice":"jus d'orange",
 "orange zest":"zeste d'orange","brown sugar":"sucre roux","powdered sugar":"sucre glace",
 "all-purpose flour":"farine tout usage","baking powder":"levure chimique","baking soda":"bicarbonate de soude",
 "sea salt":"sel de mer","kosher salt":"sel casher","white wine":"vin blanc","red wine":"vin rouge",
 "greek yogurt":"yaourt grec","plain yogurt":"yaourt nature","heavy cream":"crème épaisse",
 "sour cream":"crème aigre","unsalted butter":"beurre doux","red lentils":"lentilles corail",
 "green lentils":"lentilles vertes","white pearl onions":"oignons grelots blancs","pearl onions":"oignons grelots",
 "lentil soup":"soupe de lentilles","red onion":"oignon rouge","red onions":"oignons rouges",
 "yellow onion":"oignon jaune","white onion":"oignon blanc","green onions":"oignons verts",
 "green onion":"oignon vert","red pepper":"poivron rouge","red bell pepper":"poivron rouge",
 "green bell pepper":"poivron vert","bell pepper":"poivron","bell peppers":"poivrons","green beans":"haricots verts",
 "garlic cloves":"gousses d'ail","cloves garlic":"gousses d'ail","clove garlic":"gousse d'ail",
 "garlic powder":"ail en poudre","onion powder":"oignon en poudre","smoked paprika":"paprika fumé",
 "chili powder":"piment en poudre","chili flakes":"flocons de piment","red pepper flakes":"flocons de piment",
 "bay leaves":"feuilles de laurier","bay leaf":"feuille de laurier","preserved lemons":"citrons confits",
 "preserved lemon":"citron confit","sesame seeds":"graines de sésame","pine nuts":"pignons de pin",
 "coconut milk":"lait de coco","soy sauce":"sauce soja","vanilla extract":"extrait de vanille",
 "cocoa powder":"cacao en poudre","ras el hanout":"ras el hanout","orange blossom water":"eau de fleur d'oranger",
 "rose water":"eau de rose","chickpea":"pois chiche","ground beef":"bœuf haché","ground lamb":"agneau haché",
 "chicken breast":"blanc de poulet","chicken breasts":"blancs de poulet","chicken thighs":"cuisses de poulet",
 "lamb shoulder":"épaule d'agneau","cooking spray":"spray de cuisson","cream cheese":"fromage frais",
 "goat cheese":"fromage de chèvre","fresh ginger":"gingembre frais","fresh parsley":"persil frais",
 # ingrédients
 "ground cloves":"clous de girofle moulus","ground cardamom":"cardamome moulue","green cardamom":"cardamome verte",
 "ground green cardamom":"cardamome verte moulue","dried bay leaves":"feuilles de laurier séchées",
 "star anise":"anis étoilé","fennel seeds":"graines de fenouil","ground fennel seeds":"graines de fenouil moulues",
 "fenugreek":"fenugrec","allspice":"piment de la Jamaïque","mace":"macis","lavender buds":"boutons de lavande",
 "chilli powder":"piment en poudre","chilli":"piment","extra virgin olive oil":"huile d'olive extra vierge",
 "cayenne pepper":"piment de Cayenne","ground cayenne":"piment de Cayenne moulu",
 "chickpeas":"pois chiches","lentils":"lentilles","couscous":"couscous","garlic":"ail","onion":"oignon",
 "onions":"oignons","tomato":"tomate","tomatoes":"tomates","potato":"pomme de terre","potatoes":"pommes de terre",
 "carrot":"carotte","carrots":"carottes","zucchini":"courgette","courgette":"courgette","eggplant":"aubergine",
 "cucumber":"concombre","spinach":"épinards","cabbage":"chou","cauliflower":"chou-fleur","broccoli":"brocoli",
 "mushrooms":"champignons","celery":"céleri","peas":"petits pois","beans":"haricots","corn":"maïs",
 "pumpkin":"citrouille","squash":"courge","avocado":"avocat","avocados":"avocats","lemon":"citron","lemons":"citrons",
 "lime":"citron vert","orange":"orange","oranges":"oranges","apple":"pomme","apples":"pommes","banana":"banane",
 "dates":"dattes","raisins":"raisins secs","apricots":"abricots","figs":"figues","olives":"olives",
 "almonds":"amandes","walnuts":"noix","pistachios":"pistaches","peanuts":"cacahuètes","honey":"miel",
 "sugar":"sucre","salt":"sel","pepper":"poivre","flour":"farine","butter":"beurre","milk":"lait","cream":"crème",
 "cheese":"fromage","yogurt":"yaourt","egg":"œuf","eggs":"œufs","water":"eau","oil":"huile","vinegar":"vinaigre",
 "rice":"riz","pasta":"pâtes","bread":"pain","semolina":"semoule","chicken":"poulet","beef":"bœuf","lamb":"agneau",
 "fish":"poisson","shrimp":"crevettes","salmon":"saumon","tuna":"thon","turkey":"dinde","meat":"viande",
 "sausage":"saucisse","broth":"bouillon","stock":"bouillon","soup":"soupe","parsley":"persil",
 "cilantro":"coriandre fraîche","coriander":"coriandre","mint":"menthe","basil":"basilic","thyme":"thym",
 "rosemary":"romarin","oregano":"origan","cumin":"cumin","cinnamon":"cannelle","turmeric":"curcuma",
 "ginger":"gingembre","paprika":"paprika","cayenne":"piment de Cayenne","chili":"piment","saffron":"safran",
 "nutmeg":"muscade","cloves":"clous de girofle","cardamom":"cardamome","harissa":"harissa","tahini":"tahini",
 "mustard":"moutarde","mayonnaise":"mayonnaise","chocolate":"chocolat","coconut":"noix de coco","wine":"vin",
 "vegetables":"légumes","vegetable":"légume","paste":"concentré","sauce":"sauce","juice":"jus","zest":"zeste",
 "leaves":"feuilles","seeds":"graines","powder":"poudre","spice":"épice","spices":"épices","mix":"mélange",
 # adjectifs / mots courants
 "ground":"moulu","fresh":"frais","dried":"séché","chopped":"haché","sliced":"tranché","diced":"en dés",
 "minced":"émincé","grated":"râpé","crushed":"écrasé","roasted":"rôti","red":"rouge","green":"vert",
 "white":"blanc","black":"noir","yellow":"jaune","large":"gros","small":"petit","medium":"moyen",
 "whole":"entier","cubed":"en cubes","plain":"nature","and":"et","or":"ou","with":"avec","to taste":"selon le goût",
 "for serving":"pour servir","for garnish":"pour décorer","divided":"divisé","optional":"facultatif",
 # unités
 "tablespoons":"c. à soupe","tablespoon":"c. à soupe","tbsp":"c. à soupe","teaspoons":"c. à café",
 "teaspoon":"c. à café","tsp":"c. à café","cups":"tasses","cup":"tasse","ounces":"oz","ounce":"oz",
 "pounds":"lb","pound":"lb","cans":"boîtes","can":"boîte","pinch":"pincée","bunch":"botte",
 "slices":"tranches","slice":"tranche","stalks":"branches","stalk":"branche","handful":"poignée",
 "cartons":"briques","carton":"brique","bag":"sachet","bags":"sachets","package":"paquet","jar":"bocal",
}
_FR_RE = re.compile(
    r"(?<![\w-])(" + "|".join(re.escape(k) for k in sorted(FR, key=len, reverse=True)) + r")(?![\w-])",
    re.IGNORECASE,
)


ADJ_FR = {"ground", "dried", "fresh", "chopped", "sliced", "minced", "grated", "crushed", "roasted"}


def to_french(text):
    """Traduction par dictionnaire (mots inconnus laissés tels quels)."""
    if not isinstance(text, str):
        return ""
    # L'adjectif se place après le nom en français : "ground cumin" -> "cumin ground"
    skip = {"black", "red", "white", "green", "yellow", "olive", "sweet", "bell", "hot", "bay", "star"}
    def swap(m):
        adj, noun = m.group(1).lower(), m.group(2).lower()
        if f"{adj} {noun}" in FR or noun in skip or noun in ADJ_FR:
            return m.group(0)
        return f"{noun} {adj}"
    text = re.sub(r"\b(ground|dried|fresh|chopped|sliced|minced|grated|crushed|roasted)\s+([A-Za-z]+)\b", swap, text, flags=re.I)
    out = _FR_RE.sub(lambda m: FR[m.group(1).lower()], text)
    # Accord au féminin pour quelques noms courants
    fem = r"(cannelle|coriandre|cardamome|muscade|moutarde|lavande|menthe|sauge|vanille)"
    for m_, f_ in (("moulu", "moulue"), ("séché", "séchée"), ("frais", "fraîche"), ("haché", "hachée"), ("râpé", "râpée")):
        out = re.sub(rf"\b{fem} {m_}\b", rf"\1 {f_}", out)
    out = re.sub(r"\bde ([aeiouéèœ])", r"d'\1", out)
    return out



def display_ingredient(ingredient):
    """Ingrédient complet (avec quantité) pour l'affichage dans la carte."""
    if not isinstance(ingredient, str):
        return ""
    text = html.unescape(ingredient).replace("\xa0", " ")
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\([^)]*\)", "", text)
    text = text.split(",")[0]
    text = re.sub(r"\badvertisement\b", "", text, flags=re.I)
    text = re.sub(r"(\d)\s*-\s*(ounce|oz)\b\.?", r"\1 oz", text, flags=re.I)
    text = re.sub(r"^\s*(?:and|or)\s+", "", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip(" \t\n,;:.-*•")


# =====================================
# 5. GENERATION DE LA LISTE DE RECHERCHE
# =====================================
@st.cache_data
def build_options(_data, min_recipes=2):
    """Ingrédients de base, triés du plus courant au plus rare.
    Ceux présents dans une seule recette (souvent du bruit) sont masqués."""
    counts = {}
    for ingredients in _data["Ingredients_List"]:
        if isinstance(ingredients, list):
            names = {clean_ingredient_name(i) for i in ingredients}
            for n in names:
                if n:
                    counts[n] = counts.get(n, 0) + 1
    kept = {n: c for n, c in counts.items() if c >= min_recipes} or counts
    ordered = sorted(kept, key=lambda n: (-kept[n], n))
    return ordered, kept


ingredient_options, ingredient_counts = build_options(data)


# =====================================
# 6. RECUPERATION DES IMAGES
# =====================================
HEADERS = {"User-Agent": "FoodMindRecipeApp/1.0 (student project)"}
_STOP = {"with", "and", "the", "free", "easy", "best", "simple", "quick", "homemade", "recipe",
         "authentic", "traditional", "style", "from", "for", "gluten", "dairy", "soy"}


def _tokens(text):
    return {w for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 2 and w not in _STOP}


_DISH_WORDS = {"tagine", "tajine", "couscous", "harira", "hummus", "falafel", "shakshuka", "baklava",
               "tabbouleh", "pastilla", "bastilla", "msemen", "baghrir", "harissa", "kefta", "zaalouk",
               "tanjia", "mechoui", "rfissa", "briouat", "chebakia", "sellou"}


def _similar(query, title):
    """MealDB : il faut au moins 2 mots en commun (ou tous, si le nom est court)."""
    q, t = _tokens(query), _tokens(title)
    if not q or not t:
        return False
    need = len(q) if len(q) <= 2 else -(-len(q) * 6 // 10)
    return len(q & t) >= need


def _wiki_ok(query, title):
    """Wikipedia : le titre de l'article doit être contenu dans le nom du plat
    (ex. « Ras el hanout »), jamais un mot générique comme « Chicken »."""
    q, t = _tokens(query), _tokens(title)
    if not t or not t <= q:
        return False
    return len(t) >= 2 or bool(t & _DISH_WORDS)


def _search_queries(recipe_name):
    name = re.sub(r"\([^)]*\)", " ", recipe_name)
    name = re.sub(r"\s+", " ", name).strip(" -,")
    short = re.split(r"\s+(?:with|and|&)\s+|,|\s-\s", name, flags=re.I)[0].strip()
    # "Vickys Ras-El-Hanout ..." -> enlever le prénom possessif en tête
    short = re.sub(r"^\w+s'?s?\s+(?=[A-Z])", "", short) if re.match(r"^\w+ys\s", short) else short
    seen, res = set(), []
    for v in (name, short):
        if v and v.lower() not in seen:
            seen.add(v.lower())
            res.append(v)
    return res


def _mealdb(query):
    try:
        r = requests.get("https://www.themealdb.com/api/json/v1/1/search.php",
                         params={"s": query}, timeout=6)
        r.raise_for_status()
        for meal in r.json().get("meals") or []:
            if meal.get("strMealThumb") and _similar(query, meal.get("strMeal", "")):
                return meal["strMealThumb"]
    except (requests.RequestException, ValueError, TypeError):
        pass
    return None


def _wikipedia(query):
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "generator": "search", "gsrsearch": query,
                    "gsrlimit": 5, "prop": "pageimages", "piprop": "thumbnail",
                    "pithumbsize": 700, "format": "json"},
            headers=HEADERS, timeout=6)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in sorted(pages.values(), key=lambda p: p.get("index", 99)):
            thumb = page.get("thumbnail", {}).get("source")
            if thumb and _wiki_ok(query, page.get("title", "")):
                return thumb
    except (requests.RequestException, ValueError, TypeError):
        pass
    return None


def fetch_image(recipe_name):
    """Cherche une photo UNIQUEMENT si son titre correspond au plat.
    Sinon None : on préfère un joli visuel de remplacement à une mauvaise photo."""
    if not isinstance(recipe_name, str) or not recipe_name.strip():
        return None
    queries = _search_queries(clean_title(recipe_name))
    for q in queries:
        url = _mealdb(q) or _wikipedia(q)
        if url:
            return url
    return None


def get_images(names):
    cache = st.session_state.setdefault("img_cache", {})
    missing = [n for n in names if n not in cache]
    if missing:
        with ThreadPoolExecutor(max_workers=6) as pool:
            for n, url in zip(missing, pool.map(fetch_image, missing)):
                if url:
                    cache[n] = url
    return {n: cache.get(n) for n in names}


def placeholder_for(recipe_name, ingredients):
    """Emoji + type de plat, déduits du nom et des ingrédients."""
    text = (recipe_name + " " + " ".join(i for i in ingredients if isinstance(i, str))).lower()
    rules = [
        (("tagine", "tajine"), "🫕", "Tajine"), (("couscous",), "🍚", "Couscous"),
        (("soup", "harira", "broth"), "🍜", "Soupe"), (("salad", "salade"), "🥗", "Salade"),
        (("bread", "msemen", "baghrir", "pancake"), "🫓", "Pain & crêpes"),
        (("cake", "cookie", "dessert", "sweet", "pastry", "dough"), "🍰", "Dessert"),
        (("spice", "ras el hanout", "seasoning", "mix"), "🌶️", "Épices"),
        (("chicken", "poultry"), "🍗", "Poulet"), (("lamb", "beef", "meat", "kefta", "kebab"), "🍖", "Viande"),
        (("fish", "salmon", "tuna", "shrimp"), "🐟", "Poisson"), (("lentil", "chickpea", "bean"), "🫘", "Légumineuses"),
        (("rice", "pasta"), "🍚", "Plat complet"),
    ]
    for keys, emoji, label in rules:
        if any(k in text for k in keys):
            return emoji, label
    return "🍲", "Plat marocain"


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
        format_func=lambda n: f"{to_french(n)}  ·  {ingredient_counts.get(n, 0)} recettes",
        placeholder="Tapez pour rechercher : tomates, lentilles, oignon...",
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
def dish_emoji(name):
    n = str(name).lower()
    rules = [
        (("soup", "harira", "stew", "broth"), "🍲"), (("tagine", "tajine"), "🥘"),
        (("salad", "zaalouk", "taktouka"), "🥗"), (("chicken", "poultry"), "🍗"),
        (("lamb", "beef", "kefta", "kebab", "meat", "mince"), "🥩"),
        (("fish", "sardine", "salmon", "shrimp", "seafood"), "🐟"),
        (("couscous", "rice", "pasta", "lentil"), "🍚"),
        (("cake", "cookie", "dessert", "sweet", "pastry", "chebakia", "date"), "🍰"),
        (("bread", "msemen", "baghrir", "pancake", "khobz"), "🍞"),
        (("tea", "drink", "juice"), "🍵"), (("egg", "omelet"), "🍳"),
        (("spice", "ras-el-hanout", "ras el hanout", "seasoning", "mix"), "🧂"),
        (("potato", "carrot", "vegetable", "pumpkin", "zucchini"), "🥕"),
    ]
    for keys, emoji in rules:
        if any(k in n for k in keys):
            return emoji
    return "🍽️"


def clean_title(name):
    """Enlève le prénom de l'auteur ("Vickys ...") et les mentions régime (", Gluten-Free")."""
    s = html.unescape(str(name)).strip()
    s = re.split(r",|\s[-–|]\s", s)[0]
    s = re.sub(r"\b(?:gluten|dairy|egg|soy|nut|sugar)[- ]free\b", "", s, flags=re.I)
    m = re.match(r"^[A-Z][a-z]+(?:ys|'s|’s)\s+(.+)", s)
    if m:
        s = m.group(1)
    return re.sub(r"\s+", " ", s).strip(" &-,") or str(name)


def render_card(recipe, image_url, selected):
    esc = html.escape
    desc = recipe["Description"]
    desc = esc(str(desc)) if pd.notna(desc) else "Aucune description disponible."

    chips = []
    for ing in recipe["Ingredients"]:
        raw = display_ingredient(ing)
        if not raw:
            continue
        hit = any(s in raw.lower() for s in selected)
        chips.append(f'<span class="fm-chip{" hit" if hit else ""}">{esc(to_french(raw))}</span>')

    if image_url:
        media = f'<div class="fm-img"><img src="{esc(image_url, quote=True)}" alt="{esc(clean_title(recipe["Recipe_Name"]))}" loading="lazy"></div>'
    else:
        emoji, label = placeholder_for(clean_title(recipe["Recipe_Name"]), recipe["Ingredients"])
        media = f'<div class="fm-img ph">{emoji}<span>{label}</span></div>'
    pct = recipe["Score"] * 100

    return (
        '<div class="fm-card">'
        f'{media}'
        '<div class="fm-body">'
        '<div class="fm-top">'
        f'<h3 class="fm-title">{esc(clean_title(recipe["Recipe_Name"]))}</h3>'
        f'<div class="fm-score">{pct:.0f}%<small>compatibilité</small></div>'
        '</div>'
        f'<p class="fm-desc">{desc}</p>'
        f'<div class="fm-bar"><span style="width:{pct:.0f}%"></span></div>'
        '<div class="fm-label">Ingrédients</div>'
        f'<div class="fm-chips">{"".join(chips)}</div>'
        '</div></div>'
    )


IMAGE_COL = next((c for c in data.columns if any(k in c.lower() for k in ("image", "photo", "img", "thumbnail"))), None)

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
                    "Image": (r[IMAGE_COL] if IMAGE_COL and isinstance(r[IMAGE_COL], str)
                              and r[IMAGE_COL].startswith("http") else None),
                } for r, s in zip(rows, scores)],
                key=lambda x: x["Score"], reverse=True,
            )[:number_recipes]

            images = get_images([r["Recipe_Name"] for r in results if not r["Image"]])

        st.markdown("## Vos recettes recommandées")
        if not results:
            st.info("Aucune recette exploitable n'a été trouvée. Essayez d'autres ingrédients.")
        else:
            selected_lower = [s.lower() for s in selected_ingredients]
            for recipe in results:
                st.markdown(render_card(recipe, recipe["Image"] or images.get(recipe["Recipe_Name"]), selected_lower),
                            unsafe_allow_html=True)