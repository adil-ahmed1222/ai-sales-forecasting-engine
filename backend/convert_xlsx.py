"""Utility to convert an Excel file to CSV for the project.

Usage:
    python backend/convert_xlsx.py [path/to/Book1.xlsx] [backend/demo_sales.csv]

If no arguments are provided it looks for `Book1.xlsx` in the workspace root
and writes `backend/demo_sales.csv`.
"""
from __future__ import annotations
import sys
import os
import pandas as pd


def convert_xlsx_to_csv(xlsx_path: str, out_csv: str) -> None:
    if not os.path.exists(xlsx_path):
        raise FileNotFoundError(f"Excel file not found: {xlsx_path}")

    df = pd.read_excel(xlsx_path, sheet_name=0, engine='openpyxl')

    # Normalize column names and ensure required columns exist
    cols_lc = {c.lower(): c for c in df.columns}
    if 'date' not in cols_lc or 'revenue' not in cols_lc:
        raise ValueError("Excel must contain 'date' and 'revenue' columns (case-insensitive)")

    date_col = cols_lc['date']
    rev_col = cols_lc['revenue']

    df = df[[date_col, rev_col]].rename(columns={date_col: 'date', rev_col: 'revenue'})
    df['date'] = pd.to_datetime(df['date'])

    out_dir = os.path.dirname(out_csv)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    df.to_csv(out_csv, index=False)
    print(f"Converted {xlsx_path} -> {out_csv} ({len(df)} rows)")


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'Book1.xlsx'
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), 'demo_sales.csv')
    try:
        convert_xlsx_to_csv(src, dst)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)