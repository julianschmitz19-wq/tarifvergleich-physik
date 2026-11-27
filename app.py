import streamlit as st
import pandas as pd

# --- Seiten-Konfiguration ---
st.set_page_config(
    page_title="Annas erste eigene Wohnung", page_icon="🏠", layout="wide"
)

# --- vordefinierte Geräte (QoL-Feature: Presets) ---
PRESETS = {
    "Individuell (Leeres Gerät)": {"power": 100, "hours": 1.0},
    "WLAN-Router": {"power": 15, "hours": 24.0},
    "Wasserkocher": {"power": 2000, "hours": 0.3},
    "Spülmaschine": {"power": 1200, "hours": 1.5},
    "Staubsauger": {"power": 800, "hours": 0.5},
    "Föhn": {"power": 1800, "hours": 0.2},
    "PC mit Monitor": {"power": 300, "hours": 5.0},
}

# --- Session State für Geräte initialisieren ---
if "devices" not in st.session_state:
    st.session_state.devices = [
        {"id": 1, "name": "Kühlschrank", "power": 40, "hours": 24.0, "active": True},
        {"id": 2, "name": "Fernseher", "power": 100, "hours": 4.0, "active": True},
        {"id": 3, "name": "Laptop", "power": 50, "hours": 6.0, "active": True},
        {"id": 4, "name": "Waschmaschine", "power": 2000, "hours": 0.5, "active": True},
    ]
    st.session_state.next_id = 5


# --- Hilfsfunktionen für Buttons ---
def add_device(preset_name):
    # Fügt ein neues Gerät basierend auf der Auswahl im Dropdown hinzu
    preset_data = PRESETS[preset_name]
    st.session_state.devices.append(
        {
            "id": st.session_state.next_id,
            "name": preset_name
            if preset_name != "Individuell (Leeres Gerät)"
            else "Neues Gerät",
            "power": preset_data["power"],
            "hours": preset_data["hours"],
            "active": True,
        }
    )
    st.session_state.next_id += 1


def delete_device(device_id):
    # Filtert die Liste neu und wirft das Gerät mit der passenden ID heraus
    st.session_state.devices = [
        d for d in st.session_state.devices if d["id"] != device_id
    ]


# ==========================================
# 1. TARIFMODELLE (Jetzt in der Seitenleiste)
# ==========================================
with st.sidebar:
    st.header("⚙️ Tarifmodelle")
    st.write("Passe hier die Vertragsdaten an.")

    st.subheader("🔵 Tarif A (Stadtwerke)")
    gp_a = st.number_input("Grundpreis (€/Monat)", value=9.50, step=0.50, key="gp_a")
    ap_a = st.number_input("Arbeitspreis (€/kWh)", value=0.42, step=0.01, key="ap_a")

    st.divider()

    st.subheader("🟢 Tarif B (Eco-Flat)")
    gp_b = st.number_input("Grundpreis (€/Monat)", value=16.00, step=0.50, key="gp_b")
    ap_b = st.number_input("Arbeitspreis (€/kWh)", value=0.28, step=0.01, key="ap_b")

# Wir ermitteln hier schon den aktuell günstigeren Arbeitspreis für die Vorschau pro Gerät
aktueller_ap = ap_a if ap_a < ap_b else ap_b


# ==========================================
# 2. HAUPTFENSTER: GERÄTE-VERWALTUNG
# ==========================================
st.title("🏠 Stromtarif-Vergleich")
st.markdown(
    "**Annas erste eigene Wohnung** – Finde heraus, was deine Geräte wirklich kosten!"
)

st.header("🔌 Deine Geräte")

# QoL: Preset-Auswahl zum Hinzufügen
col_preset, col_btn = st.columns([3, 2])
with col_preset:
    selected_preset = st.selectbox(
        "Geräte-Vorlage wählen:",
        options=list(PRESETS.keys()),
        label_visibility="collapsed",
    )
with col_btn:
    st.button("➕ Gerät hinzufügen", on_click=add_device, args=(selected_preset,))

st.write("---")

total_kwh_day = 0.0

# QoL: Bessere Spaltenaufteilung für den Löschen-Button
c1, c2, c3, c4, c5, c6 = st.columns([0.5, 2, 3, 3, 2, 0.5])
c1.write("**An**")
c2.write("**Gerät**")
c3.write("**Leistung (W)**")
c4.write("**Laufzeit (h/Tag)**")
c5.write("**Kosten/Jahr**")
c6.write("**Löschen**")

for i, device in enumerate(st.session_state.devices):
    with st.container():
        c1, c2, c3, c4, c5, c6 = st.columns([0.5, 2, 3, 3, 2, 0.5])

        device["active"] = c1.checkbox(
            "Aktiv",
            value=device["active"],
            key=f"active_{device['id']}",
            label_visibility="collapsed",
        )
        device["name"] = c2.text_input(
            "Name",
            value=device["name"],
            key=f"name_{device['id']}",
            label_visibility="collapsed",
        )
        device["power"] = c3.slider(
            "Watt",
            0,
            3000,
            device["power"],
            10,
            key=f"power_{device['id']}",
            label_visibility="collapsed",
        )
        device["hours"] = c4.slider(
            "Stunden",
            0.0,
            24.0,
            device["hours"],
            0.5,
            key=f"hours_{device['id']}",
            label_visibility="collapsed",
        )

        if device["active"]:
            # Berechne kWh und füge sie zur Tagessumme hinzu
            kwh = (device["power"] * device["hours"]) / 1000
            total_kwh_day += kwh

            # QoL: Was kostet dieses eine Gerät im Jahr? (Grobe Schätzung mit dem günstigeren Tarif)
            jahreskosten_geraet = (kwh * 365) * aktueller_ap
            c5.write(f"~ {jahreskosten_geraet:.2f} €")
        else:
            c5.write("0.00 €")

        # QoL: Löschen-Button
        c6.button(
            "🗑️", key=f"del_{device['id']}", on_click=delete_device, args=(device["id"],)
        )

st.divider()

# ==========================================
# 3. AUSWERTUNG & KOSTEN
# ==========================================
st.header("📊 Auswertung & Monatlicher Abschlag")

total_kwh_year = total_kwh_day * 365
cost_a = (total_kwh_year * ap_a) + (gp_a * 12)
cost_b = (total_kwh_year * ap_b) + (gp_b * 12)

# QoL: Monatliche Kosten berechnen
monthly_a = cost_a / 12
monthly_b = cost_b / 12

col_metrics, col_chart = st.columns([1, 1])

with col_metrics:
    st.metric("Geschätzter Jahresverbrauch", f"{total_kwh_year:.0f} kWh")

    # Empfehlung und monatlicher Abschlag
    if cost_a < cost_b:
        st.success(
            f"**Tarif A (Stadtwerke)** ist günstiger!\n\nAnna spart ca. **{(cost_b - cost_a):.2f} €** im Jahr."
        )
        st.info(f"💡 Empfohlener monatlicher Abschlag: **ca. {monthly_a:.2f} €**")
    elif cost_b < cost_a:
        st.success(
            f"**Tarif B (Eco-Flat)** ist günstiger!\n\nAnna spart ca. **{(cost_a - cost_b):.2f} €** im Jahr."
        )
        st.info(f"💡 Empfohlener monatlicher Abschlag: **ca. {monthly_b:.2f} €**")
    else:
        st.warning("Beide Tarife sind auf den Cent gleich teuer!")
        st.info(f"💡 Empfohlener monatlicher Abschlag: **ca. {monthly_a:.2f} €**")

with col_chart:
    chart_data = pd.DataFrame(
        {"Tarif": ["Tarif A", "Tarif B"], "Jahreskosten (€)": [cost_a, cost_b]}
    )
    st.bar_chart(chart_data.set_index("Tarif"), color="#4CAF50")
