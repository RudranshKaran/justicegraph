## **Complete Tech Stack (Free + Professional-Level)**

### 1. **Data Layer**

| Purpose                        | Tools                                                  | Why                                                                                                                                       |
| ------------------------------ | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Data Collection (Scraping)** | `BeautifulSoup4`, `Requests`, `Selenium`, `Playwright` | Extract data from public court databases (like eCourts, LawStar, Indian Kanoon, etc.). Playwright > Selenium for handling JS-heavy sites. |
| **APIs (if available)**        | `Open Government Data (OGD)` Portal, `Data.gov.in`     | Access structured data if government provides it.                                                                                         |
| **Data Storage (Raw + Clean)** | `MongoDB Atlas (Free Tier)`                            | Cloud NoSQL database — perfect for unstructured court records, scalable, free tier.                                                       |
| **Backup / Versioning**        | `Google Drive API` or `AWS S3 (Free Tier)`             | Store snapshots for reproducibility and audit trail.                                                                                      |

---

### 2. **Data Cleaning & Processing Layer**

| Purpose                 | Tools                    | Why                                                                                                        |
| ----------------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------- |
| **Data Preprocessing**  | `Pandas`, `NumPy`        | Standard cleaning, date normalization, missing value handling.                                             |
| **Text Normalization**  | `Regex`, `nltk`, `spaCy` | Legal documents are text-heavy; you’ll clean, tokenize, and extract entities (judges, courts, acts, etc.). |
| **Parallel Processing** | `Dask` or `Modin`        | For large-scale data cleaning (especially thousands of case records).                                      |

---

### 3. **Modeling Layer (Core Data Science)**

| Goal                                         | Tool                                              | Description                                                                |
| -------------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------- |
| **Case Delay Prediction**                    | `scikit-learn`                                    | Start with Random Forest / Gradient Boosting for baseline models.          |
| **Feature Engineering**                      | `Pandas`, `Category Encoders`                     | Derive features like court type, region, judge, category, complexity, etc. |
| **NLP-based Insights Extraction**            | `HuggingFace Transformers` (`BERT`, `Legal-BERT`) | Extract key themes (e.g., delay reasons, act types) from text judgments.   |
| **Time Series Forecasting (Backlog Trends)** | `Prophet` or `statsmodels`                        | Predict future case inflow/backlog patterns per district or court.         |
| **Clustering of Similar Cases**              | `KMeans`, `HDBSCAN`, `UMAP`                       | Find clusters of similar cases to identify systemic bottlenecks.           |

---

### 4. **Visualization & Insights Layer**

| Goal                               | Tool                          | Description                                           |
| ---------------------------------- | ----------------------------- | ----------------------------------------------------- |
| **EDA and Interactive Dashboards** | `Plotly`, `Dash`, `Streamlit` | Beautiful, interactive, and public-facing dashboards. |
| **Geo Analysis**                   | `Folium`, `GeoPandas`         | Map backlogs and delays across states/districts.      |
| **Legal Text Visualization**       | `WordCloud`, `NetworkX`       | For act connections and theme analysis.               |

*(You can choose either Streamlit or Dash — Streamlit is easier and faster to deploy for public access.)*

---

### 5. **Backend & API Layer**

| Purpose                       | Tool                                       | Why                                                 |
| ----------------------------- | ------------------------------------------ | --------------------------------------------------- |
| **Model Serving**             | `FastAPI`                                  | Lightweight, fast REST API for serving predictions. |
| **Database Integration**      | `Motor` (async MongoDB client for FastAPI) | Asynchronous access to MongoDB for fast retrieval.  |
| **Authentication (Optional)** | `Auth0` free plan or `Firebase Auth`       | For securing user access if you go public.          |

---

### 6. **Deployment Layer**

| Goal                          | Tool                                         | Description                             |
| ----------------------------- | -------------------------------------------- | --------------------------------------- |
| **App Hosting**               | `Streamlit Community Cloud` *(Free)*         | Deploy interactive web app easily.      |
| **API Hosting**               | `Render` / `Railway` / `Deta.space` *(Free)* | Deploy FastAPI backend.                 |
| **Database Hosting**          | `MongoDB Atlas` *(Free)*                     | Cloud storage for data and predictions. |
| **Model Registry (Optional)** | `Weights & Biases (W&B)` or `MLflow`         | Track model performance and versions.   |

---

### 7. **MLOps + Monitoring (Optional but Impressive)**

| Goal                       | Tool                                           | Description                              |
| -------------------------- | ---------------------------------------------- | ---------------------------------------- |
| **Experiment Tracking**    | `MLflow` or `Weights & Biases`                 | Logs runs, hyperparameters, and results. |
| **Pipeline Orchestration** | `Prefect` / `Airflow` *(Local setup possible)* | Automate ETL → Training → Deployment.    |
| **Version Control**        | `GitHub`                                       | For code, notebooks, and documentation.  |

---

### 8. **Collaboration & Documentation**

| Tool                   | Purpose                                          |
| ---------------------- | ------------------------------------------------ |
| `Jupyter Notebooks`    | Exploratory analysis, model development          |
| `Notion` or `Obsidian` | For documenting case studies, notes, and results |
| `GitHub Pages`         | Host public documentation site for “NyayaLens”   |

---

## **Example End-to-End Flow with Tech Stack**

**1. Data Scraping** → Playwright + BeautifulSoup
**2. Data Cleaning** → Pandas + spaCy
**3. Storage** → MongoDB Atlas
**4. Modeling** → scikit-learn + LegalBERT
**5. Visualization** → Streamlit + Plotly + GeoPandas
**6. API Integration** → FastAPI
**7. Deployment** → Streamlit Cloud (frontend) + Render (backend)
**8. Monitoring & Docs** → MLflow + GitHub Pages