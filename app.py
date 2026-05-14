from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path("expenses.csv")
CATEGORIES = [
    "Food",
    "Housing",
    "Transport",
    "Utilities",
    "Healthcare",
    "Entertainment",
    "Shopping",
    "Savings",
    "Other",
]
COLUMNS = ["date", "description", "category", "amount", "payment_method", "notes"]


@st.cache_data
def load_expenses() -> pd.DataFrame:
    """Load saved expenses or return an empty expense sheet."""
    if DATA_FILE.exists():
        expenses = pd.read_csv(DATA_FILE)
        for column in COLUMNS:
            if column not in expenses.columns:
                expenses[column] = "" if column != "amount" else 0.0
        expenses = expenses[COLUMNS]
        expenses["amount"] = pd.to_numeric(expenses["amount"], errors="coerce").fillna(0.0)
        return expenses

    return pd.DataFrame(columns=COLUMNS)


def save_expenses(expenses: pd.DataFrame) -> None:
    """Persist expenses to a local CSV file."""
    expenses.to_csv(DATA_FILE, index=False)
    load_expenses.clear()


def add_expense(expense: dict) -> None:
    """Append a new expense row to the sheet."""
    expenses = load_expenses()
    updated_expenses = pd.concat([expenses, pd.DataFrame([expense])], ignore_index=True)
    save_expenses(updated_expenses)


def format_currency(value: float) -> str:
    """Format currency values consistently across the dashboard."""
    return f"${value:,.2f}"


def main() -> None:
    st.set_page_config(page_title="Expense Tracker Sheet", page_icon="💸", layout="wide")

    st.title("💸 Expense Tracker Sheet")
    st.caption("Log daily spending, review category totals, and download your expense sheet.")

    with st.sidebar:
        st.header("Add an expense")
        with st.form("expense_form", clear_on_submit=True):
            expense_date = st.date_input("Date", value=date.today())
            description = st.text_input("Description", placeholder="e.g., Groceries")
            category = st.selectbox("Category", CATEGORIES)
            amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
            payment_method = st.selectbox(
                "Payment method",
                ["Cash", "Debit Card", "Credit Card", "Bank Transfer", "Digital Wallet"],
            )
            notes = st.text_area("Notes", placeholder="Optional details")
            submitted = st.form_submit_button("Save expense", type="primary")

        if submitted:
            if not description.strip():
                st.error("Please add a short description before saving.")
            elif amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                add_expense(
                    {
                        "date": expense_date.isoformat(),
                        "description": description.strip(),
                        "category": category,
                        "amount": amount,
                        "payment_method": payment_method,
                        "notes": notes.strip(),
                    }
                )
                st.success("Expense saved.")

    expenses = load_expenses()

    if expenses.empty:
        st.info("No expenses yet. Use the sidebar form to start building your tracker sheet.")
        return

    expenses["date"] = pd.to_datetime(expenses["date"], errors="coerce")
    expenses = expenses.dropna(subset=["date"]).sort_values("date", ascending=False)

    min_date = expenses["date"].min().date()
    max_date = expenses["date"].max().date()

    st.subheader("Filters")
    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])
    with filter_col1:
        start_date = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
    with filter_col2:
        end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)
    with filter_col3:
        selected_categories = st.multiselect("Categories", CATEGORIES, default=CATEGORIES)

    filtered_expenses = expenses[
        (expenses["date"].dt.date >= start_date)
        & (expenses["date"].dt.date <= end_date)
        & (expenses["category"].isin(selected_categories))
    ]

    total_spent = filtered_expenses["amount"].sum()
    average_spend = filtered_expenses["amount"].mean() if not filtered_expenses.empty else 0
    top_category = (
        filtered_expenses.groupby("category")["amount"].sum().idxmax()
        if not filtered_expenses.empty
        else "N/A"
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Total spent", format_currency(total_spent))
    metric_col2.metric("Average expense", format_currency(average_spend))
    metric_col3.metric("Top category", top_category)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("Spending by category")
        category_totals = filtered_expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.bar_chart(category_totals)

    with chart_col2:
        st.subheader("Daily spending trend")
        daily_totals = filtered_expenses.groupby(filtered_expenses["date"].dt.date)["amount"].sum()
        st.line_chart(daily_totals)

    st.subheader("Expense sheet")
    display_expenses = filtered_expenses.copy()
    display_expenses["date"] = display_expenses["date"].dt.date
    st.dataframe(display_expenses, use_container_width=True, hide_index=True)

    csv_data = display_expenses.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered sheet as CSV",
        data=csv_data,
        file_name="expense_tracker_sheet.csv",
        mime="text/csv",
    )

    with st.expander("Danger zone"):
        st.warning("This clears every saved expense from the local CSV sheet.")
        if st.button("Clear all expenses"):
            save_expenses(pd.DataFrame(columns=COLUMNS))
            st.rerun()


if __name__ == "__main__":
    main()
