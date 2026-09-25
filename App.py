# Configuration & iPad-friendly Page Setup
st.set_page_config(
    page_title="Grandma's Embroidered Cookbook",
    page_icon="📖",
    layout="wide"
)

# Custom Styling for "Libretto / Freeform Moodboard" feel
st.markdown("""
<style>
    .main-header {
        font-family: 'Georgia', serif;
        color: #2c3e50;
        text-align: center;
        padding-bottom: 10px;
    }
    .recipe-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        border: 1px solid #eef2f5;
        text-align: center;
    }
    .tag-badge {
        background-color: #e0f2fe;
        color: #0369a1;
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
# DATABASE & ANAGRAFICA (Fase 1)
# ---------------------------------------------------------
if "recipes_db" not in st.session_state:
    st.session_state.recipes_db = {
        "matcha_oats": {
            "title": "Matcha Morning Oats",
            "category": "Breakfast",
            "image_url": "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=500",
            "creator_link": "https://pinterest.com",
            "notes": "Usare latte d'avena non zuccherato per non alterare l'indice glicemico.",
            "tags": ["High-Fiber", "Antioxidants", "Low-GI"],
            "ingredients": [
                {"name": "rolled oats", "quantity": 50, "unit": "g"},
                {"name": "almond milk", "quantity": 200, "unit": "ml"},
                {"name": "matcha powder", "quantity": 5, "unit": "g"},
                {"name": "chia seeds", "quantity": 10, "unit": "g"}
            ]
        },
        "turmeric_chickpea_stew": {
            "title": "Turmeric Chickpea Stew",
            "category": "Savory Mains",
            "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500",
            "creator_link": "https://instagram.com",
            "notes": "Cottura lenta per 20 minuti. Ottimo anche scaldata il giorno dopo!",
            "tags": ["Anti-Inflammatory", "Vegan", "High-Fiber"],
            "ingredients": [
                {"name": "canned chickpeas", "quantity": 400, "unit": "g"},
                {"name": "coconut milk", "quantity": 200, "unit": "ml"},
                {"name": "turmeric", "quantity": 5, "unit": "g"},
                {"name": "spinach", "quantity": 100, "unit": "g"},
                {"name": "yellow onion", "quantity": 1, "unit": "item"}
            ]
        },
        "vietnamese_noodle_soup": {
            "title": "Quick Tofu Pho",
            "category": "Savory Mains",
            "image_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=500",
            "creator_link": "https://tiktok.com",
            "notes": "Aggiungere germogli di soia freschi a fine cottura per mantenere la croccantezza.",
            "tags": ["B12-Rich", "High-Protein", "Comfort Food"],
            "ingredients": [
                {"name": "rice noodles", "quantity": 100, "unit": "g"},
                {"name": "vegetable broth", "quantity": 500, "unit": "ml"},
                {"name": "firm tofu", "quantity": 150, "unit": "g"},
                {"name": "bok choy", "quantity": 150, "unit": "g"},
                {"name": "yellow onion", "quantity": 1, "unit": "item"}
            ]
        }
    }

# ---------------------------------------------------------
# MOTORE SPESA (Fase 2)
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

# ---------------------------------------------------------
# MATRICE NUTRIZIONALE SCIENTIFICA (Fase 3)
# ---------------------------------------------------------
NUTRITION_RULES = [
    {
        "id": "curcumin_pepper",
        "trigger": ["turmeric"],
        "booster": ["black pepper"],
        "type": "synergy",
        "message": "💡 **Sinergia Curcumina + Pepe**: La curcuma richiede la piperina del pepe nero per aumentare l'assorbimento fino al 2000%."
    },
    {
        "id": "iron_vit_c",
        "trigger": ["spinach", "canned chickpeas", "firm tofu", "lentils"],
        "booster": ["lemon", "lime", "bell pepper", "orange", "broccoli"],
        "type": "synergy",
        "message": "💡 **Sinergia Ferro Non-Eme + Vitamina C**: I tuoi piatti contengono fonti vegetali di ferro. Aggiungi succo di limone fresco per triplicarne l'assimilazione."
    },
    {
        "id": "fat_soluble_vitamins",
        "trigger": ["spinach", "carrots", "kale", "tomatoes"],
        "booster": ["olive oil", "coconut milk", "avocado", "nuts", "chia seeds"],
        "type": "synergy",
        "message": "💡 **Sinergia Vitamine Liposolubili**: Gli antiossidanti e le vitamine A/K richiedono grassi sani (olio d'oliva/cocco/semi) per essere assorbiti dal corpo."
    },
    {
        "id": "coffee_tea_iron_inhibitor",
        "trigger": ["spinach", "canned chickpeas", "firm tofu"],
        "booster": ["coffee", "black tea", "green tea"],
        "type": "inhibition",
        "message": "⚠️ **Inibitore Tannini/Polifenoli**: Evita di bere tè o caffè entro 1 ora dai pasti ricchi di ferro vegetale per non bloccarne l'assorbimento."
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
        elif rule["type"] == "inhibition" and has_trigger and has_booster:
            tips.append(rule["message"])

    return tips

# ---------------------------------------------------------
# INTERFACCIA VISIVA (Fase 4: Libretto Moodboard)
# ---------------------------------------------------------
st.markdown("<h1 class='main-header'>📖 Grandma's Embroidered Cookbook</h1>", unsafe_allow_html=True)
st.caption("✨ Touca le ricette per aprire l'anagrafica o spuntale per aggiungerle al piano settimanale.")

# Dialog Pop-up Modal per Anagrafica
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

# Layout a 2 colonne: Moodboard a Sinistra | Piano & Spesa a Destra
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🖼️ Freeform Canvas / Moodboard")
    
    selected_recipes = []
    grid_cols = st.columns(2)
    
    for idx, (r_id, details) in enumerate(st.session_state.recipes_db.items()):
        col = grid_cols[idx % 2]
        with col:
            st.image(details["image_url"], use_container_width=True)
            st.markdown(f"**{details['title']}**")
            
            # Badge dei Tag
            tags_html = "".join([f"<span class='tag-badge'>{tag}</span>" for tag in details['tags']])
            st.markdown(tags_html, unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("ℹ️ Anagrafica", key=f"info_{r_id}"):
                    show_recipe_modal(r_id)
            with c2:
                is_checked = st.checkbox("Scegli", key=f"chk_{r_id}")
                if is_checked:
                    selected_recipes.append(r_id)
            st.markdown("<br>", unsafe_allow_html=True)

with col_right:
    st.subheader("🛒 Piano Settimanale & Spesa")
    if selected_recipes:
        groceries = generate_consolidated_grocery_list(selected_recipes, st.session_state.recipes_db)
        tips = analyze_advanced_nutrition(selected_recipes, st.session_state.recipes_db)
        
        st.write("### Lista Unificata")
        for item in groceries.values():
            st.write(f"• **{item['quantity']} {item['unit']}** di {item['name']}")
            
        st.markdown("---")
        st.write("### 🧠 Sinergie Nutrizionali")
        if tips:
            for t in tips:
                st.info(t)
        else:
            st.success("✨ Tutte le sinergie nutrizionali sono ottimizzate!")
    else:
        st.warning("👈 Spunta almeno una ricetta dal moodboard per generare la spesa.")
