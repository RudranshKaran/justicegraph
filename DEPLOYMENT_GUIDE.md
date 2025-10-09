# NyayaLens Deployment Guide

## 🚀 Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. Ensure all files are committed:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. Verify these files exist:
- `app.py` (main file)
- `requirements.txt`
- `.streamlit/config.toml`
- All page files in `/pages`
- All utility files in `/utils`

### Step 2: Deploy on Streamlit Cloud

1. **Sign in to Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Sign in with GitHub

2. **Create New App**
   - Click "New app"
   - Repository: `RudranshKaran/justicegraph`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: Choose a custom URL (e.g., `nyayalens`)

3. **Advanced Settings** (Optional)
   - Python version: 3.9
   - Click "Deploy"

### Step 3: Configure Environment Variables

If connecting to a backend API:

1. Go to App settings → Secrets
2. Add:
```toml
FASTAPI_BASE_URL = "https://your-api-url.com"
API_TIMEOUT = "30"
```

### Step 4: Monitor Deployment

- Watch the deployment logs
- First deployment takes 2-5 minutes
- App will auto-reload on git push

## 📱 Local Development

### Run Locally
```bash
streamlit run app.py
```

### View on Network
```bash
streamlit run app.py --server.address=0.0.0.0
```

## 🐳 Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t nyayalens .
docker run -p 8501:8501 nyayalens
```

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility

**2. Page Not Loading**
- Verify file structure matches Streamlit conventions
- Check `pages/` folder naming

**3. API Connection Issues**
- Verify environment variables
- Check backend API is running

**4. Visualization Issues**
- Clear Streamlit cache: Settings → Clear cache
- Restart the app

## ✅ Pre-Deployment Checklist

- [ ] All code tested locally
- [ ] Requirements.txt updated
- [ ] No hardcoded secrets or API keys
- [ ] .gitignore includes sensitive files
- [ ] README.md is comprehensive
- [ ] All pages load without errors
- [ ] Responsive on mobile devices
- [ ] Performance optimized (caching enabled)

## 📊 Performance Optimization

1. **Use Caching**
```python
@st.cache_data(ttl=300)
def expensive_function():
    pass
```

2. **Lazy Loading**
- Load heavy libraries only when needed
- Use dynamic imports

3. **Optimize Data**
- Use data sampling for large datasets
- Implement pagination

## 🔒 Security Best Practices

1. Never commit `.env` files
2. Use Streamlit secrets for sensitive data
3. Validate all user inputs
4. Sanitize API responses
5. Use HTTPS for production

## 📈 Monitoring

Monitor app health:
- Streamlit Cloud dashboard
- Error logs
- User analytics (if configured)

## 🆘 Support

Issues? Contact:
- Email: support@nyayalens.org
- GitHub Issues: https://github.com/RudranshKaran/justicegraph/issues

---

**Happy Deploying! 🚀**
