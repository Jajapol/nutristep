import streamlit as st
from datetime import datetime

# ======================================
# Nastavení stránky
# ======================================

st.set_page_config(page_title="NutriStep", layout="centered")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ======================================
# BRANDING FIRMY
# ======================================

st.title("NutriStep - Mgr. Jaroslav Přidal")

st.markdown("""
**Provozovatel:** NutriStep - Mgr. Jaroslav Přidal  
**IČO:** 24012289  
**Sídlo podnikání:** Budovatelů 173/7, Přerov  
**Telefon:** 773 699 937  
**E-mail:** pridal.jaroslav@icloud.com  
""")

st.caption(f"Aktuální datum: {datetime.now().strftime('%d.%m.%Y')}")

st.write("Profesionální aplikace pro kalorické výpočty")

# ======================================
# Funkce BMR
# ======================================

def calculate_bmr(weight, height, age, gender):
    if gender == "Muž":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161


# ======================================
# VSTUPY
# ======================================

st.divider()

gender = st.selectbox("Pohlaví", ["Muž", "Žena"])
age = st.number_input("Věk (roky)", 10, 100, 30)
height = st.number_input("Výška (cm)", 100, 250, 170)
weight = st.number_input("Váha (kg)", 30.0, 300.0, 80.0)

st.subheader("Bazální metabolismus (BMR)")

bmr_mode = st.radio("Způsob zadání BMR:", ["Zadat ručně", "Vypočítat rovnicí"])

if bmr_mode == "Zadat ručně":
    bmr = st.number_input("BMR (kcal)", 500.0, 4000.0, 1700.0)
else:
    bmr = calculate_bmr(weight, height, age, gender)
    st.write(f"Vypočítané BMR: {bmr:.0f} kcal")

st.divider()

# ======================================
# AKTIVITA
# ======================================

st.subheader("Způsob zadání aktivity")

activity_mode = st.radio(
    "",
    ["Paušální faktor aktivity", "Ruční zadání aktivních kalorií (7 dní)"]
)

if activity_mode == "Paušální faktor aktivity":

    activity_options = {
        "Sedavý (1.2)": 1.2,
        "Lehká aktivita (1.375)": 1.375,
        "Střední aktivita (1.55)": 1.55,
        "Vysoká aktivita (1.725)": 1.725
    }

    selected_activity = st.selectbox(
        "Faktor aktivity",
        list(activity_options.keys())
    )

    activity_factor = activity_options[selected_activity]
    weekly_active_calories = None

else:
    weekly_active_calories = st.number_input(
        "Součet aktivních kalorií za 7 dní (kcal)",
        0.0, 30000.0, 2500.0
    )
    activity_factor = None

st.divider()

# ======================================
# CÍL
# ======================================

goal = st.selectbox("Cíl", ["Redukce", "Udržování", "Nárůst"])

adjustment = 0
if goal == "Redukce":
    adjustment = st.number_input("Denní deficit (kcal)", 0, 2000, 500)
elif goal == "Nárůst":
    adjustment = st.number_input("Denní surplus (kcal)", 0, 2000, 300)

protein_per_kg = st.number_input("Bílkoviny (g/kg)", 0.5, 3.5, 1.8)

st.divider()

# ======================================
# VÝPOČET
# ======================================

if st.button("Spočítat kalorický plán"):

    if activity_mode == "Paušální faktor aktivity":
        daily_base = bmr * activity_factor
        activity_daily = daily_base - bmr
    else:
        weekly_base = (bmr * 7) + weekly_active_calories
        daily_base = weekly_base / 7
        activity_daily = weekly_active_calories / 7

    tdee = daily_base / 0.90
    tef_daily = tdee * 0.10

    if goal == "Redukce":
        target = tdee - adjustment
    elif goal == "Nárůst":
        target = tdee + adjustment
    else:
        target = tdee

    if target < bmr:
        st.error("Nelze nastavit příjem pod hodnotu BMR.")
        st.stop()

    weekly_energy_change = adjustment * 7 if goal != "Udržování" else 0
    predicted_weight_change = weekly_energy_change / 7700
    weekly_percent_weight_change = (predicted_weight_change / weight) * 100

    if goal != "Udržování" and weekly_percent_weight_change > 1:
        st.warning("Změna přesahuje 1 % tělesné hmotnosti týdně.")

    fat_kcal = target * 0.30
    fat_g = fat_kcal / 9

    protein_g = weight * protein_per_kg
    protein_kcal = protein_g * 4

    remaining_kcal = target - (fat_kcal + protein_kcal)

    if remaining_kcal < 0:
        st.error("Příliš vysoké množství bílkovin.")
        st.stop()

    carbs_g = remaining_kcal / 4

    st.subheader("Rozpad energetického výdeje")
    st.write(f"BMR: {bmr:.0f} kcal")
    st.write(f"Aktivita: {activity_daily:.0f} kcal")
    st.write(f"TEF (10 %): {tef_daily:.0f} kcal")
    st.write(f"Celkový TDEE: {tdee:.0f} kcal")

    st.divider()

    st.subheader("Výsledky")
    st.write(f"Doporučený denní příjem: {target:.0f} kcal")

    if goal != "Udržování":
        st.write(f"Odhad změny hmotnosti: {predicted_weight_change:.2f} kg / týden")
        st.write(f"{weekly_percent_weight_change:.2f} % tělesné hmotnosti týdně")

    st.divider()

    st.subheader("Makroživiny")
    st.write(f"Bílkoviny: {protein_g:.0f} g")
    st.write(f"Tuky: {fat_g:.0f} g")
    st.write(f"Sacharidy: {carbs_g:.0f} g")

    st.divider()

    st.subheader("Odborná analýza")

    if goal != "Udržování":
        percent_deficit = (adjustment / tdee) * 100 if tdee != 0 else 0
        st.write(f"Procentuální změna: {percent_deficit:.1f} % z TDEE")

        if percent_deficit <= 15:
            st.success("Jedná se o mírnou a dlouhodobě udržitelnou redukci.")
        elif percent_deficit <= 25:
            st.warning("Jedná se o standardní redukční nastavení.")
        else:
            st.error("Jedná se o agresivní redukci – zvažte úpravu.")

    st.divider()

    st.subheader("Jak číst tento výsledek")

    st.markdown("""
**BMR (Bazální metabolismus)**  
Energie potřebná pro základní životní funkce v klidu.

**TDEE (Celkový denní výdej energie)**  
Součet BMR, fyzické aktivity a energie potřebné na trávení (TEF).

**TEF (Thermic Effect of Food)**  
Přibližně 10 % denního energetického výdeje.

**Makroživiny**
- Bílkoviny pomáhají udržet svalovou hmotu.
- Tuky jsou fixně nastaveny na 30 %.
- Sacharidy doplňují zbytek energie.

Dlouhodobá redukce by neměla přesahovat 1 % tělesné hmotnosti týdně.
""")