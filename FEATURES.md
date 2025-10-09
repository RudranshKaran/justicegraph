# NyayaLens - Complete Feature Documentation

## 📋 Table of Contents
1. [Home Page](#home-page)
2. [Explore Data Dashboard](#explore-data-dashboard)
3. [Delay Prediction](#delay-prediction)
4. [Regional Insights](#regional-insights)
5. [Model Explainability](#model-explainability)
6. [About & Feedback](#about--feedback)

---

## 🏠 Home Page

### Features
- **Hero Section**: Project title and mission statement
- **Quick Access Buttons**: Navigate to all main pages
- **Summary Statistics Cards**:
  - Total Cases Analyzed: 45M+
  - States Covered: 28
  - Average Delay: 3.2 years
  - Pending Cases: 38M
  - Resolution Rate: 15.6%
- **Backlog Trend Chart**: Interactive line chart showing case growth (2015-2025)
- **Key Insights Section**: Highlights important metrics
- **Call to Action**: Encouraging users to explore features

### User Flow
1. Land on homepage
2. View summary statistics
3. Read project overview
4. Navigate to specific feature via buttons

---

## 📊 Explore Data Dashboard

### Sidebar Filters
- **Year Range Slider**: 2015-2025
- **State/District Dropdown**: All Indian states
- **Court Type**: Supreme, High, District
- **Case Type**: Civil, Criminal, Other
- **Reset Filters Button**
- **Export CSV Button**

### Visualizations

#### 1. Geographic Map
- Interactive Folium map of India
- State-wise markers with pending case data
- Color-coded by average duration:
  - 🟢 Green: < 3 years
  - 🟡 Orange: 3-4 years
  - 🔴 Red: > 4 years
- Tooltips with state details

#### 2. Top 10 States Bar Chart
- Pending cases by state
- Color: Deep Maroon (#800000)
- Interactive hover details

#### 3. Average Duration Chart
- Average case duration by state
- Color: Royal Blue (#1A237E)
- Sortable visualization

#### 4. Trend Analysis
- Dual-line chart:
  - Pending cases (Maroon)
  - Resolved cases (Blue)
- Filtered by year range
- Hover for exact values

#### 5. Case Type Distribution
- Pie charts showing:
  - Case types (Civil, Criminal, etc.)
  - Court levels (District, High, Supreme)

#### 6. Data Table
- Filtered summary table
- Columns: State, Total Cases, Avg Duration, Pending %
- Formatted numbers and percentages
- Top 10 results

### Key Insights Cards
- Highest Backlog (Orange card)
- Best Performance (Green card)
- Overall Statistics (Blue card)

---

## 🔮 Delay Prediction

### Input Form
- **Case Type**: Dropdown with 7 options
- **State**: 14 major states
- **Court Type**: District, High, Supreme
- **Filing Date**: Date picker
- **Case Category**: 9 categories
- **Hearings Count**: Numeric input (0-100)
- **Case Summary**: Optional text area

### Prediction Output

#### 1. Result Cards (Gradient Design)
- **Delay Probability**: 
  - Percentage display (0-100%)
  - Blue gradient background
- **Predicted Duration**:
  - Years to resolution
  - Maroon gradient background

#### 2. Contributing Factors
- Top 3-5 factors with visual bars
- Impact percentage for each
- Color-coded by importance

#### 3. Feature Importance Chart
- Horizontal bar chart
- Viridis colorscale
- Sorted by importance

#### 4. Recommendations
- Risk-based messaging:
  - **High Risk (>70%)**: Error alert with actions
  - **Moderate Risk (50-70%)**: Warning with tips
  - **Low Risk (<50%)**: Success message

### Model Information
- Architecture details
- Training data statistics
- Performance metrics

---

## 🗺️ Regional Insights

### Interactive Map
- Folium map with state markers
- Toggle metric view:
  - Average Duration
  - Pending Cases
  - Resolution Rate

### State Comparison
- **Selection**: Two dropdown menus
- **Compare Button**: Triggers analysis
- **Side-by-Side Cards**:
  - Pending cases count
  - Average duration
  - Resolution rate
- **Gauge Charts**: Visual efficiency score (0-100)
- **Comparison Bar Chart**: All metrics together

### Performance Rankings

#### Best Performers
- Top 5 states by resolution time
- Medal system (🥇🥈🥉)
- Green card styling

#### Highest Backlog
- Top 5 states by pending cases
- Numbered list
- Red card styling

### Correlation Heatmap
- 6x6 matrix showing relationships:
  - Backlog
  - Duration
  - Resolution Rate
  - Population
  - GDP
  - Courts Count
- Red-Blue colorscale
- Numerical correlation values

### Regional Trends Chart
- Multi-line chart by region:
  - North (Red)
  - South (Green)
  - East (Blue)
  - West (Orange)
- 2018-2025 timeframe

### Export Options
- State data CSV
- Geographic data CSV
- Trend data CSV

### Key Takeaways
- Best Performers card (Green)
- Areas of Concern card (Orange)
- National Average card (Blue)

---

## 🧠 Model Explainability

### Feature Importance
- **Bar Chart**: Top 7 features with scores
- **Top Features List**: Card showing top 5 with impact %
- **Interpretation Guide**

### Performance Metrics
- **Accuracy**: 87% (Green card)
- **Precision**: 85% (Blue card)
- **Recall**: 83% (Orange card)
- **F1 Score**: 0.84 (Pink card)

### ROC Curve
- Interactive Plotly chart
- AUC score: 0.91
- Comparison with random classifier
- Interpretation guide

### SHAP Summary Plot
- Placeholder visualization
- Explanation of SHAP values
- Feature contribution analysis

### Confusion Matrix
- 2x2 heatmap (Blue colorscale)
- Values:
  - True Positives: 870
  - True Negatives: 850
  - False Positives: 150
  - False Negatives: 130
- Interpretation cards for each quadrant

### Model Training Details
- **Training Data Card**:
  - 2M+ cases
  - 2015-2025 period
  - 28 states
  - 45 features
- **Architecture Card**:
  - Ensemble type
  - Component models
  - Validation method
- **Optimization Card**:
  - Hyperparameter tuning
  - Class balancing
  - Feature selection

### Training History
- Line chart showing:
  - Training accuracy (Blue)
  - Validation accuracy (Maroon)
- 50 epochs
- Convergence visualization

### Privacy & Ethics
- **Privacy Guarantees Card** (Green):
  - Anonymization
  - No PII
  - Compliance
  - Audits
- **Ethical AI Card** (Blue):
  - Fairness
  - Transparency
  - Accountability
  - Non-discrimination

### Disclaimer
- Comprehensive usage notice
- Data source information
- Legal disclaimer

### Version History Table
- Version numbers
- Release dates
- Improvements
- Accuracy metrics

---

## ℹ️ About & Feedback

### Project Overview
- Mission statement (Gradient card)
- Platform description
- Goals and objectives

### Justice Index
- **Gauge Chart**: National score (0-100)
- **Composition Breakdown**:
  - Resolution Rate: 30%
  - Average Delay: 25%
  - Backlog Growth: 20%
  - Access to Justice: 15%
  - Digital Adoption: 10%
- Current score: 68.5/100

### Platform Features
- **Data Exploration Card** (Green)
- **AI Predictions Card** (Blue)
- **Regional Insights Card** (Orange)

### Technology Stack
- **Frontend Card**:
  - Streamlit, Plotly, Folium
  - Pandas, GeoPandas
- **Backend Card**:
  - FastAPI, MongoDB
  - ML libraries, SHAP

### Team Section
- 4 team members with:
  - Emoji avatar
  - Name
  - Role
  - Bio
- Card layout (4 columns)

### Feedback Form
- **Input Fields**:
  - Name (required)
  - Email (required)
  - Organization (optional)
  - Feedback Type dropdown
  - Rating slider (1-5)
  - Feedback text area (required)
- **Submit Button**: Posts to API
- **Success/Error Messages**
- **Feedback Stats Card**:
  - Total responses
  - Average rating
  - Response time

### Resources Section
- **Documentation Links**
- **GitHub Repository**:
  - Link with stats
  - Stars and forks count
- **Research Papers**

### Acknowledgments
- Data sources
- Partners
- Funding
- Contributors

### License & Privacy
- **Open Source License Card** (Green):
  - MIT License
  - Usage terms
- **Privacy Policy Card** (Blue):
  - Data handling
  - Privacy commitment

### Footer
- Logo and tagline
- Copyright notice
- Legal links
- Contact information

---

## 🎨 Design System

### Colors
- **Primary**: #1A237E (Royal Blue)
- **Secondary**: #800000 (Deep Maroon)
- **Background**: #F5F5F5 (Light Gray)
- **Success**: #E8F5E9 (Light Green)
- **Warning**: #FFF3E0 (Light Orange)
- **Info**: #E3F2FD (Light Blue)
- **Error**: #FFEBEE (Light Red)

### Components
- **Cards**: White background, rounded corners, shadow
- **Buttons**: Gradient, hover effects
- **Metrics**: Large numbers, icons, delta indicators
- **Charts**: Consistent color scheme, interactive
- **Forms**: Clean inputs, validation

### Typography
- **Headings**: Inter, bold
- **Body**: Inter, regular
- **Code**: Monospace

### Layout
- **Responsive**: Desktop and mobile
- **Grid System**: Streamlit columns
- **Spacing**: Consistent padding/margins
- **Hierarchy**: Clear visual structure

---

## 🔄 User Workflows

### Workflow 1: Explore Case Data
1. Navigate to "Explore Data"
2. Apply filters (state, year, court type)
3. View geographic map
4. Analyze charts and trends
5. Export data as CSV

### Workflow 2: Predict Case Delay
1. Navigate to "Delay Prediction"
2. Fill in case details form
3. Submit prediction
4. Review results and factors
5. Read recommendations

### Workflow 3: Compare States
1. Navigate to "Regional Insights"
2. Select two states from sidebar
3. Click "Compare States"
4. Review side-by-side metrics
5. Analyze differences

### Workflow 4: Understand Model
1. Navigate to "Model Explainability"
2. Review feature importance
3. Check performance metrics
4. Examine ROC curve
5. Read privacy policies

### Workflow 5: Provide Feedback
1. Navigate to "About"
2. Fill feedback form
3. Submit feedback
4. Receive confirmation

---

## 📱 Responsive Design

- **Desktop**: Full sidebar, multi-column layouts
- **Tablet**: Adjusted columns, collapsible sidebar
- **Mobile**: Single column, stacked cards

---

## ⚡ Performance Features

- **Caching**: API calls cached for 5 minutes
- **Lazy Loading**: Heavy libraries loaded on demand
- **Data Sampling**: Large datasets sampled for display
- **Optimized Charts**: Plotly with reduced data points

---

## 🔒 Security Features

- **No Hardcoded Secrets**: All via environment variables
- **Input Validation**: Form data sanitized
- **API Timeout**: 30 seconds max
- **Error Handling**: Graceful degradation

---

**Last Updated**: October 2025
**Version**: 3.0
