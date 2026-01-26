import streamlit as st
from src.load_data import load_dataset

@st.cache_data(show_spinner="Loading dataset...")
def get_data():
    return load_dataset()

st.title("Flight Delay App – Test")

# Load data
df = load_dataset()

st.write("Dataset loaded:")
st.write(df.head())

# Simple test graph: delays per airport
st.subheader("Total delays per airport")

agg = (
    df.groupby("airport")[["arr_del15", "arr_flights"]]
    .sum()
    .reset_index()
)

agg["delay_rate"] = agg["arr_del15"] / agg["arr_flights"]

# Just take top 10 airports by traffic
top = agg.sort_values("arr_flights", ascending=False).head(10)

st.bar_chart(
    data=top.set_index("airport")["delay_rate"]
)