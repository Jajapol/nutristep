import streamlit as st
import pandas as pd
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import tempfile

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

st.title("NutriStep")
st.subheader("Mgr. Jaroslav Přidal")
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
age = st.number_input("Věk", 10, 100, 30)
height = st.number_input("Výška (cm)", 100, 250, 170)
weight = st.number_input("Váha (kg)", 30.0, 300.0, 80.0)

bmr_mode = st.radio("BMR:", ["Ručně", "Vypočítat rovnicí"])

if bmr_mode == "Ručně":
    bmr = st.number_input("BMR (kcal)", 500.0, 4000.0, 1700.0)
else:
    bmr = calculate_bmr(weight, height, age, gender)
    st.write(f"BMR: {bmr:.0f} kcal")

# Správně vyřešený faktor aktivity
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

    daily_base = bmr * activity_factor
    tdee = daily_base / 0.90  # započtení TEF

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

    # Makra
    fat_kcal = target * 0.30
    fat_g = fat_kcal / 9

    protein_g = weight * protein_per_kg
    protein_kcal = protein_g * 4

    remaining_kcal = target - (fat_kcal + protein_kcal)

    if remaining_kcal < 0:
        st.error("Příliš vysoké množství bílkovin pro daný příjem.")
        st.stop()

    carbs_g = remaining_kcal / 4

    # ======================================
    # VÝSTUP
    # ======================================

    st.subheader("Výsledky")
    st.write(f"TDEE: {tdee:.0f} kcal")
    st.write(f"Doporučený příjem: {target:.0f} kcal")

    if goal != "Udržování":
        st.write(f"Odhad změny hmotnosti: {predicted_weight_change:.2f} kg / týden")
        st.write(f"{weekly_percent_weight_change:.2f} % tělesné hmotnosti týdně")

    st.divider()

    st.subheader("Makroživiny")
    st.write(f"Bílkoviny: {protein_g:.0f} g")
    st.write(f"Tuky: {fat_g:.0f} g")
    st.write(f"Sacharidy: {carbs_g:.0f} g")

    # ======================================
    # Interaktivní graf
    # ======================================

    if goal != "Udržování":
        weeks = [0, 1, 2, 3, 4]
        weights = [
            weight + (predicted_weight_change * i if goal == "Nárůst"
                      else -predicted_weight_change * i)
            for i in weeks
        ]

        df = pd.DataFrame({"Týden": weeks, "Hmotnost (kg)": weights})
        fig = px.line(
            df,
            x="Týden",
            y="Hmotnost (kg)",
            markers=True,
            title="Projekce hmotnosti (4 týdny)"
        )
        st.plotly_chart(fig)

    # ======================================
    # PDF Export
    # ======================================

    def create_pdf():
        file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(file.name)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("NutriStep – Výživový report", styles["Heading1"]))
        elements.append(Spacer(1, 0.3 * inch))

        text = f"""
        TDEE: {tdee:.0f} kcal<br/>
        Doporučený příjem: {target:.0f} kcal<br/>
        Odhad změny: {predicted_weight_change:.2f} kg týdně<br/><br/>
        Bílkoviny: {protein_g:.0f} g<br/>
        Tuky: {fat_g:.0f} g<br/>
        Sacharidy: {carbs_g:.0f} g
        """

        elements.append(Paragraph(text, styles["Normal"]))
        doc.build(elements)
        return file.name

    if st.button("Vytvořit PDF report"):
        pdf_file = create_pdf()
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="Stáhnout PDF",
                data=f,
                file_name="nutristep_report.pdf",
                mime="application/pdf"
            )