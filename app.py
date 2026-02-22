import streamlit as st

# ===============================
# NutriStep – Kalorické výpočty
# Mgr. Jaroslav Přidal
# ===============================

st.set_page_config(page_title="NutriStep – Kalorické výpočty", layout="centered")

# Skrytí Streamlit menu
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# ===============================
# Funkce
# ===============================

def calculate_bmr(weight, height, age, gender):
    if gender == "Muž":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161


# ===============================
# UI
# ===============================

st.title("NutriStep")
st.subheader("Mgr. Jaroslav Přidal")
st.write("Aplikace pro kalorické výpočty")

st.divider()

# --- ZÁKLADNÍ ÚDAJE ---

gender = st.selectbox("Pohlaví", ["Muž", "Žena"])
age = st.number_input("Věk (roky)", 10, 100, 30)
height = st.number_input("Výška (cm)", 100, 250, 170)
weight = st.number_input("Váha (kg)", 30.0, 300.0, 80.0)

st.subheader("Bazální metabolismus (BMR)")

bmr_mode = st.radio(
    "Způsob zadání BMR:",
    ["Zadat ručně", "Vypočítat rovnicí (Mifflin-St Jeor)"]
)

if bmr_mode == "Zadat ručně":
    bmr = st.number_input("Hodnota BMR (kcal)", 500.0, 4000.0, 1700.0)
else:
    bmr = calculate_bmr(weight, height, age, gender)
    st.write(f"Vypočítané BMR: {bmr:.0f} kcal")

st.divider()

# --- AKTIVITA ---

st.subheader("Způsob zadání aktivity")

activity_mode = st.radio(
    "",
    ["Aktivní kalorie za 7 dní", "Paušální faktor aktivity"]
)

if activity_mode == "Aktivní kalorie za 7 dní":
    weekly_active_calories = st.number_input(
        "Součet aktivních kalorií za 7 dní (kcal)",
        0.0,
        30000.0,
        2500.0
    )
    activity_factor = None
else:
    activity_factor = st.selectbox(
        "Vyber faktor aktivity",
        {
            "Sedavý (1.2)": 1.2,
            "Lehká aktivita (1.375)": 1.375,
            "Střední aktivita (1.55)": 1.55,
            "Vysoká aktivita (1.725)": 1.725
        }
    )
    weekly_active_calories = None

st.divider()

# --- CÍL ---

goal = st.selectbox(
    "Cíl:",
    ["Redukce hmotnosti", "Udržování hmotnosti", "Nárůst hmotnosti"]
)

adjustment = 0.0

if goal == "Redukce hmotnosti":
    adjustment = st.number_input("Denní deficit (kcal)", 0.0, 2000.0, 500.0)

elif goal == "Nárůst hmotnosti":
    adjustment = st.number_input("Denní surplus (kcal)", 0.0, 2000.0, 300.0)

protein_per_kg = st.number_input(
    "Bílkoviny (g / kg tělesné hmotnosti)",
    0.5,
    3.5,
    1.8
)

st.divider()

# ===============================
# VÝPOČET
# ===============================

if st.button("Spočítat kalorický plán"):

    KCAL_PROTEIN = 4
    KCAL_CARBS = 4
    KCAL_FAT = 9

    # --- Výpočet základního výdeje ---
    if activity_mode == "Aktivní kalorie za 7 dní":
        weekly_base = (bmr * 7) + weekly_active_calories
        daily_base = weekly_base / 7
    else:
        daily_base = bmr * activity_factor

    # Přičtení TEF (10 %)
    tdee = daily_base / 0.90
    weekly_tdee = tdee * 7
    tef_daily = tdee * 0.10

    # --- Úprava dle cíle ---
    if goal == "Redukce hmotnosti":
        target_calories = tdee - adjustment
        weekly_energy_change = adjustment * 7
    elif goal == "Nárůst hmotnosti":
        target_calories = tdee + adjustment
        weekly_energy_change = adjustment * 7
    else:
        target_calories = tdee
        weekly_energy_change = 0

    # --- Ochrana proti příjmu pod BMR ---
    if target_calories < bmr:
        st.error("Nelze nastavit příjem pod hodnotu BMR. Snižte deficit.")
        st.stop()

    # --- Odhad změny hmotnosti ---
    predicted_weight_change = weekly_energy_change / 7700

    # --- Makroživiny ---
    fat_kcal = target_calories * 0.30
    fat_g = fat_kcal / KCAL_FAT

    protein_g = weight * protein_per_kg
    protein_kcal = protein_g * KCAL_PROTEIN

    remaining_kcal = target_calories - (fat_kcal + protein_kcal)
    carbs_g = remaining_kcal / KCAL_CARBS

    # ===============================
    # VÝSTUP
    # ===============================

    st.subheader("Energetický výdej")

    st.write(f"BMR: {bmr:.0f} kcal")
    st.write(f"Průměrná denní spotřeba (včetně TEF): {tdee:.0f} kcal")
    st.write(f"Týdenní výdej: {weekly_tdee:.0f} kcal")
    st.write(f"Denní TEF (10 %): {tef_daily:.0f} kcal")

    st.divider()

    st.subheader("Plánovaný příjem")

    st.write(f"Doporučený denní příjem: {target_calories:.0f} kcal")

    if goal != "Udržování hmotnosti":
        st.write(f"Týdenní energetická změna: {weekly_energy_change:.0f} kcal")
        st.write(f"Odhad změny hmotnosti: {predicted_weight_change:.2f} kg / týden")

    st.divider()

    st.subheader("Makroživiny")

    st.write(f"Bílkoviny: {protein_g:.0f} g ({protein_kcal:.0f} kcal)")
    st.write(f"Tuky (30 %): {fat_g:.0f} g ({fat_kcal:.0f} kcal)")
    st.write(f"Sacharidy: {carbs_g:.0f} g ({remaining_kcal:.0f} kcal)")