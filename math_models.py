import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import streamlit as st


@st.cache_data
def process_rfm(df):
    """Computes RFM metrics with log-transform and 99th-percentile capping."""
    if df.empty:
        return None, None

    reference_date = df["invoice_date"].max() + pd.Timedelta(days=1)
    rfm = (
        df.groupby("customer_id")
        .agg(
            recency_days=("invoice_date", lambda x: (reference_date - x.max()).days),
            last_visit_date=("invoice_date", "max"),
            frequency=("customer_id", "count"),
            monetary=("amount", "sum"),
        )
        .reset_index()
    )

    rfm["monetary_clipped"] = rfm["monetary"].clip(upper=rfm["monetary"].quantile(0.99))
    rfm["frequency_clipped"] = rfm["frequency"].clip(upper=rfm["frequency"].quantile(0.99))
    rfm["monetary_log"] = np.log1p(rfm["monetary_clipped"])
    rfm["frequency_log"] = np.log1p(rfm["frequency_clipped"])

    X = rfm[["recency_days", "frequency_log", "monetary_log"]].copy()
    X_scaled = StandardScaler().fit_transform(X)

    return rfm, X_scaled


@st.cache_data
def apply_clustering(rfm, X_scaled, best_k=4):
    """Runs K-Means and maps each cluster to a ranked business label."""
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    rfm["cluster"] = kmeans.fit_predict(X_scaled)

    cluster_stats = rfm.groupby("cluster").agg(
        {"recency_days": "mean", "frequency": "mean", "monetary": "mean"}
    )
    cluster_stats["score"] = (
        cluster_stats["monetary"].rank(ascending=True)
        + cluster_stats["frequency"].rank(ascending=True)
        + cluster_stats["recency_days"].rank(ascending=False)
    )
    cluster_stats = cluster_stats.sort_values("score", ascending=False).reset_index()

    labels = ["High-Value Active", "Steady Regulars", "At-Risk / Churning", "Inactive / Lost"]
    mapping = {
        row["cluster"]: labels[i]
        for i, row in cluster_stats.iterrows()
        if i < len(labels)
    }
    rfm["segment_label"] = rfm["cluster"].map(mapping)
    rfm["aov"] = rfm["monetary"] / rfm["frequency"]

    return rfm
