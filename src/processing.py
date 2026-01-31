"""
Data processing helpers for the Flight Delay Explorer Streamlit app.

This module centralizes common dataframe operations:
- listing airports and airlines
- filtering an airport+airline duo
- computing KPI metrics
- aggregating delay causes for charts
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import logging
import math

import pandas as pd

LOGGER = logging.getLogger(__name__)

CAUSE_MAP: Dict[str, Tuple[Dict[str, str], str]] = {
    "Counts (flights)": (
        {
            "Airline issues": "carrier_ct",
            "Weather": "weather_ct",
            "Air traffic / NAS": "nas_ct",
            "Security": "security_ct",
            "Late inbound aircraft": "late_aircraft_ct",
        },
        "Count",
    ),
    "Minutes": (
        {
            "Airline issues": "carrier_delay",
            "Weather": "weather_delay",
            "Air traffic / NAS": "nas_delay",
            "Security": "security_delay",
            "Late inbound aircraft": "late_aircraft_delay",
        },
        "Minutes",
    ),
}


def get_airports(df: pd.DataFrame) -> List[str]:
    """
    Return a sorted list of unique airport codes present in the dataset.

    Args:
        df: Input dataframe containing an 'airport' column.

    Returns:
        A sorted list of airport codes (strings). Missing values are excluded.
    """
    if "airport" not in df.columns:
        LOGGER.warning("Column 'airport' not found in dataframe.")
        return []

    airports = sorted(df["airport"].dropna().unique().tolist())
    LOGGER.debug("Found %d airports.", len(airports))
    return airports


def get_airlines_for_airport(df: pd.DataFrame, airport: str) -> List[str]:
    """
    Return a sorted list of airlines operating at the given airport.

    Args:
        df: Input dataframe containing 'airport' and 'carrier_name' columns.
        airport: Airport code to filter by.

    Returns:
        A sorted list of airline names (strings). Missing values are excluded.
    """
    required_cols = {"airport", "carrier_name"}
    missing = required_cols.difference(df.columns)
    if missing:
        LOGGER.warning("Missing required columns for airlines lookup: %s", sorted(missing))
        return []

    mask = df["airport"] == airport
    airlines = sorted(df.loc[mask, "carrier_name"].dropna().unique().tolist())
    LOGGER.debug("Found %d airlines for airport '%s'.", len(airlines), airport)
    return airlines


def filter_duo(df: pd.DataFrame, airport: str, airline: str) -> pd.DataFrame:
    """
    Filter the dataset to a specific (airport, airline) duo.

    Args:
        df: Input dataframe containing 'airport' and 'carrier_name' columns.
        airport: Airport code to filter by.
        airline: Airline name to filter by.

    Returns:
        A filtered dataframe containing only rows matching the duo.
        If required columns are missing, an empty dataframe is returned.
    """
    required_cols = {"airport", "carrier_name"}
    missing = required_cols.difference(df.columns)
    if missing:
        LOGGER.warning("Missing required columns for duo filter: %s", sorted(missing))
        return df.iloc[0:0].copy()

    filtered = df[(df["airport"] == airport) & (df["carrier_name"] == airline)]
    LOGGER.debug(
        "Filtered to duo airport='%s', airline='%s': %d rows.",
        airport,
        airline,
        len(filtered),
    )
    return filtered


def compute_kpis(filtered: pd.DataFrame) -> Dict[str, float]:
    """
    Compute KPI values for a filtered dataset.

    KPIs:
    - total_flights: sum of 'arr_flights'
    - total_delays: sum of 'arr_del15'
    - delay_rate: total_delays / total_flights (NaN if total_flights == 0)

    Args:
        filtered: Dataframe for a selected airport+airline duo.

    Returns:
        A dict with keys: 'total_flights', 'total_delays', 'delay_rate'.
        Values are floats. 'delay_rate' may be NaN if total_flights is 0.
    """
    required_cols = {"arr_flights", "arr_del15"}
    missing = required_cols.difference(filtered.columns)
    if missing:
        LOGGER.warning("Missing required columns for KPI computation: %s", sorted(missing))
        return {"total_flights": 0.0, "total_delays": 0.0, "delay_rate": math.nan}

    total_flights = float(filtered["arr_flights"].sum())
    total_delays = float(filtered["arr_del15"].sum())
    delay_rate = (total_delays / total_flights) if total_flights else math.nan

    LOGGER.debug(
        "KPIs computed: total_flights=%.0f, total_delays=%.0f, delay_rate=%s",
        total_flights,
        total_delays,
        f"{delay_rate:.4f}" if not math.isnan(delay_rate) else "nan",
    )

    return {
        "total_flights": total_flights,
        "total_delays": total_delays,
        "delay_rate": delay_rate,
    }


def compute_causes(filtered: pd.DataFrame, metric_choice: str) -> Tuple[pd.DataFrame, str]:
    """
    Aggregate delay causes for a filtered dataset.

    The function maps a user-facing metric choice to the corresponding columns
    and returns a dataframe in the form:
        Cause | <value_label>

    Args:
        filtered: Dataframe for a selected airport+airline duo.
        metric_choice: Either "Counts (flights)" or "Minutes".

    Returns:
        A tuple (causes_df, value_label) where:
          - causes_df: dataframe with columns ["Cause", value_label], sorted desc
          - value_label: "Count" or "Minutes"

    Raises:
        ValueError: if metric_choice is not a supported key in CAUSE_MAP.
    """
    if metric_choice not in CAUSE_MAP:
        LOGGER.error("Unsupported metric_choice: '%s'. Supported: %s", metric_choice, list(CAUSE_MAP))
        raise ValueError(f"Unsupported metric_choice: {metric_choice!r}")

    cause_cols, value_label = CAUSE_MAP[metric_choice]

    rows: List[Dict[str, float | str]] = []
    for label, col in cause_cols.items():
        if col not in filtered.columns:
            LOGGER.debug("Cause column missing, skipping: %s (%s)", label, col)
            continue

        value = float(filtered[col].fillna(0).sum())
        rows.append({"Cause": label, value_label: value})

    causes_df = (
        pd.DataFrame(rows)
        .sort_values(value_label, ascending=False)
        .reset_index(drop=True)
    )

    LOGGER.debug(
        "Computed causes for metric '%s': %d rows.",
        metric_choice,
        len(causes_df),
    )
    return causes_df, value_label