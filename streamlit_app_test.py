"""
Flight Delay Explorer Streamlit app.

This app lets users select an airport + airline duo and explore:
- delay rate and flight KPIs
- delay causes (counts or minutes) with an animated bar chart
"""

from __future__ import annotations

import base64
import logging
import time
from pathlib import Path
from typing import Optional

import altair as alt
import pandas as pd
import streamlit as st

from src.load_data import load_dataset
from src.processing import (
    compute_causes,
    compute_kpis,
    filter_duo,
    get_airlines_for_airport,
    get_airports,
)

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BAR_COLOR = "#2a00e4"


def load_banner_base64(image_path: Path) -> Optional[str]:
    """
    Load an image file and return its base64-encoded contents.

    Args:
        image_path: Path to the banner image file.

    Returns:
        A base64 string if the file exists and is readable; otherwise None.
    """
    if not image_path.exists():
        LOGGER.warning("Banner image not found at: %s", image_path)
        return None

    try:
        data = image_path.read_bytes()
        return base64.b64encode(data).decode("utf-8")
    except OSError:
        LOGGER.exception("Failed to read banner image at: %s", image_path)
        return None


def render_title() -> None:
    """
    Render the app title centered at the top of the page.
    """
    st.markdown(
        """
        <h1 style="text-align: center; margin-bottom: 0.8rem;">
            Flight Delay Explorer
        </h1>
        """,
        unsafe_allow_html=True,
    )


def render_banner(image_b64: Optional[str], height_px: int = 110) -> None:
    """
    Render a compact banner image.

    Args:
        image_b64: Base64-encoded image content (JPEG).
        height_px: Banner height in pixels.
    """
    if not image_b64:
        st.warning("Banner could not be loaded.")
        return

    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: {height_px}px;
            margin-bottom: 1rem;
            border-radius: 14px;
            overflow: hidden;
        ">
            <img src="data:image/jpeg;base64,{image_b64}"
                 style="width:100%; height:100%; object-fit:cover;" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_style() -> None:
    """
    Inject CSS styles for the page background and KPI cards.
    """
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(
                180deg,
                rgba(245,247,255,1) 0%,
                rgba(255,255,255,1) 35%,
                rgba(245,250,255,1) 100%
            );
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
def get_data() -> pd.DataFrame:
    """
    Load and cache the dataset for the Streamlit session.

    Returns:
        The flight delay dataset.
    """
    df = load_dataset()
    LOGGER.info("Dataset loaded with %d rows and %d columns.", len(df), len(df.columns))
    return df


def render_intro_card() -> None:
    """
    Render the short app explanation card.
    """
    st.markdown(
        """
        <div style="
            background: white;
            padding: 18px 22px;
            border-radius: 16px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.06);
            margin-bottom: 1.5rem;
            text-align: center;
        ">
            <h3 style="margin-top:0;"> Wondering if your flight might be delayed?</h3>
            <p style="margin-bottom:0.4rem;">
                Flight Delay Explorer helps you understand how likely your flight is to be delayed.
                By choosing your departure airport and airline, you can explore delay rates, total
                flights, and the main reasons behind delays. Travel smarter, with data on your side.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_help_text() -> None:
    """
    Render helper text in the sidebar below the duo selection.
    """
    st.sidebar.markdown(
        """
        <div style="
            margin-top: 1rem;
            margin-bottom: 1.6rem;
            font-size: 0.85rem;
            color: rgba(0,0,0,0.65);
        ">
            ❓ Unsure about your airport code?<br/>
            Check out the <strong>airport glossary</strong> above.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_selected_duo_badge(selected_airport: str, selected_airline: str) -> None:
    """
    Render a centered badge describing the currently selected airport-airline duo.

    Args:
        selected_airport: The selected airport code.
        selected_airline: The selected airline name.
    """
    st.markdown(
        f"""
        <div style="
            text-align: center;
            margin-bottom: 0.8rem;
            font-size: 1.5rem;
        ">
            <span style="
                background: white;
                padding: 8px 14px;
                border-radius: 999px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.06);
                display: inline-block;
            ">
                You are currently aboard <br/><strong>{selected_airport}</strong>
                <span style="opacity: 0.6;">→</span>
                <strong>{selected_airline}</strong>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_bar_chart(df_: pd.DataFrame, value_label: str) -> alt.Chart:
    """
    Build an Altair horizontal bar chart for the causes dataframe.

    Args:
        df_: Dataframe containing columns: 'Cause' and value_label.
        value_label: The numeric column name to plot ("Count" or "Minutes").

    Returns:
        An Altair chart object.
    """
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
                axis=alt.Axis(labelLimit=300, labelFontSize=12),
            ),
            tooltip=[
                "Cause:N",
                alt.Tooltip(f"{value_label}:Q", format=",.0f"),
            ],
        )
        .properties(height=260)
    )


def render_animated_chart(
    causes_df: pd.DataFrame,
    value_label: str,
    animate: bool,
    steps: int = 18,
    duration: float = 0.6,
) -> None:
    """
    Render the causes chart, optionally with a simple grow animation.

    Args:
        causes_df: Dataframe of aggregated causes.
        value_label: "Count" or "Minutes" column name.
        animate: Whether to animate bars growing from 0 to target values.
        steps: Number of animation steps (higher is smoother).
        duration: Total animation duration (seconds).
    """
    placeholder = st.empty()

    if not animate:
        placeholder.altair_chart(
            make_bar_chart(causes_df, value_label),
            use_container_width=True,
        )
        return

    for i in range(1, steps + 1):
        t = i / steps
        anim_df = causes_df.copy()
        anim_df[value_label] = anim_df[value_label] * t

        placeholder.altair_chart(
            make_bar_chart(anim_df, value_label),
            use_container_width=True,
        )
        time.sleep(duration / steps)


def render_footer() -> None:
    """
    Render a small grey data source footer at the bottom of the page.
    """
    st.markdown(
        """
        <div style="
            margin-top: 2.5rem;
            text-align: center;
            font-size: 0.75rem;
            color: rgba(0, 0, 0, 0.5);
        ">
            Data source: Flight Delay Data (Kaggle - Public Domain)
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """
    Run the Streamlit app.
    """
    st.set_page_config(layout="wide")

    render_title()

    root_dir = Path(__file__).resolve().parent
    banner_path = root_dir / "assets" / "high-flying-plane.jpg"
    banner_b64 = load_banner_base64(banner_path)
    render_banner(banner_b64, height_px=110)

    render_page_style()

    df = get_data()
    render_intro_card()

    st.sidebar.header("Pick your duo")

    airports = get_airports(df)
    selected_airport = st.sidebar.selectbox("Airport", airports, key="airport_select")

    airlines_for_airport = get_airlines_for_airport(df, selected_airport)
    selected_airline = st.sidebar.selectbox(
        "Airline",
        airlines_for_airport,
        key="airline_select",
    )

    render_sidebar_help_text()

    metric_choice = st.sidebar.radio(
        "Cause metric",
        ["Counts (flights)", "Minutes"],
        horizontal=False,
        key="cause_metric_choice",
    )

    filtered = filter_duo(df, selected_airport, selected_airline)
    if filtered.empty:
        st.warning("No data available for this airport–airline combination.")
        LOGGER.info(
            "Empty filtered selection for airport='%s', airline='%s'.",
            selected_airport,
            selected_airline,
        )
        st.stop()

    render_selected_duo_badge(selected_airport, selected_airline)

    kpis = compute_kpis(filtered)

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Delay rate (≥15 min)",
        f"{kpis['delay_rate']:.2%}" if kpis["total_flights"] else "—",
    )
    col2.metric("Total flights", f"{int(kpis['total_flights']):,}")
    col3.metric("Delayed flights", f"{int(kpis['total_delays']):,}")

    st.divider()

    causes_df, value_label = compute_causes(filtered, metric_choice)

    if "show_table" not in st.session_state:
        st.session_state.show_table = False

    left, right = st.columns([3, 1])
    with left:
        st.subheader("See the main causes for delays")
        st.caption("Aggregated across the selected airport + airline.")
    with right:
        toggle_label = "📋 Table" if not st.session_state.show_table else "📊 Chart"
        if st.button(f"Switch to {toggle_label}", use_container_width=True):
            st.session_state.show_table = not st.session_state.show_table

    if causes_df.empty or causes_df[value_label].sum() == 0:
        st.info("No delay-cause data available for this selection.")
        LOGGER.info(
            "No cause data for airport='%s', airline='%s', metric='%s'.",
            selected_airport,
            selected_airline,
            metric_choice,
        )
        st.stop()

    if st.session_state.show_table:
        st.dataframe(causes_df, use_container_width=True, hide_index=True)
        render_footer()
        st.stop()

    animate = st.sidebar.checkbox("Animate bars", value=True)
    render_animated_chart(causes_df, value_label, animate=animate)

    render_footer()


if __name__ == "__main__":
    main()