
import streamlit as st

# =========================
# NutriStep – Kalorické výpočty
# =========================

def calculate_bmr_formula(weight, height, age, gender):
    if gender == "Muž":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161


st.set_page_config(page_title="NutriStep – Kalorické výpočty", layout="centered")

st.title("NutriStep")
st.subheader("Mgr. Jaroslav Přidal")
st.write("Aplikace pro kalorické výpočty")

st.divider()

# ====== ZÁKLAD ======

gender = st.selectbox("Pohlaví", ["Muž", "Žena"])
age = st.number_input("Věk (roky)", 10, 100, 30)
height = st.number_input("Výška (cm)", 100, 250, 170)
weight = st.number_input("Váha (kg)", 30.0, 300.0, 80.0)

st.subheader("Bazální metabolismus (BMR)")

bmr_option = st.radio(
    "Způsob zadání BMR:",
    ["Zadat ručně", "Nevím – spočítat rovnicí"]
)

if bmr_option == "Zadat ručně":
    bmr = st.number_input("Zadej hodnotu BMR (kcal)", 500.0, 4000.0, 1700.0)
else:
    bmr = calculate_bmr_formula(weight, height, age, gender)
    st.write(f"Vypočítané BMR (Mifflin-St Jeor): {bmr:.0f} kcal")

st.divider()

# ====== AKTIVITA ======

weekly_active_calories = st.number_input(
    "Součet aktivních kalorií za 7 dní (kcal)",
    0.0,
    20000.0,
    2500.0
)

st.divider()

# ====== CÍL ======

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

# ====== VÝPOČET ======

if st.button("Spočítat kalorický plán"):

    KCAL_PROTEIN = 4
    KCAL_CARBS = 4
    KCAL_FAT = 9

    # 1️⃣ Základ bez TEF
    weekly_base_expenditure = (bmr * 7) + weekly_active_calories
    daily_base_expenditure = weekly_base_expenditure / 7

    # 2️⃣ Přičtení TEF
    tdee = daily_base_expenditure / 0.90
    weekly_total_expenditure = tdee * 7
    tef_daily = tdee * 0.10

    # 3️⃣ Úprava dle cíle
    if goal == "Redukce hmotnosti":
        target_calories = tdee - adjustment
        weekly_energy_change = adjustment * 7

    elif goal == "Nárůst hmotnosti":
        target_calories = tdee + adjustment
        weekly_energy_change = adjustment * 7

    else:
        target_calories = tdee
        weekly_energy_change = 0

    # 🔴 Ochrana proti příjmu pod BMR
    if target_calories < bmr:
        st.error("Nelze nastavit příjem pod hodnotu BMR. Snižte deficit.")
        st.stop()

    # 4️⃣ Odhad změny hmotnosti
    predicted_weight_change = weekly_energy_change / 7700

    # ====== MAKRA ======

    fat_kcal = target_calories * 0.30
    fat_g = fat_kcal / KCAL_FAT

    protein_g = weight * protein_per_kg
    protein_kcal = protein_g * KCAL_PROTEIN

    remaining_kcal = target_calories - (fat_kcal + protein_kcal)
    carbs_g = remaining_kcal / KCAL_CARBS

    # ====== VÝSTUP ======

    st.subheader("Energetický výdej")

    st.write(f"BMR: {bmr:.0f} kcal")
    st.write(f"Průměrná denní spotřeba (včetně TEF): {tdee:.0f} kcal")
    st.write(f"Týdenní výdej: {weekly_total_expenditure:.0f} kcal")
    st.write(f"Denní TEF: {tef_daily:.0f} kcal")

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