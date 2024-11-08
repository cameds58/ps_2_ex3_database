import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Bar plot for position metrics
def bar_plot_position(df: pd.DataFrame, metrics: list) -> None:
    for metric in metrics:
        sorted_df = df.sort_values(by=metric, ascending=False)
        plt.figure(figsize=(6, 2))
        plt.bar(sorted_df["position"], sorted_df[metric])
        plt.xlabel("Position")
        plt.title(f"{metric} by Position")
        plt.xticks(rotation=45)
        plt.show()


# Radar plot for position athletic performance
def radar_plot_position(df: pd.DataFrame) -> None:
    df = df[df["position"].isin(["SG", "PG", "SF", "PF", "C"])]
    min_leap, max_leap = (
        df["max_vertical_leap"].min(),
        df["max_vertical_leap"].max(),
    )
    min_agility, max_agility = (
        df["lane_agility_time"].min(),
        df["lane_agility_time"].max(),
    )
    min_press, max_press = df["bench_press"].min(), df["bench_press"].max()

    df_normalized = df.copy()
    df_normalized["explosive_power"] = df["max_vertical_leap"].apply(
        lambda x: (x - min_leap) / (max_leap - min_leap)
    )
    df_normalized["speed"] = df["lane_agility_time"].apply(
        lambda x: (1 / x - 1 / max_agility)
        / (1 / min_agility - 1 / max_agility)
    )
    df_normalized["endurance"] = df["bench_press"].apply(
        lambda x: (x - min_press) / (max_press - min_press)
    )

    for _, row in df_normalized.iterrows():
        values = row[["explosive_power", "speed", "endurance"]].values.tolist()
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, 3, endpoint=False).tolist() + [0]
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color="skyblue", alpha=0.25)
        ax.plot(angles, values, color="blue", linewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(
            ["Explosive Power", "Speed", "Endurance"], fontsize=10
        )
        ax.set_title(
            f"{row['position']} Profile", size=15, color="blue", y=1.1
        )
        plt.show()


# Visualization for Insight 3: Draft pick distribution
def plot_draft_pick_distribution(df: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    plt.bar(
        df["Category"],
        df["Number of Draft Picks"],
        color=["blue", "green", "red"],
    )
    plt.xlabel("Category")
    plt.ylabel("Number of Draft Picks")
    plt.title("Number of Draft Picks by Category")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# Visualization for Insight 4: Franchise stability
def plot_franchise_stability(df: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 8))
    plt.barh(df["city"], df["years_in_city"], color="skyblue")
    plt.xlabel("Total Years as Host City")
    plt.ylabel("City")
    plt.title("Total Years Each City Has Hosted an NBA Franchise")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
