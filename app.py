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