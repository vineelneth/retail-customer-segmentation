# Grocery Customer Segmentation Dashboard

A production-style Streamlit web application that performs **RFM (Recency, Frequency, Monetary) analysis** and **K-Means clustering** on grocery transaction data to identify customer segments and generate targeted marketing campaigns.

---

## Features

- **Secure login** — role-based authentication with session cookies (manager + staff accounts)
- **Live data ingestion** — upload any CSV and the dashboard updates instantly
- **RFM pipeline** — log-transformed, scaled, and outlier-capped before clustering
- **K-Means segmentation** — automatically maps clusters to business labels (High-Value Active, Steady Regulars, At-Risk / Churning, Inactive / Lost)
- **Executive KPI summary** — total revenue, customer count, and average order value
- **Visual segment map** — PCA-reduced 2-D scatter plot coloured by segment
- **Revenue pie chart** — share of wallet by segment
- **Per-customer lookup** — search any customer ID for their full profile
- **Campaign manager** — pre-written SMS/WhatsApp copy per segment + one-click CSV export of the audience list
- **Date-range filter** — slice any time window from the sidebar

---

## Tech Stack

| Layer | Library |
|-------|---------|
| UI / Server | Streamlit |
| Auth | streamlit-authenticator |
| Data wrangling | pandas, numpy |
| ML | scikit-learn (StandardScaler, KMeans) |
| Dimensionality reduction | scikit-learn PCA |
| Visualisation | matplotlib |

---

## Project Structure

```
├── main.py                  # Streamlit entry point — layout & orchestration
├── auth.py                  # Login / logout / session cookie logic
├── data_engine.py           # CSV validation, cleaning, INR formatter
├── math_models.py           # RFM computation + K-Means clustering
├── generatesDataset.py      # Utility script to generate mock transaction data
├── mock_transactions.csv    # Sample dataset (500 rows, 100 customers)
├── requirements.txt         # Pinned Python dependencies
├── .streamlit/
│   ├── config.toml          # Theme and server settings
│   └── secrets.toml         # Credentials — DO NOT commit (see secrets.toml.example)
└── app_data/
    └── latest_transactions.csv   # Persisted upload (git-ignored)
```

---

## Local Setup

### 1. Clone & install

```bash
git clone https://github.com/<your-username>/rfm-grocery-segmentation.git
cd rfm-grocery-segmentation
pip install -r requirements.txt
```

### 2. Configure secrets

Copy the example file and fill in your own values:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
[passwords]
admin  = "your_manager_password"
staff1 = "your_staff_password"

[cookies]
key = "a_long_random_secret_string_at_least_32_chars"
```

### 3. Run

```bash
streamlit run main.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Demo Credentials

| Role | Username | Password (default) |
|------|----------|-------------------|
| Store Manager | `admin` | set in `secrets.toml` |
| Checkout Staff | `staff1` | set in `secrets.toml` |

---

## CSV Format

The dashboard accepts any CSV with at least these three columns (case-insensitive, whitespace-tolerant):

| Column | Type | Example |
|--------|------|---------|
| `customer_id` | string | `C042` |
| `invoice_date` | date | `15-03-2024` |
| `amount` | numeric | `1250` |

Run `generatesDataset.py` to generate a ready-to-use mock dataset:

```bash
python generatesDataset.py
# → mock_transactions.csv  (500 transactions, 100 customers, Jan 2024 – Feb 2025)
```

---

## How RFM Works

| Metric | Definition |
|--------|-----------|
| **Recency** | Days since the customer's last purchase |
| **Frequency** | Total number of purchases in the period |
| **Monetary** | Total spend in the period |

The pipeline applies **log1p transformation** and **99th-percentile capping** before scaling, so a single high-spending outlier does not distort the clusters.

### Segment labels (ranked by composite RFM score)

| Rank | Segment | Description |
|------|---------|-------------|
| 1 | High-Value Active | Recent, frequent, high-spend buyers |
| 2 | Steady Regulars | Consistent mid-tier shoppers |
| 3 | At-Risk / Churning | Used to buy regularly, haven't returned |
| 4 | Inactive / Lost | Long-absent, low historical value |

---

## Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub (ensure `.streamlit/secrets.toml` is in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select your repo.
3. Add your secrets under **Settings → Secrets** (paste the contents of `secrets.toml`).
4. Click **Deploy**.

---

## License

MIT — see [LICENSE](LICENSE).
