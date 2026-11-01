"""Snowbloom: marketing & promotion studio (Streamlit)."""
import re
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
LEADS = ROOT / "data" / "leads.csv"

st.set_page_config(page_title="Snowbloom", page_icon="🌸", layout="wide")
st.markdown(f"<style>{(ROOT / 'styles' / 'snowbloom.css').read_text()}</style>", unsafe_allow_html=True)

# ---- Brand content: edit these to match your real formulation ----
BRAND = {
    "name": "Snowbloom",
    "tagline": "A brighter-looking glow, one lather at a time.",
    "benefits": [
        ("Radiance-boosting", "Gently cleanses and exfoliates so skin looks fresh and luminous."),
        ("Even-looking tone", "Helps skin look more even with regular daily use."),
        ("Gentle on skin", "pH-friendly, soap-free-feel lather. Patch test before first use."),
    ],
    "ingredients": ["Niacinamide", "Licorice root extract", "Rice water", "Vitamin C", "Glycerin"],
}

# Phrases that regulators (e.g. ASCI / CDSCO in India, FTC elsewhere) often challenge on cosmetics.
RISKY = ["whiten", "fairness", "fair skin", "lighten your skin", "bleach", "cure", "treat acne",
         "permanent", "guaranteed", "100%", "clinically proven", "dermatologist approved", "removes dark spots"]

def check_claims(text: str) -> list[str]:
    return [w for w in RISKY if re.search(re.escape(w), text, re.I)]

TEMPLATES = {
    "Instagram": "{hook}\n\nMeet {name}: {benefit}\n\n✨ {offer}\n\n{cta}\n#Snowbloom #GlowRoutine #SkincareIndia",
    "WhatsApp": "Hi! {hook} {name} is here: {benefit}. {offer}. {cta}",
    "Email subject + preview": "Subject: {hook}\nPreview: {name}, {benefit}. {offer}",
    "Google ad": "{name}: Brighter-Looking Skin\n{benefit}\n{offer}. {cta}",
}
HOOKS = ["Your shower just got a glow-up.", "Soap that treats your skin like skincare.",
         "Fresh, bright, bloom-ready.", "Meet your new morning ritual."]

# ---- Hero ----
st.markdown(f"""
<section class="sb-hero">
  <div>
    <h1>{BRAND['name']}: a brighter-looking glow.</h1>
    <p>{BRAND['tagline']} A brightening soap made for daily use, with ingredients you can pronounce.</p>
    <div class="sb-badges">
      <span class="sb-badge">Niacinamide</span><span class="sb-badge cool">Vitamin C</span>
      <span class="sb-badge">Dermatologically tested*</span><span class="sb-badge cool">Cruelty-free*</span>
    </div>
  </div>
  <div class="sb-soap-wrap"><div class="sb-soap" role="img" aria-label="Snowbloom soap bar"></div></div>
</section>
""", unsafe_allow_html=True)
st.caption("*Only keep badges you can back up with documentation.")
st.write("")

tab_home, tab_studio, tab_offers, tab_calendar, tab_leads = st.tabs(
    ["Why Snowbloom", "Campaign studio", "Offers", "Content calendar", "Join the list"])

# ---- Why Snowbloom ----
with tab_home:
    cols = st.columns(3)
    for col, (title, text) in zip(cols, BRAND["benefits"]):
        col.markdown(f'<div class="sb-card"><h3>{title}</h3><p>{text}</p></div>', unsafe_allow_html=True)
    st.subheader("What's inside")
    st.markdown(" ".join(f'<span class="sb-badge">{i}</span>' for i in BRAND["ingredients"]), unsafe_allow_html=True)

# ---- Campaign studio ----
with tab_studio:
    left, right = st.columns([1, 1])
    with left:
        channel = st.selectbox("Channel", list(TEMPLATES))
        hook = st.selectbox("Hook", HOOKS)
        benefit = st.text_input("Key benefit", "a gentle brightening bar for a fresh, radiant look")
        offer = st.text_input("Offer", "Launch offer: 20% off with code BLOOM20")
        cta = st.text_input("Call to action", "Order today on snowbloom.in")
    caption = TEMPLATES[channel].format(hook=hook, name=BRAND["name"], benefit=benefit, offer=offer, cta=cta)
    caption = st.text_area("Edit your copy", caption, height=210)
    with right:
        st.markdown(f'<div class="sb-post"><div class="sb-post-img">{hook}</div>'
                    f'<div class="sb-post-cap">{caption}</div></div>', unsafe_allow_html=True)
        flags = check_claims(caption)
        if flags:
            st.warning("Claim check: reconsider " + ", ".join(f"“{f}”" for f in flags) +
                       ". Use “brighter-looking” or “radiant” wording and keep claims you can substantiate.")
        else:
            st.success("Claim check: no risky phrases found.")
        st.download_button("Download copy", caption, file_name="snowbloom_copy.txt")

# ---- Offers ----
with tab_offers:
    c1, c2 = st.columns(2)
    code = c1.text_input("Promo code", "BLOOM20")
    pct = c1.slider("Discount %", 5, 50, 20)
    end = c1.date_input("Ends on", date.today() + timedelta(days=14))
    days = max((end - date.today()).days, 0)
    c2.markdown(f'<div class="sb-offer"><b>{pct}% off</b><br>Use code <b style="font-size:1.2rem">{code}</b><br>'
                f'{days} days left</div>', unsafe_allow_html=True)
    price = st.number_input("Price per bar (₹)", 50, 2000, 299)
    qty = st.select_slider("Bundle size", [1, 2, 3, 5], 3)
    st.metric(f"{qty}-bar bundle", f"₹{price * qty * (1 - pct / 100):,.0f}", f"-₹{price * qty * pct / 100:,.0f}")

# ---- Calendar ----
with tab_calendar:
    start = st.date_input("Campaign start", date.today(), key="cal")
    plan = [("Teaser: petal reveal", "Instagram Reel"), ("Founder story", "Instagram Carousel"),
            ("Ingredient spotlight", "Story"), ("Launch offer", "WhatsApp + Email"),
            ("Customer routines (UGC)", "Reel"), ("Last-day reminder", "Story + Email")]
    df = pd.DataFrame([{"Date": start + timedelta(days=2 * i), "Idea": a, "Format": b}
                       for i, (a, b) in enumerate(plan)])
    df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    st.download_button("Download calendar (CSV)", df.to_csv(index=False), "snowbloom_calendar.csv")

# ---- Leads ----
with tab_leads:
    with st.form("lead"):
        name = st.text_input("Name")
        contact = st.text_input("Email or WhatsApp")
        consent = st.checkbox("I agree to receive Snowbloom offers and can opt out anytime.")
        if st.form_submit_button("Get my launch code"):
            if name and contact and consent:
                LEADS.parent.mkdir(exist_ok=True)
                pd.DataFrame([{"date": date.today(), "name": name, "contact": contact}]).to_csv(
                    LEADS, mode="a", header=not LEADS.exists(), index=False)
                st.success(f"Welcome, {name}! Your code is BLOOM20.")
            else:
                st.error("Add your name, contact and tick the consent box.")
    if LEADS.exists():
        st.dataframe(pd.read_csv(LEADS), use_container_width=True)
