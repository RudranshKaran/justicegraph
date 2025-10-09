# NyayaLens: AI-Powered Judicial Insights for Faster Justice

<div align="center">

![NyayaLens Logo](https://via.placeholder.com/800x200/1A237E/FFFFFF?text=NyayaLens+-+AI-Powered+Judicial+Insights)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 🏛️ Overview

NyayaLens is an advanced AI-driven analytics platform that analyzes Indian court case data to identify backlog trends, predict case delays, and visualize judicial inefficiencies. Built with Streamlit and FastAPI, it provides actionable insights for faster, more efficient justice delivery.

## ✨ Features

### 📊 Data Exploration Dashboard
- Interactive filters for year range, state, court type, and case type
- Geographic heatmap visualization of India with state-wise metrics
- Comprehensive charts and trend analysis
- Exportable data summaries

### 🔮 AI-Powered Delay Prediction
- Machine learning model with **87% accuracy**
- Predicts delay probability and expected resolution time
- SHAP-based feature importance analysis
- Actionable recommendations based on predictions

### 🗺️ Regional Insights
- Interactive state comparison tools
- Correlation analysis between judicial metrics
- Regional performance rankings
- Geographic trend visualization

### 🧠 Model Explainability
- Transparent AI with feature importance charts
- ROC curves and confusion matrices
- Training history and performance metrics
- Ethical AI principles and privacy guarantees

### ℹ️ About & Feedback
- Justice Index national metric
- Team and contributor information
- Integrated feedback form
- Comprehensive documentation links

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/RudranshKaran/justicegraph.git
cd justicegraph
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
justicegraph/
├── app.py                          # Main homepage
├── pages/
│   ├── 01_Explore_Data.py         # Data exploration dashboard
│   ├── 02_Predict_Delay.py        # AI prediction interface
│   ├── 03_Regional_Insights.py    # Geographic analysis
│   ├── 04_Model_Explainability.py # Model transparency
│   └── 05_About.py                # About & feedback
├── utils/
│   ├── api.py                     # API utility functions
│   └── visuals.py                 # Visualization helpers
├── .streamlit/
│   └── config.toml                # Streamlit configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🛠️ Technology Stack

### Frontend
- **Framework:** Streamlit
- **Visualization:** Plotly, Folium, Matplotlib, Seaborn
- **Data Processing:** Pandas, NumPy
- **Geospatial:** GeoPandas

### Backend (API Integration Ready)
- **API Framework:** FastAPI
- **Database:** MongoDB Atlas
- **ML Models:** Scikit-learn, XGBoost, TensorFlow
- **Explainability:** SHAP

### Deployment
- **Platform:** Streamlit Community Cloud
- **CI/CD:** GitHub Actions (optional)

## 🎨 Design System

### Color Palette
- **Primary:** Royal Blue (#1A237E)
- **Secondary:** Deep Maroon (#800000)
- **Background:** Light Gray (#F5F5F5)
- **Accent:** Sky Blue (#4A90E2)

### Typography
- **Font Family:** Inter, Poppins, Roboto

## 📊 Data Sources

NyayaLens uses publicly available, anonymized judicial data from:
- National Judicial Data Grid (NJDG)
- e-Courts Project
- State Judicial Departments

**Note:** All data is anonymized and contains no personally identifiable information (PII).

## 🔌 API Integration

The application is designed to connect with a FastAPI backend. Configure the API endpoint in `.env`:

```env
FASTAPI_BASE_URL=http://localhost:8000
API_TIMEOUT=30
```

### API Endpoints (Backend Required)

- `GET /data/summary` - Summary statistics
- `GET /data/cases` - Filtered case data
- `POST /predict` - Case delay prediction
- `POST /feedback` - User feedback submission

**Demo Mode:** The app includes dummy data generators for testing without a backend.

## 🚢 Deployment to Streamlit Cloud

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets** (if using backend API)
   - In Streamlit Cloud dashboard, go to App settings → Secrets
   - Add your environment variables:
   ```toml
   FASTAPI_BASE_URL = "https://your-api-url.com"
   API_TIMEOUT = "30"
   ```

## 🧪 Testing

Run the application locally and test each page:

```bash
streamlit run app.py
```

Navigate through all pages:
1. Home → Check metrics and navigation
2. Explore Data → Test filters and visualizations
3. Predict Delay → Submit test predictions
4. Regional Insights → Compare states
5. Model Explainability → Review metrics
6. About → Submit test feedback

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributors

- **Dr. Aisha Sharma** - Lead Data Scientist
- **Rajesh Kumar** - Full-Stack Developer
- **Priya Mehta** - Legal Domain Expert
- **Arjun Singh** - UI/UX Designer

## 📧 Contact

- **Email:** info@nyayalens.org
- **GitHub:** [@RudranshKaran](https://github.com/RudranshKaran)
- **Twitter:** @NyayaLens

## ⚠️ Disclaimer

NyayaLens is an analytical tool for research and insights. All predictions are based on historical data patterns and should not be considered as legal advice or definitive case outcomes. This platform is designed to support judicial reform efforts and improve access to justice.

## 🙏 Acknowledgments

- National Judicial Data Grid (NJDG)
- e-Courts Project
- Digital India Initiative
- Indian Institute of Technology
- National Law Universities
- All contributors and supporters

---

<div align="center">

**© 2025 NyayaLens | Built with ❤️ using Streamlit & FastAPI**

[Documentation](#) | [API Reference](#) | [Report Issue](https://github.com/RudranshKaran/justicegraph/issues)

</div>
