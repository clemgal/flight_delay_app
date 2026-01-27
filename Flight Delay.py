import pandas as pd
import streamlit as st
from src.load_data import load_dataset

st.set_page_config(page_title="Flight Delay Explorer", layout="centered")

@st.cache_data(show_spinner="Loading dataset...")
def get_data():
    return load_dataset()

df = get_data()

st.title("Flight Delay Explorer")

# --- Dropdowns (Airport then Airline depends on Airport) ---
airports = sorted(df["airport"].dropna().unique())
selected_airport = st.selectbox("Select an airport", airports, key="airport_select")

airlines_for_airport = sorted(
    df.loc[df["airport"] == selected_airport, "carrier_name"].dropna().unique()
)
selected_airline = st.selectbox(
    "Select an airline", airlines_for_airport, key="airline_select"
)

# --- Filter with AND logic ---
filtered = df[
    (df["airport"] == selected_airport) &
    (df["carrier_name"] == selected_airline)
]

if filtered.empty:
    st.warning("No data available for this airport–airline combination.")
    st.stop()

# --- Delay-rate metric (>=15 min) ---
total_flights = filtered["arr_flights"].sum()
total_delays = filtered["arr_del15"].sum()

if total_flights == 0:
    st.warning("No flights recorded for this selection.")
    st.stop()

delay_rate = total_delays / total_flights
st.metric("Delay rate (≥15 min)", f"{delay_rate:.2%}")

st.divider()

# --- Radio to choose measure: counts vs minutes ---
metric_choice = st.radio(
    "Delay causes measured by",
    ["Counts (flights)", "Minutes"],
    horizontal=True,
    key="cause_metric_choice",
)

# Map display labels -> df column names, depending on metric
if metric_choice == "Counts (flights)":
    cause_cols = {
        "Airline issues": "carrier_ct",
        "Weather": "weather_ct",
        "Air traffic / NAS": "nas_ct",
        "Security": "security_ct",
        "Late inbound aircraft": "late_aircraft_ct",
    }
    value_label = "Count"
else:
    cause_cols = {
        "Airline issues": "carrier_delay",
        "Weather": "weather_delay",
        "Air traffic / NAS": "nas_delay",
        "Security": "security_delay",
        "Late inbound aircraft": "late_aircraft_delay",
    }
    value_label = "Minutes"

# Build the cause summary table (always)
data = []
missing_cols = []
for label, col in cause_cols.items():
    if col not in filtered.columns:
        missing_cols.append(col)
        continue
    data.append({"Cause": label, value_label: float(filtered[col].fillna(0).sum())})

if missing_cols:
    st.info(f"Some expected columns were not found and were skipped: {missing_cols}")

causes_df = (
    pd.DataFrame(data)
    .sort_values(value_label, ascending=False)
    .reset_index(drop=True)
)

st.subheader("Most common delay causes")

if causes_df.empty or causes_df[value_label].sum() == 0:
    st.info("No delay-cause data available for this selection.")
    st.stop()

# --- Toggle between chart and table ---
if "show_table" not in st.session_state:
    st.session_state.show_table = False

btn_label = "Show data table" if not st.session_state.show_table else "Show bar chart"
if st.button(btn_label, key="toggle_chart_table"):
    st.session_state.show_table = not st.session_state.show_table

if st.session_state.show_table:
    st.dataframe(causes_df, use_container_width=True)
else:
    st.bar_chart(causes_df.set_index("Cause")[value_label])
