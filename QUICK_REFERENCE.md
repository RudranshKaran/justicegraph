# 🚀 NyayaLens - Quick Reference Guide

## 📦 Installation (3 Steps)

```bash
# 1. Clone the repository
git clone https://github.com/RudranshKaran/justicegraph.git
cd justicegraph

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

**Windows PowerShell**: Run `.\run.ps1`
**Linux/Mac**: Run `./run.sh`

---

## 📁 Project Structure

```
justicegraph/
├── app.py                          # 🏠 Homepage
├── pages/
│   ├── 01_Explore_Data.py         # 📊 Data dashboard
│   ├── 02_Predict_Delay.py        # 🔮 AI prediction
│   ├── 03_Regional_Insights.py    # 🗺️ Geographic analysis
│   ├── 04_Model_Explainability.py # 🧠 Model transparency
│   └── 05_About.py                # ℹ️ About & feedback
├── utils/
│   ├── api.py                     # API functions
│   └── visuals.py                 # Chart helpers
├── .streamlit/config.toml         # Streamlit config
├── requirements.txt               # Dependencies
└── .env                           # Environment vars
```

---

## 🎨 Quick Commands

### Run Locally
```bash
streamlit run app.py
```

### Run on Network
```bash
streamlit run app.py --server.address=0.0.0.0
```

### Clear Cache
```bash
streamlit cache clear
```

### Install New Package
```bash
pip install package_name
pip freeze > requirements.txt
```

---

## 🔧 Configuration

### `.env` File
```env
FASTAPI_BASE_URL=http://localhost:8000
API_TIMEOUT=30
```

### `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#1A237E"
backgroundColor = "#F5F5F5"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1A1A1A"
```

---

## 📊 Page Overview

| Page | Route | Key Features |
|------|-------|-------------|
| Home | `/` | Stats, navigation, trend chart |
| Explore Data | `/01_Explore_Data` | Filters, map, charts, table |
| Predict Delay | `/02_Predict_Delay` | Form, prediction, factors |
| Regional Insights | `/03_Regional_Insights` | State comparison, rankings |
| Model Explainability | `/04_Model_Explainability` | Metrics, ROC, confusion matrix |
| About | `/05_About` | Team, feedback, resources |

---

## 🎯 Key Functions

### API Functions (`utils/api.py`)
- `fetch_data(endpoint)` - GET request with caching
- `post_data(endpoint, data)` - POST request
- `predict_delay(case_data)` - Delay prediction
- `get_dummy_*()` - Dummy data generators

### Visual Functions (`utils/visuals.py`)
- `create_line_chart()` - Line graphs
- `create_bar_chart()` - Bar graphs
- `create_india_map()` - Geographic map
- `create_gauge_chart()` - Gauge visualization
- `create_feature_importance_chart()` - ML feature chart
- `apply_custom_css()` - Custom styling

---

## 🐛 Troubleshooting

### Import Error
```bash
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
streamlit run app.py --server.port=8502
```

### Cache Issues
```bash
streamlit cache clear
# Or in app: Settings → Clear cache
```

### Module Not Found
```bash
# Ensure you're in project root
cd justicegraph
python -c "import sys; print(sys.path)"
```

---

## 🚀 Deployment Checklist

- [ ] Test all pages locally
- [ ] Update requirements.txt
- [ ] Remove hardcoded secrets
- [ ] Test without backend API
- [ ] Verify responsive design
- [ ] Check error handling
- [ ] Commit to GitHub
- [ ] Deploy on Streamlit Cloud
- [ ] Configure secrets
- [ ] Test production URL

---

## 📝 Common Tasks

### Add New Page
1. Create `pages/06_New_Page.py`
2. Follow naming convention (number_name)
3. Import utilities
4. Set page config
5. Test navigation

### Add New Chart
1. Add function to `utils/visuals.py`
2. Use consistent color scheme
3. Add title and labels
4. Return Plotly figure
5. Use in page with `st.plotly_chart()`

### Add New API Endpoint
1. Add function to `utils/api.py`
2. Use `@st.cache_data` decorator
3. Handle errors gracefully
4. Return dictionary
5. Test with dummy data

### Customize Styling
1. Edit `.streamlit/config.toml` for theme
2. Modify `apply_custom_css()` in `utils/visuals.py`
3. Use inline styles in markdown
4. Test on multiple screens

---

## 🔑 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FASTAPI_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `API_TIMEOUT` | Request timeout (seconds) | `30` |

---

## 📊 Dummy Data Functions

All pages work without backend using these functions:
- `get_dummy_summary_stats()`
- `get_dummy_backlog_trend()`
- `get_dummy_state_data()`
- `get_dummy_case_data()`
- `get_dummy_geo_data()`
- `get_dummy_feature_importance()`
- `get_dummy_model_metrics()`

---

## 🎨 Color Palette

```python
PRIMARY = "#1A237E"      # Royal Blue
SECONDARY = "#800000"    # Deep Maroon
BACKGROUND = "#F5F5F5"   # Light Gray
ACCENT = "#4A90E2"       # Sky Blue
SUCCESS = "#6BCF7F"      # Green
WARNING = "#FFA726"      # Orange
ERROR = "#E94B3C"        # Red
```

---

## 📱 Browser Support

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

---

## 📚 Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python
- **Folium Docs**: https://python-visualization.github.io/folium
- **Pandas Docs**: https://pandas.pydata.org

---

## 💡 Tips & Tricks

1. **Fast Reload**: Edit files and Streamlit auto-reloads
2. **Debug Mode**: Add `st.write()` for debugging
3. **Session State**: Use `st.session_state` for persistence
4. **Caching**: Use `@st.cache_data` for expensive operations
5. **Columns**: Use `st.columns()` for layouts
6. **Expanders**: Use `st.expander()` for collapsible sections

---

## 🆘 Get Help

- **GitHub Issues**: https://github.com/RudranshKaran/justicegraph/issues
- **Email**: support@nyayalens.org
- **Streamlit Forum**: https://discuss.streamlit.io

---

## 📊 Performance Metrics

- **Load Time**: < 3 seconds
- **Page Navigation**: Instant
- **Chart Rendering**: < 1 second
- **API Timeout**: 30 seconds
- **Cache TTL**: 5 minutes

---

## ✅ Testing Checklist

- [ ] Homepage loads with all metrics
- [ ] All navigation buttons work
- [ ] Filters apply correctly
- [ ] Charts render properly
- [ ] Forms submit successfully
- [ ] Maps display correctly
- [ ] Mobile view works
- [ ] No console errors

---

**Quick Start**: Just run `streamlit run app.py` and start exploring! 🚀

**Need Help?** Check DEPLOYMENT_GUIDE.md or FEATURES.md for detailed information.

---

**© 2025 NyayaLens | Built with ❤️ using Streamlit**
