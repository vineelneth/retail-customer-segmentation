import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from auth import authenticate_user
from data_engine import load_and_clean_data, format_inr
from math_models import process_rfm, apply_clustering

st.set_page_config(page_title="Grocery Segmentation", layout="wide")

authenticate_user()

st.title("🛒 Grocery Customer Segmentation Dashboard")
st.write(
    "Upload transaction data to group customers and generate targeted marketing campaigns."
)

SAVE_DIR = "app_data"
SAVE_PATH = os.path.join(SAVE_DIR, "latest_transactions.csv")

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

uploaded_file = st.file_uploader(
    "Upload your transactions CSV (Updates the database)", type=["csv"]
)

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        raw_df.to_csv(SAVE_PATH, index=False)
        st.success("✅ Database updated successfully!")
    except Exception:
        st.error(
            "❌ The file you uploaded could not be read. Please ensure it is a valid, uncorrupted CSV file."
        )

if os.path.exists(SAVE_PATH):
    raw_df = pd.read_csv(SAVE_PATH)
    clean_df, status = load_and_clean_data(raw_df)

    if clean_df is None:
        st.error(status)
    else:
        st.sidebar.header("📅 Timeframe Filter")
        min_date = clean_df["invoice_date"].min().date()
        max_date = clean_df["invoice_date"].max().date()

        col_start, col_end = st.sidebar.columns(2)
        start_date = col_start.date_input(
            "Start Date", value=min_date, min_value=min_date, max_value=max_date
        )
        end_date = col_end.date_input(
            "End Date", value=max_date, min_value=min_date, max_value=max_date
        )

        if start_date > end_date:
            st.error("⚠️ Please ensure the Start Date comes before the End Date.")
        else:
            mask = (clean_df["invoice_date"].dt.date >= start_date) & (
                clean_df["invoice_date"].dt.date <= end_date
            )
            filtered_df = clean_df.loc[mask]

            rfm_base, X_scaled = process_rfm(filtered_df)

            if rfm_base is None or len(rfm_base) < 4:
                st.warning("Not enough data in this date range to form segments.")
            else:
                rfm = apply_clustering(rfm_base, X_scaled, best_k=4)

                st.sidebar.divider()
                st.sidebar.header("🔍 Search Specific Customer")
                search_id = (
                    st.sidebar.text_input("Enter Customer ID (e.g., C042)")
                    .strip()
                    .upper()
                )

                if search_id:
                    customer_data = rfm[rfm["customer_id"].str.upper() == search_id]
                    if not customer_data.empty:
                        st.sidebar.success(
                            f"**Status:** {customer_data.iloc[0]['segment_label']}"
                        )
                        st.sidebar.write(
                            f"**Total Spent:** {format_inr(customer_data.iloc[0]['monetary'])}"
                        )
                        st.sidebar.write(
                            f"**Total Visits:** {customer_data.iloc[0]['frequency']}"
                        )
                        st.sidebar.write(
                            f"**Last Visit:** {customer_data.iloc[0]['last_visit_date'].strftime('%d %b %Y')}"
                        )
                    else:
                        st.sidebar.error("Customer not found.")

                tab1, tab2 = st.tabs(["📊 Analytics Dashboard", "✉️ Campaign Manager"])

                with tab1:
                    st.header("📊 Executive Summary")
                    kpi1, kpi2, kpi3 = st.columns(3)
                    kpi1.metric("Total Revenue", format_inr(rfm["monetary"].sum()))
                    kpi2.metric("Total Customers", len(rfm))
                    kpi3.metric("Storewide AOV", format_inr(rfm["aov"].mean()))
                    st.divider()

                    col1, col2 = st.columns([1.2, 1])
                    with col1:
                        st.subheader("1. Segment Profiles")
                        profile = (
                            rfm.groupby("segment_label")
                            .agg(
                                Customers=("customer_id", "nunique"),
                                Avg_Recency=("recency_days", "mean"),
                                Avg_Freq=("frequency", "mean"),
                                Avg_Spend=("monetary", "mean"),
                                Avg_Order_Value=("aov", "mean"),
                            )
                            .round(1)
                            .reset_index()
                        )
                        st.dataframe(profile, use_container_width=True, hide_index=True)

                        st.divider()
                        st.subheader("💰 Revenue Contribution")
                        rev_by_segment = rfm.groupby("segment_label")["monetary"].sum()
                        fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
                        ax_pie.pie(
                            rev_by_segment,
                            labels=rev_by_segment.index,
                            autopct="%1.1f%%",
                            startangle=140,
                            colors=plt.cm.Set2.colors,
                            textprops={"fontsize": 9},
                        )
                        ax_pie.axis("equal")
                        st.pyplot(fig_pie)

                    with col2:
                        st.subheader("2. Visual Map")
                        pca = PCA(n_components=2, random_state=42)
                        proj = pca.fit_transform(X_scaled)
                        rfm["pca1"], rfm["pca2"] = proj[:, 0], proj[:, 1]

                        fig, ax = plt.subplots(figsize=(7, 6))
                        for segment in rfm["segment_label"].unique():
                            subset = rfm[rfm["segment_label"] == segment]
                            ax.scatter(
                                subset["pca1"],
                                subset["pca2"],
                                label=segment,
                                alpha=0.8,
                                edgecolors="w",
                                s=80,
                            )
                        ax.set_xticks([])
                        ax.set_yticks([])
                        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
                        plt.tight_layout()
                        st.pyplot(fig)

                with tab2:
                    st.header("✉️ Segment Action Center")
                    target_segment = st.selectbox(
                        "Select Target Segment:", rfm["segment_label"].unique()
                    )
                    target_list = rfm[rfm["segment_label"] == target_segment]

                    st.success(
                        f"**Audience Size:** Campaign for **{len(target_list)}** customers."
                    )

                    msgs = {
                        "High-Value Active": "🌟 VIP EXCLUSIVE: Hi [Name]! Show this message at checkout for a free gift! 🎁",
                        "Steady Regulars": "🛒 Time for a restock? Hi [Name], earn DOUBLE loyalty points this weekend.",
                        "At-Risk / Churning": "👋 We miss you, [Name]! Come back this week and enjoy flat ₹200 OFF!",
                        "Inactive / Lost": "🚨 MEGA CLEARANCE! Hi [Name], drop by today for massive weekend discounts.",
                    }
                    st.info(
                        msgs.get(
                            target_segment, "Hi [Name], check out our latest offers!"
                        )
                    )

                    target_csv = (
                        target_list[
                            ["customer_id", "recency_days", "frequency", "monetary"]
                        ]
                        .to_csv(index=False)
                        .encode("utf-8")
                    )
                    st.download_button(
                        f"⬇️ Download {target_segment} List (CSV)",
                        data=target_csv,
                        file_name=f"Campaign_{target_segment.replace(' ', '_')}.csv",
                        mime="text/csv",
                    )
else:
    st.info("👋 Welcome! Please upload your first transaction CSV to get started.")
