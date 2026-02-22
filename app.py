import streamlit as st
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

# ======================================
# NASTAVENÍ STRÁNKY
# ======================================

st.set_page_config(page_title="NutriStep", layout="centered")

st.markdown("""
<style>
body {background-color: #F4F6F9;}
h1, h2, h3 {color: #1F2A44;}
.stButton>button {
    background-color: #1F2A44;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    border: none;
}
.stButton>button:hover {background-color: #162033;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ======================================
# BRANDING + LOGO
# ======================================

col1, col2 = st.columns([3,2])

with col1:
    st.title("Nutriční kalkulačka")
    st.subheader("NutriStep - Mgr. Jaroslav Přidal")
    st.markdown("""
**Provozovatel:** NutriStep - Mgr. Jaroslav Přidal  
**IČO:** 24012289  
**Sídlo podnikání:** Budovatelů 173/7, Přerov  
**Telefon:** 773 699 937  
**E-mail:** pridal.jaroslav@icloud.com  
""")

with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=240)

st.caption(f"Aktuální datum: {datetime.now().strftime('%d.%m.%Y')}")

st.markdown("""
*Pomáhám lidem hubnout systematicky, bez extrémních diet a bez jojo efektu.  
Každý plán vychází z individuálního výpočtu.*
""")

st.divider()

# ======================================
# BMR FUNKCE
# ======================================

def calculate_bmr(weight, height, age, gender):
    if gender == "Muž":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

# ======================================
# VSTUPY
# ======================================

gender = st.selectbox("Pohlaví", ["Muž", "Žena"])
age = st.number_input("Věk (roky)", 10, 100, 30)
height = st.number_input("Výška (cm)", 100, 250, 170)
weight = st.number_input("Váha (kg)", 30.0, 300.0, 80.0)

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

activity_mode = st.radio("Způsob zadání aktivity:",
    ["Paušální faktor aktivity", "Ruční zadání aktivních kalorií (7 dní)"])

if activity_mode == "Paušální faktor aktivity":
    activity_options = {
        "Sedavý (1.2)": 1.2,
        "Lehká aktivita (1.375)": 1.375,
        "Střední aktivita (1.55)": 1.55,
        "Vysoká aktivita (1.725)": 1.725
    }
    selected = st.selectbox("Faktor aktivity", list(activity_options.keys()))
    tdee_base = bmr * activity_options[selected]
else:
    weekly_active = st.number_input("Součet aktivních kalorií za 7 dní", 0.0, 30000.0, 2500.0)
    tdee_base = bmr + (weekly_active / 7)

st.divider()

# ======================================
# TĚLESNÉ SLOŽENÍ
# ======================================

st.subheader("Způsob zadání tělesného složení")

body_mode = st.radio("", ["Automatický výpočet tuku", "Zadat % tuku ručně"])

if body_mode == "Zadat % tuku ručně":
    body_fat = st.number_input("Tělesný tuk (%)", 3.0, 60.0, 20.0)
else:
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    gender_val = 1 if gender == "Muž" else 0
    body_fat = (1.20 * bmi) + (0.23 * age) - (10.8 * gender_val) - 5.4

fat_mass = weight * (body_fat / 100)
lean_mass_auto = weight - fat_mass

lbm_mode = st.radio("Beztuková hmota (LBM)",
                    ["Vypočítat automaticky", "Zadat ručně (kg)"])

if lbm_mode == "Zadat ručně (kg)":
    lean_mass = st.number_input("Beztuková hmota (kg)", 20.0, weight, lean_mass_auto)
else:
    lean_mass = lean_mass_auto

muscle_mass = st.number_input("Svalová hmota (kg) – volitelné", 0.0, weight, 0.0)

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

    tef = tdee_base * 0.10
    tdee = tdee_base + tef

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
    weekly_percent_change = (predicted_weight_change / weight) * 100

    if goal != "Udržování" and weekly_percent_change > 1:
        st.warning("Změna přesahuje 1 % tělesné hmotnosti týdně.")

    change_4_weeks = predicted_weight_change * 4
    change_12_weeks = predicted_weight_change * 12
    predicted_fat_change = predicted_weight_change * 0.8

    st.subheader("Rozpad energetického výdeje")
    st.write(f"BMR: {bmr:.0f} kcal")
    st.write(f"TDEE: {tdee:.0f} kcal")
    st.write(f"Doporučený příjem: {target:.0f} kcal")

    if goal != "Udržování":
        st.write(f"Odhad změny hmotnosti / týden: {predicted_weight_change:.2f} kg")
        st.write(f"Odhad za 4 týdny: {change_4_weeks:.2f} kg")
        st.write(f"Odhad za 12 týdnů: {change_12_weeks:.2f} kg")

    st.divider()

    st.subheader("Tělesné složení")
    st.markdown("**Jedná se pouze o orientační výpočet tělesného tuku (pokud nebyl zadán ručně).**")

    st.write(f"Odhad tělesného tuku: {body_fat:.1f} %")
    st.write(f"Tuková hmota: {fat_mass:.1f} kg")
    st.write(f"Beztuková hmota: {lean_mass:.1f} kg")

    if muscle_mass > 0:
        st.write(f"Svalová hmota (zadáno): {muscle_mass:.1f} kg")

    bmr_lbm = 370 + (21.6 * lean_mass)
    ffmi = lean_mass / ((height/100) ** 2)

    st.write(f"BMR dle LBM (bazální metabolismus vypočtený z beztukové hmoty): {bmr_lbm:.0f} kcal")
    st.write(f"FFMI (Fat Free Mass Index – index beztukové hmoty): {ffmi:.1f}")
    st.write(f"Odhad změny tukové hmoty / týden: {predicted_fat_change:.2f} kg")

    st.divider()

    fat_kcal = target * 0.30
    fat_g = fat_kcal / 9
    protein_g = weight * protein_per_kg
    protein_kcal = protein_g * 4
    remaining_kcal = target - (fat_kcal + protein_kcal)

    if remaining_kcal < 0:
        st.error("Příliš vysoké množství bílkovin.")
        st.stop()

    carbs_g = remaining_kcal / 4
    sugar_max = carbs_g * 0.10
    saturated_max = (target * 0.10) / 9

    st.subheader("Makroživiny")
    st.write(f"Bílkoviny: {protein_g:.0f} g")
    st.write(f"Tuky: {fat_g:.0f} g")
    st.write(f"Sacharidy: {carbs_g:.0f} g")
    st.write(f"Cukry (max): {sugar_max:.0f} g")
    st.write(f"Nasycené MK (max 10 % příjmu): {saturated_max:.0f} g")
    st.write("Vláknina: 25–35 g denně")

    st.divider()

    st.subheader("Motivační shrnutí")
    st.markdown("""
Tento plán představuje realistický a dlouhodobě udržitelný přístup.  
Klíčem k úspěchu je konzistence, pravidelnost a dlouhodobá strategie.
""")

    st.info("Tato kalkulačka je orientační nástroj.")

# ======================================
# KONTAKTNÍ FORMULÁŘ
# ======================================

st.divider()
st.subheader("Chcete individuální plán na míru?")
st.write("Zanechte kontakt a ozvu se vám.")

with st.form("contact_form"):
    name = st.text_input("Jméno")
    email = st.text_input("Email")
    phone = st.text_input("Telefon (volitelné)")
    message_text = st.text_area("Vaše zpráva / cíl", height=120)
    submitted = st.form_submit_button("Mám zájem o spolupráci")

    if submitted and name and email:
        try:
            sender = st.secrets["EMAIL_ADDRESS"]
            password = st.secrets["EMAIL_PASSWORD"]

            message = f"""
Nová poptávka z NutriStep

Jméno: {name}
Email: {email}
Telefon: {phone}

Zpráva:
{message_text}
"""

            msg = MIMEText(message)
            msg["Subject"] = "Nová poptávka z NutriStep"
            msg["From"] = sender
            msg["To"] = "pridal.jaroslav@icloud.com"

            server = smtplib.SMTP_SSL("smtp.mail.me.com", 465)
            server.login(sender, password)
            server.sendmail(sender, "pridal.jaroslav@icloud.com", msg.as_string())
            server.quit()

            st.success("Děkuji, brzy se vám ozvu.")
        except:
            st.error("Došlo k chybě při odesílání.")

st.caption("Odesláním formuláře souhlasíte se zpracováním osobních údajů za účelem kontaktování.")