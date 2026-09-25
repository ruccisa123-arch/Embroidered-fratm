import streamlit as st
import json

# Setup Pagina iPad-Friendly
st.set_page_config(
    page_title="Grandma's Embroidered Cookbook",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# STILE CSS: COVER BOOK & FREEFORM CANVAS
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Sfondo Generale Minimal */
    .stApp {
        background-color: #f7f4ef;
    }
    
    /* Copertina del Libretto Tridimensionale */
    .book-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 70vh;
    }
    
    .book-cover {
        width: 320px;
        height: 440px;
        background: linear-gradient(135deg, #7c2d12 0%, #451a03 100%);
        border-radius: 12px 24px 24px 12px;
        box-shadow: 15px 20px 30px rgba(0,0,0,0.3), inset 4px 0 10px rgba(255,255,255,0.2);
        border-left: 12px solid #290e02;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #fef3c7;
        font-family: 'Georgia', serif;
        text-align: center;
        padding: 20px;
        cursor: pointer;
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }
    
    .book-cover:hover {
        transform: translateY(-8px) rotate(-1deg);
        box-shadow: 20px 28px 35px rgba(0,0,0,0.35);
    }

    .embroidered-border {
        border: 2px dashed #f59e0b;
        padding: 30px 15px;
        border-radius: 8px;
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .tag-badge {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin: 2px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# STATE & DATABASE (Fase 1)
# ---------------------------------------------------------
if "book_open" not in st.session_state:
    st.session_state.book_open = False

if "recipes_db" not in st.session_state:
    st.session_state.recipes_db = {
        "matcha_oats": {
            "title": "Matcha Morning Oats",
            "category": "Breakfast",
            "image_url": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=500",
            "creator_link": "https://pinterest.com",
            "notes": "Usare latte d'avena non zuccherato per non alterare l'indice glicemico.",
            "tags": ["High-Fiber", "Antioxidants"],
            "ingredients": [
                {"name": "rolled oats", "quantity": 50, "unit": "g"},
                {"name": "almond milk", "quantity": 200, "unit": "ml"},
                {"name": "matcha powder", "quantity": 5, "unit": "g"}
            ]
        },
        "turmeric_chickpea_stew": {
            "title": "Turmeric Chickpea Stew",
            "category": "Savory Mains",
            "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500",
            "creator_link": "https://instagram.com",
            "notes": "Cottura lenta per 20 minuti.",
            "tags": ["Anti-Inflammatory", "Vegan"],
            "ingredients": [
                {"name": "canned chickpeas", "quantity": 400, "unit": "g"},
                {"name": "coconut milk", "quantity": 200, "unit": "ml"},
                {"name": "turmeric", "quantity": 5, "unit": "g"},
                {"name": "spinach", "quantity": 100, "unit": "g"}
            ]
        }
    }

# ---------------------------------------------------------
# MOTORE SPESA & MATRICE NUTRIZIONALE (Fasi 2 e 3)
# ---------------------------------------------------------
def generate_consolidated_grocery_list(selected_ids, database):
    consolidated = {}
    for r_id in selected_ids:
        if r_id in database:
            for item in database[r_id]["ingredients"]:
                name = item["name"].strip().lower()
                qty = item["quantity"]
                unit = item["unit"].strip().lower()
                key = (name, unit)
                if key in consolidated:
                    consolidated[key]["quantity"] += qty
                else:
                    consolidated[key] = {"name": name, "quantity": qty, "unit": unit}
    return consolidated

NUTRITION_RULES = [
    {
        "id": "iron_vit_c",
        "trigger": ["spinach", "canned chickpeas"],
        "booster": ["lemon", "bell pepper"],
        "type": "synergy",
        "message": "💡 **Sinergia Ferro Non-Eme + Vitamina C**: Aggiungi succo di limone fresco per triplicare l'assorbimento del ferro vegetale."
    }
]

def analyze_advanced_nutrition(selected_recipe_ids, database):
    tips = []
    all_ingredients = set()
    for r_id in selected_recipe_ids:
        if r_id in database:
            for item in database[r_id]["ingredients"]:
                all_ingredients.add(item["name"].lower())

    for rule in NUTRITION_RULES:
        has_trigger = any(ing in all_ingredients for ing in rule["trigger"])
        has_booster = any(ing in all_ingredients for ing in rule["booster"])
        if rule["type"] == "synergy" and has_trigger and not has_booster:
            tips.append(rule["message"])
    return tips

# Modal Anagrafica Pop-Up
@st.dialog("📋 Anagrafica Ricetta")
def show_recipe_modal(r_id):
    recipe = st.session_state.recipes_db[r_id]
    st.image(recipe["image_url"], use_container_width=True)
    st.subheader(recipe["title"])
    st.write(f"**Categoria:** {recipe['category']}")
    st.write(f"**Note personali:** {recipe['notes']}")
    st.markdown(f"🔗 [Link al Creator / Blog originale]({recipe['creator_link']})")
    st.markdown("---")
    st.write("**Ingredienti:**")
    for ing in recipe["ingredients"]:
        st.write(f"• {ing['quantity']} {ing['unit']} di {ing['name']}")

# ---------------------------------------------------------
# HOMEPAGE: IL LIBRETTO (Copertina 3D)
# ---------------------------------------------------------
if not st.session_state.book_open:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown("""
        <div class="book-container">
            <div class="book-cover">
                <div class="embroidered-border">
                    <h1 style="font-size: 28px; margin-bottom: 5px;">Grandma's</h1>
                    <h2 style="font-size: 20px; font-weight: normal; color: #fef08a;">EMBROIDERED COOKBOOK</h2>
                    <p style="font-size: 12px; margin-top: 20px; color: #d97706;">✨ Tocca per aprire il ricettario</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Pulsante invisibile sopra la copertina per Aprire
        if st.button("📖 Apri il Libro", use_container_width=True):
            st.session_state.book_open = True
            st.rerun()

# ---------------------------------------------------------
# PAGINA INTERNA: FREEFORM COLLAGE CANVAS
# ---------------------------------------------------------
else:
    # Header Navigazione
    top_col1, top_col2 = st.columns([6, 1])
    with top_col1:
        st.markdown("<h2 style='font-family: Georgia, serif; color: #451a03;'>📖 Il tuo Libretto Freeform</h2>", unsafe_allow_html=True)
    with top_col2:
        if st.button("📕 Chiudi Libro"):
            st.session_state.book_open = False
            st.rerun()

    st.caption("✨ Trascina e organizza liberamente i tuoi ritagli nella pagina collage. Tocca Anagrafica per aprire le note del creator.")

    # SIDEBAR: Aggiunta Nuove Ricette & Screenshot
    st.sidebar.title("➕ Aggiungi al Collage")
    with st.sidebar.form("add_recipe_form", clear_on_submit=True):
        new_title = st.text_input("Titolo Ricetta*")
        new_category = st.selectbox("Categoria", ["Breakfast", "Savory Mains", "Snacks", "Desserts"])
        new_creator = st.text_input("Link Creator / Pinterest", value="https://pinterest.com")
        new_notes = st.text_area("Note / Modifiche personali")
        new_tags = st.text_input("Tag", value="Anti-Inflammatory")
        uploaded_file = st.file_uploader("Carica Screenshot iPad", type=["jpg", "png", "webp"])
        ingredients_raw = st.text_area("Ingredienti (qty, unit, nome)", value="100, g, spinach")
        
        submitted = st.form_submit_button("✨ Incolla nel Libro")
        if submitted and new_title:
            recipe_id = new_title.lower().replace(" ", "_")
            img_src = uploaded_file if uploaded_file else "https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=500"
            
            parsed_ing = []
            for line in ingredients_raw.strip().split("\n"):
                parts = line.split(",")
                if len(parts) == 3:
                    try:
                        parsed_ing.append({"name": parts[2].strip(), "quantity": float(parts[0].strip()), "unit": parts[1].strip()})
                    except: pass

            st.session_state.recipes_db[recipe_id] = {
                "title": new_title,
                "category": new_category,
                "image_url": img_src,
                "creator_link": new_creator,
                "notes": new_notes,
                "tags": [t.strip() for t in new_tags.split(",") if t.strip()],
                "ingredients": parsed_ing
            }
            st.sidebar.success("Ritaglio aggiunto!")
            st.rerun()

    # LAYOUT PAGINA COLLAGE (Freeform Workspace)
    col_canvas, col_grocery = st.columns([2.5, 1])

    with col_canvas:
        st.markdown("### 🎨 La Pagina dei Ritagli")
        
        # Griglia Dinamica stile Scrapbook Collage
        selected_recipes = []
        cols = st.columns(2)
        
        for idx, (r_id, details) in enumerate(st.session_state.recipes_db.items()):
            target_col = cols[idx % 2]
            with target_col:
                # Card Visiva Stile Ritaglio
                st.image(details["image_url"], use_container_width=True)
                st.markdown(f"**{details['title']}**")
                
                b1, b2 = st.columns([1, 1])
                with b1:
                    if st.button("ℹ️ Anagrafica", key=f"info_{r_id}"):
                        show_recipe_modal(r_id)
                with b2:
                    if st.checkbox("Aggiungi", key=f"chk_{r_id}"):
                        selected_recipes.append(r_id)
                st.markdown("<hr style='border: 1px dashed #d1d5db;'>", unsafe_allow_html=True)

    with col_grocery:
        st.markdown("### 🛒 Lista Spesa & Sinergie")
        if selected_recipes:
            groceries = generate_consolidated_grocery_list(selected_recipes, st.session_state.recipes_db)
            tips = analyze_advanced_nutrition(selected_recipes, st.session_state.recipes_db)
            
            st.write("**Ingredienti Unificati:**")
            for item in groceries.values():
                st.write(f"• **{item['quantity']} {item['unit']}** di {item['name']}")
                
            if tips:
                st.markdown("---")
                st.write("**💡 Consigli Scientifici:**")
                for t in tips:
                    st.info(t)
        else:
            st.info("Spunta le ricette dal collage per calcolare la spesa unificata.")
