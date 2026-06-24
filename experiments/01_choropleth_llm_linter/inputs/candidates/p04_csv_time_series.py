#!/usr/bin/env python3
"""Candidate for P04: annual burned area and fire-count plot."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_DIR = Path(os.environ["CHOROPLETH_DATA_DIR"])
OUT_DIR = Path(os.environ["CHOROPLETH_OUTPUT_DIR"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_DIR / "MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv")
    max_row = df.loc[df["Burned Area [ha]"].idxmax()]
    print(f"max_burned_area_year={int(max_row['Year'])}")
    print(f"max_burned_area_ha={float(max_row['Burned Area [ha]']):.2f}")

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax1.plot(df["Year"], df["Burned Area [ha]"], color="#c23b22", marker="o", label="Burned area [ha]")
    ax1.set_ylabel("Burned area [ha]", color="#c23b22")
    ax1.tick_params(axis="y", labelcolor="#c23b22")
    ax2 = ax1.twinx()
    ax2.plot(df["Year"], df["Number of Fires"], color="#2f6f9f", marker="s", label="Number of fires")
    ax2.set_ylabel("Number of fires", color="#2f6f9f")
    ax2.tick_params(axis="y", labelcolor="#2f6f9f")
    ax1.set_xlabel("Year")
    ax1.set_title("Portugal Annual Burned Area and Number of Fires, 2002-2022")
    ax1.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "time_series.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()

