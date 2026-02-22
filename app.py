import streamlit as st
from datetime import datetime
import os

# ======================================
# Nastavení stránky + vizuální styl
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
# Branding + Logo
# ======================================

col1, col2 = st.columns([3, 2])

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
    selected_activity = st.selectbox("Faktor aktivity", list(activity_options.keys()))
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

    change_4_weeks = predicted_weight_change * 4
    change_12_weeks = predicted_weight_change * 12

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
        st.write(f"Odhad za 4 týdny: {change_4_weeks:.2f} kg")
        st.write(f"Odhad za 12 týdnů: {change_12_weeks:.2f} kg")

    st.divider()

    st.subheader("Makroživiny")

    fat_kcal = target * 0.30
    fat_g = fat_kcal / 9

    protein_g = weight * protein_per_kg
    protein_kcal = protein_g * 4

    remaining_kcal = target - (fat_kcal + protein_kcal)

    if remaining_kcal < 0:
        st.error("Příliš vysoké množství bílkovin.")
        st.stop()

    carbs_g = remaining_kcal / 4

    sugar_max_g = carbs_g * 0.10

    # OPRAVA NMK – 10 % z celkového příjmu
    saturated_fat_max_kcal = target * 0.10
    saturated_fat_max_g = saturated_fat_max_kcal / 9

    st.write(f"Bílkoviny: {protein_g:.0f} g")
    st.write(f"Tuky: {fat_g:.0f} g")
    st.write(f"Sacharidy: {carbs_g:.0f} g")

    st.divider()

    st.write(f"Cukry (maximální hodnota): {sugar_max_g:.0f} g")
    st.write(f"Nasycené mastné kyseliny (maximální hodnota): {saturated_fat_max_g:.0f} g")
    st.write("Vláknina: 25–35 g denně")

    st.divider()

    st.subheader("Motivační shrnutí")

    st.markdown("""
Tento plán představuje realistický a dlouhodobě udržitelný přístup.  
Klíčem k úspěchu je konzistence, pravidelnost a postupná adaptace organismu.  

Pamatujte: malé kroky prováděné dlouhodobě vedou k velkým výsledkům.
""")

    st.info("Tato kalkulačka je orientační nástroj. Individuální plán zohledňuje zdravotní stav, historii diety a metabolickou adaptaci.")

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

    if submitted:
        if name and email:
            import smtplib
            from email.mime.text import MIMEText

            try:
                sender = st.secrets["EMAIL_ADDRESS"]
                password = st.secrets["EMAIL_PASSWORD"]

                message = f"""
Nová poptávka z Nutriční kalkulačky

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

            except Exception:
                st.error("Došlo k chybě při odesílání.")

        else:
            st.warning("Vyplňte prosím jméno a email.")

st.caption("Odesláním formuláře souhlasíte se zpracováním osobních údajů za účelem kontaktování.")