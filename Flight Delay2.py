import pandas as pd
import streamlit as st
from src.load_data import load_dataset

st.set_page_config(page_title="Flight Delay Explorer", layout="wide")

# ---- Simple styling ----
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, rgba(245,247,255,1) 0%, rgba(255,255,255,1) 35%, rgba(245,250,255,1) 100%);
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid rgba(0,0,0,0.06);
        padding: 14px 16px;
        border-radius: 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner="Loading dataset...")
def get_data():
    return load_dataset()

df = get_data()

st.title("Flight Delay Explorer")

st.caption("Select an airport + airline to explore delay rate and delay causes.")

# ---- Sidebar controls ----
st.sidebar.header("Filters")

airports = sorted(df["airport"].dropna().unique())
selected_airport = st.sidebar.selectbox("Airport", airports, key="airport_select")

airlines_for_airport = sorted(
    df.loc[df["airport"] == selected_airport, "carrier_name"].dropna().unique()
)
selected_airline = st.sidebar.selectbox("Airline", airlines_for_airport, key="airline_select")

metric_choice = st.sidebar.radio(
    "Cause metric",
    ["Counts (flights)", "Minutes"],
    horizontal=False,
    key="cause_metric_choice",
)

# ---- Filter  ----
filtered = df[
    (df["airport"] == selected_airport) &
    (df["carrier_name"] == selected_airline)
]

if filtered.empty:
    st.warning("No data available for this airport–airline combination.")
    st.stop()

# ---- KPIs row ----
total_flights = filtered["arr_flights"].sum()
total_delays = filtered["arr_del15"].sum()
delay_rate = (total_delays / total_flights) if total_flights else float("nan")

k1, k2, k3 = st.columns(3)
k1.metric("Delay rate (≥15 min)", f"{delay_rate:.2%}" if total_flights else "—")
k2.metric("Total flights", f"{int(total_flights):,}")
k3.metric("Delayed flights", f"{int(total_delays):,}")

st.divider()

# ---- Cause aggregation ----
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

data = []
for label, col in cause_cols.items():
    if col in filtered.columns:
        data.append({"Cause": label, value_label: float(filtered[col].fillna(0).sum())})

causes_df = pd.DataFrame(data).sort_values(value_label, ascending=False).reset_index(drop=True)

# ---- Chart/table toggle ----
if "show_table" not in st.session_state:
    st.session_state.show_table = False

top_left, top_right = st.columns([3, 1])
with top_left:
    st.subheader("See the main causes for delays")
    st.caption("Aggregated across the selected airport + airline.")

with top_right:
    toggle_label = "📋 Table" if not st.session_state.show_table else "📊 Chart"
    if st.button(f"Switch to {toggle_label}", use_container_width=True):
        st.session_state.show_table = not st.session_state.show_table


import altair as alt
import time

BAR_COLOR = "#14b8a6"

def make_bar_chart(df_):
    return (
        alt.Chart(df_)
        .mark_bar(
            color=BAR_COLOR,
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6,
        )
        .encode(
            x=alt.X(
                f"{value_label}:Q",
                title=value_label,
                axis=alt.Axis(labelFlush=False),
            ),
            y=alt.Y(
                "Cause:N",
                sort="-x",
                title=None,
                axis=alt.Axis(
                    labelLimit=300,     # allow long labels
                    labelFontSize=12,   # readable but compact
                ),
            ),
            tooltip=[
                "Cause:N",
                alt.Tooltip(f"{value_label}:Q", format=",.0f"),
            ],
        )
        .properties(
            height=260,   # 👈 key: controls vertical spacing
        )
    )

# ---- Animated render ----
animate = st.sidebar.checkbox("Animate bars", value=True)

placeholder = st.empty()

if animate:
    steps = 18         
    duration = 0.6     
    for i in range(1, steps + 1):
        t = i / steps
        anim_df = causes_df.copy()
        anim_df[value_label] = anim_df[value_label] * t
        placeholder.altair_chart(make_bar_chart(anim_df), use_container_width=True)
        time.sleep(duration / steps)
else:
    placeholder.altair_chart(make_bar_chart(causes_df), use_container_width=True)


