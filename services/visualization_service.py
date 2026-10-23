"""Visualization service — Matplotlib + Seaborn charts, returned as figures."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid", palette="muted")
PALETTE = sns.color_palette("muted")


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "", horizontal: bool = False) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    data = df.sort_values(y, ascending=horizontal)
    if horizontal:
        sns.barplot(data=data, x=y, y=x, ax=ax, palette=PALETTE, hue=x, legend=False)
        ax.set_xlabel(y)
        ax.set_ylabel(x)
    else:
        sns.barplot(data=data, x=x, y=y, ax=ax, palette=PALETTE, hue=x, legend=False)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.lineplot(data=df, x=x, y=y, ax=ax, marker="o", linewidth=2, color=PALETTE[0])
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    return fig


def pie_chart(df: pd.DataFrame, names: str, values: str, title: str = "") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(df[values], labels=df[names], autopct="%1.1f%%", startangle=90,
           colors=PALETTE, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    return fig


def histogram(series: pd.Series, title: str = "", bins: int = 25) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(series.dropna(), bins=bins, kde=True, ax=ax, color=PALETTE[0])
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    return fig


def scatter_plot(df: pd.DataFrame, x: str, y: str, hue: str | None = None, title: str = "") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax, palette=PALETTE)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    return fig


def box_plot(df: pd.DataFrame, x: str, y: str, title: str = "") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.boxplot(data=df, x=x, y=y, ax=ax, palette=PALETTE, hue=x, legend=False)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    return fig


def heatmap(corr: pd.DataFrame, title: str = "Correlation Heatmap") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, fmt=".2f",
                square=True, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    return fig