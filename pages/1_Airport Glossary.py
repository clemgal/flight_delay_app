import streamlit as st
from src.load_data import load_dataset

st.title("Airport glossary")

@st.cache_data
def get_data():
    return load_dataset()

df = get_data()

glossary = (
    df[["airport", "airport_name"]]
    .dropna()
    .drop_duplicates()
    .sort_values("airport")
)

search = st.text_input("Search airport code or name")

if search:
    s = search.lower()
    glossary = glossary[
        glossary["airport"].str.lower().str.contains(s)
        | glossary["airport_name"].str.lower().str.contains(s)
    ]

st.dataframe(glossary, use_container_width=True)
