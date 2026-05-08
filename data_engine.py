import pandas as pd
import streamlit as st


def format_inr(number):
    """Formats a number as an Indian Rupee string (e.g. 1,23,456)."""
    s, last3 = str(int(number)), ""
    if len(s) > 3:
        last3 = "," + s[-3:]
        s = s[:-3]
        while len(s) > 2:
            last3 = "," + s[-2:] + last3
            s = s[:-2]
        return "₹" + s + last3
    return "₹" + s


@st.cache_data
def load_and_clean_data(df):
    """Validates columns, parses types, and drops malformed rows. Returns (clean_df, status)."""
    try:
        df.columns = df.columns.str.strip().str.lower()
        required_cols = ["customer_id", "invoice_date", "amount"]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return (
                None,
                f"❌ Error: Your CSV is missing these required columns: {', '.join(missing_cols).upper()}",
            )

        if df.empty:
            return None, "❌ Error: The uploaded CSV has columns, but no actual data rows."

        df = df.dropna(subset=["customer_id", "invoice_date", "amount"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce", dayfirst=True)
        df = df.dropna(subset=["amount", "invoice_date"])

        if df.empty:
            return (
                None,
                "❌ Error: We found the columns, but the data inside was invalid "
                "(e.g., text instead of numbers in the Amount column).",
            )

        return df, "Success"

    except Exception as e:
        return None, f"❌ An unexpected error occurred while reading the data: {str(e)}"
