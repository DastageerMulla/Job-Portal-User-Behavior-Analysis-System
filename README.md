📊 TalentSight Analytics: Job Portal Dashboard


TalentSight Analytics is an enterprise-grade business intelligence platform designed to visualize the entire recruitment lifecycle. By integrating data from job postings, candidate applications, and user traffic, this dashboard empowers HR executives and platform administrators to optimize supply (jobs), demand (candidates), and retention strategies.
The system features a modular architecture with specialized analytics for Job Supply, Candidate Demand, Traffic Engagement, Geographic Reach, and Partner Retention.
✨ Key Features

1. 🏢 Executive & Job Overview
High-Level Metrics: Real-time tracking of Total Jobs, Applications, Views, and Conversion Rates.
Supply Trends: Visualize the "Feast or Famine" cycle of job postings with daily and monthly trend lines.
Performance Skew: Analyze the gap between Average and Median performance to identify "Viral Jobs" vs. standard listings.

2. 🌍 Geographic Market Intelligence
Global Footprint: Interactive bar charts and sunburst diagrams showing market dominance (e.g., US vs. Rest of World).
Regional Efficiency: Compare "Applications per Job" across different countries to identify high-potential markets vs. saturated ones.
Visual Mapping: Color-coded maps and charts to highlight top-performing regions.

3. 📉 Retention & Loyalty Engine
Churn Analysis: Distinguish between "One-Time Posters" and "Retained Partners" (Active > 30 Days).
Performance Correlation: A unique "Why do they return?" analysis that correlates retention rates with the number of applications/views a company receives.
Loyalty Segmentation: Categorize companies based on posting frequency (1 Job, 2-5 Jobs, 10+ Jobs).

4. 👥 Candidate Demand & Traffic
Funnel Analysis: Track the user journey from "View" to "Application" with conversion rate anomalies.
Traffic Quality: Identify "Window Shopping" behavior (High Views, Low Apps) vs. "Direct Action" behavior (Low Views, High Apps).
Category Insights: Drill down into specific job sectors (e.g., IT vs. Logistics) to see where demand is highest.

5. 🎨 Modern UI/UX
Glassmorphism Design: Clean, semi-transparent card designs for a modern aesthetic.
Solid Gradient KPIs: Visually distinct metric cards (Blue for Jobs, Green for Apps, Cyan for Views) for instant readability.
Dynamic Filtering: Global filters for Date Range, Month, Country, Category, and Company that update all charts instantly.


🛠️ Tech Stack
Core Framework: Python Dash (Plotly)
Visualization: Plotly Express & Graph Objects
Data Processing: Pandas, NumPy
Database: MySQL (via SQLAlchemy & PyMySQL)
UI Components: Dash Bootstrap Components (DBC)
Environment Management: Python Dotenv


🚀 Installation & Setup

1. Clone the Repository
code
Bash
git clone https://github.com/yourusername/talentsight-analytics.git
cd talentsight-analytics

2. Environment Configuration
Create a .env file in the root directory to store your database credentials securely.

Env
# Database Configuration (Remote or Local)
SQL_HOST=
SQL_USER=
SQL_PASSWORD=
SQL_DATABASE=

3. Install Dependencies
Ensure you have Python 3.8+ installed. Run the following command to install all required libraries:

pip install -r requirements.txt
requirements.txt content:
code
Text
dash
dash-bootstrap-components
pandas
plotly
sqlalchemy
pymysql
python-dotenv
numpy

4. Run the ETL Process (Optional)
If you need to fetch fresh data from the remote source and load it into your local XAMPP/SQL warehouse:

python Data/get_localsqldata.py

5. Launch the Dashboard
Run the main application entry point:

python app.py
Access the Dashboard: Open your browser and go to http://127.0.0.1:8050/



📂 Project Structure

code
Text
/talentsight-analytics
│
├── app.py                          # Main Entry Point (Routing & Sidebar)
├── .env                            # Environment Variables (Credentials)
├── requirements.txt                # Python Dependencies
│
├── Data/
│   └── get_localsqldata.py         # ETL Script (Remote SQL -> Local SQL)
│
├── job_views_dashboard/            # Dashboard Pages Module
│   ├── __init__.py
│   ├── overview_analytics.py       # Page 1: Executive Summary
│   ├── jobs_posted_analytics.py    # Page 2: Supply Side Analysis
│   ├── application_analytics.py    # Page 3: Demand Side Analysis
│   ├── views_analytics.py          # Page 4: Traffic Engagement
│   ├── country_jobs_posted.py      # Page 5: Geographic Supply
│   ├── application_country.py      # Page 6: Geographic Demand
│   ├── views_country.py            # Page 7: Geographic Traffic
│   
│
└── assets/
    └── style.css                   # Custom CSS (Glassmorphism & Gradients)


📊 Dashboard Pages Overview
Job Overview: A holistic summary of the platform's health, comparing total supply, demand, and traffic trends over time.
Jobs Posted: Deep dive into company posting behaviors, seasonal spikes, and bulk-upload trends.
App Analytics: Analysis of candidate volume, identifying "Viral Jobs" and high-volume categories.
Views Analytics: Insights into user browsing behavior and the "Funnel Inversion" phenomenon.
Country Analytics (Jobs/Apps/Views): Three dedicated pages to dissect market performance by region (e.g., US dominance vs. Emerging Markets).
Retention Analytics: Strategic analysis of company loyalty, calculating retention rates based on performance metrics.

Images:
