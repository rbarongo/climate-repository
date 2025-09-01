import pandas as pd


def stringify_currency(x):
    return f"{x:,.0f}" if pd.notnull(x) else ""


def edit_coords(x):
    return x.replace('(', '')


