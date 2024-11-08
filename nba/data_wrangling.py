import pandas as pd
import numpy as np
from pathlib import Path
import sqlite3 as sql

# Set the data path (adjust if necessary)
DATA_PATH = Path.cwd() / "data" / "nba.sqlite"


# Data loading function for insights 1 & 2
def load_data(table_name: str) -> pd.DataFrame:
    """Load data from the specified SQLite table"""
    con = sql.connect(DATA_PATH)  # connect to the database
    query = """
    SELECT *
    FROM draft_combine_stats
    """
    df = pd.read_sql(query, con)
    con.close()
    return df


# Data loading function for insight 3
def load_data_draft(table_name: str) -> pd.DataFrame:
    """Load data from the specified SQLite table"""
    con = sql.connect(DATA_PATH)  # connect to the database
    query = """
    SELECT *
    FROM draft_history
    """
    df_draft = pd.read_sql(query, con)
    con.close()
    return df_draft


# Data loading function for insight 4
def load_data_team(table_name: str) -> pd.DataFrame:
    """Load data from the specified SQLite table"""
    con = sql.connect(DATA_PATH)  # connect to the database
    query = """
    SELECT *
    FROM team_history
    """
    df_team = pd.read_sql(query, con)
    con.close()
    return df_team


# Data wrangling functions
def drop_empty_str_row(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return df[df[col] != ""]


def convert_float(df: pd.DataFrame, col_list: list) -> pd.DataFrame:
    for col in col_list:
        df[col] = df[col].replace(["", None], np.nan)
        df[col] = df[col].astype(float)
    return df


def fill_na_with_mean(df: pd.DataFrame, col_list: list) -> pd.DataFrame:
    for col in col_list:
        mean_val = df[col].mean()
        df[col] = df[col].fillna(mean_val)
    return df


def cleanup_position(df: pd.DataFrame) -> pd.DataFrame:
    position_dict = {
        "C-PF": "C-PF",
        "PF-C": "C-PF",
        "PF-SF": "PF-SF",
        "SF-PF": "PF-SF",
        "SG-PG": "PG-SG",
        "PG-SG": "PG-SG",
        "SF-SG": "SG-SF",
        "SG-SF": "SG-SF",
    }
    df["position"] = df["position"].replace(position_dict)
    return df


def groupby_mean(df: pd.DataFrame, groupby_col: str) -> pd.DataFrame:
    return df.groupby(groupby_col, as_index=False).mean()


# Functions for Insight 3
def analyse_draft_picks(df: pd.DataFrame):
    """
    This function categorises draft picks by source (College, High School, Others), and visualises the distribution in a bar chart.
    """

    # Count the number of draft picks by organization type
    draft_counts = df["organization_type"].value_counts()

    # Create categories for College, High School, and Others
    categories = {
        "College": draft_counts.get("College/University", 0),
        "High School": draft_counts.get("High School", 0),
        "Others": draft_counts.sum()
        - draft_counts.get("College/University", 0)
        - draft_counts.get("High School", 0),
    }

    # Convert the dictionary to a DataFrame and sort by the number of College draft picks
    categories_df = pd.DataFrame(
        list(categories.items()), columns=["Category", "Number of Draft Picks"]
    )
    categories_df = categories_df.sort_values(
        by="Number of Draft Picks", ascending=False
    )

    return categories_df


def analyse_franchise_by_city(df: pd.DataFrame):
    """
    This function categorizes draft picks by source (College, High School, Others), and visualises the distribution in a bar chart.
    """
    from datetime import datetime

    # Data Cleaning Adjustments

    # 1. Combine "Minneapolis" and "Minnesota" as "Minnesota"
    df["city"] = df["city"].replace(
        {"Minneapolis": "Minnesota", "Minnesota": "Minnesota"}
    )

    # 2. Remove any blank or missing entries in the 'city' column
    df = df[df["city"].notna() & (df["city"] != "")]

    # 3. Merge "Kansas City-Omaha" and "Kansas City" into "Kansas City"
    df["city"] = df["city"].replace(
        {"Kansas City-Omaha": "Kansas City", "Kansas City": "Kansas City"}
    )

    # 4. Remove "Capital" if it appears in the city names
    df["city"] = df["city"].str.replace("Capital", "", regex=False).str.strip()

    # Convert 'year_founded' and 'year_active_till' to datetime
    df["year_founded"] = pd.to_datetime(df["year_founded"], format="%Y")
    df["year_active_till"] = pd.to_datetime(
        df["year_active_till"], format="%Y", errors="coerce"
    )

    # Fill any missing 'year_active_till' values with the current year (assuming these teams are still active)
    current_year = datetime.now().year
    df["year_active_till"] = df["year_active_till"].fillna(
        pd.Timestamp(current_year)
    )

    # Calculate the number of years each team has been in its city
    df["years_in_city"] = (
        df["year_active_till"].dt.year - df["year_founded"].dt.year
    ).astype(int)

    # Aggregate years by city (regardless of franchise name) and sort by total years in descending order
    df = df.groupby("city")["years_in_city"].sum().reset_index()
    df = df.sort_values(by="years_in_city", ascending=False)

    return df
