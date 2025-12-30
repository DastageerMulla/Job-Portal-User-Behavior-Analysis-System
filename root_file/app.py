import sys
import os
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

# 1. PATH CONFIGURATION
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 2. IMPORT DATA & PAGES
from Data.get_localsqldata import load_data

# Import existing pages
from job_views_dashboard.overview_analytics import layout as page1_layout, register_callbacks as register_page1_callbacks
from job_views_dashboard.jobs_posted_analytics import layout as page2_layout, register_callbacks as register_page2_callbacks
from job_views_dashboard.application_analytics import layout as page3_layout, register_callbacks as register_page3_callbacks
from job_views_dashboard.views_analytics import layout as page4_layout, register_callbacks as register_page4_callbacks
from job_views_dashboard.country_jobs_posted import layout as page5_layout, register_callbacks as register_page5_callbacks
from job_views_dashboard.application_country import layout as page6_layout, register_callbacks as register_page6_callbacks
from job_views_dashboard.views_country import layout as page7_layout, register_callbacks as register_page7_callbacks

# --- NEW PAGE IMPORT (Retention Analytics) ---
from job_views_dashboard.country_category_analytics import layout as page8_layout, register_callbacks as register_page8_callbacks

# 3. APP SETUP
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME], suppress_callback_exceptions=True)
server = app.server
app.title = "Job Portal Analytics"

# --- LOAD DATA ---
print("🚀 Launching App... Fetching Data from XAMPP...")
df = load_data()
initial_data = df.to_dict('records') if df is not None else []

# 4. SIDEBAR
SIDEBAR_STYLE = {
    "position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "16rem",
    "padding": "2rem 1rem", "backgroundColor": "#2b2d42", "color": "#f8f9fa", "boxShadow": "2px 0 5px rgba(0,0,0,0.1)"
}
CONTENT_STYLE = {
    "marginLeft": "16rem", "padding": "2rem 2rem", "backgroundColor": "#eef2f5", "minHeight": "100vh"
}

sidebar = html.Div([
    html.Div([html.I(className="fas fa-briefcase fa-lg me-2", style={"color": "#f4d35e"}), html.Span("Job Portal Admin", className="h5 fw-bold", style={"color": "white"})], className="mb-4 d-flex align-items-center"),
    html.Hr(style={"borderColor": "rgba(255,255,255,0.2)"}),
    dbc.Nav([
        dbc.NavLink([html.I(className="fas fa-chart-line me-2"), "Job Overview"], href="/dashboard", active="exact", className="text-white-50 mb-2"),
        dbc.NavLink([html.I(className="fas fa-calendar-alt me-2"), "Jobs Posted"], href="/jobs-analytics", active="exact", className="text-white-50 mb-2"),
        dbc.NavLink([html.I(className="fas fa-file-signature me-2"), "App Analytics"], href="/application-analytics", active="exact", className="text-white-50 mb-2"),
        dbc.NavLink([html.I(className="fas fa-eye me-2"), "Views Analytics"], href="/views-analytics", active="exact", className="text-white-50 mb-2"),
        dbc.NavLink([html.I(className="fas fa-globe-americas me-2"), "Country Jobs Posted"], href="/country-jobs-posted", active="exact", className="text-white-50 mb-2"),
        dbc.NavLink([html.I(className="fas fa-flag me-2"), "App Country Analytics"], href="/application-country", active="exact", className="text-white-50 mb-2"),
        dbc.NavLink([html.I(className="fas fa-globe me-2"), "Views Country Analytics"], href="/views-country", active="exact", className="text-white-50 mb-2"),
        # --- NEW LINK ---
        dbc.NavLink([html.I(className="fas fa-sync-alt me-2"), "Category Analytics"], href="/category-analytics", active="exact", className="text-white-50 mb-2"),
    ], vertical=True, pills=True),
], style=SIDEBAR_STYLE)

# 5. LAYOUT
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='global-data-store', data=initial_data),
    sidebar,
    html.Div(id='page-content', style=CONTENT_STYLE)
])

# 6. REGISTER CALLBACKS
register_page1_callbacks(app)
register_page2_callbacks(app)
register_page3_callbacks(app)
register_page4_callbacks(app)
register_page5_callbacks(app)
register_page6_callbacks(app)
register_page7_callbacks(app)
register_page8_callbacks(app) # Register Retention Callbacks

# 7. ROUTING
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/' or pathname == '/dashboard': return page1_layout
    elif pathname == '/jobs-analytics': return page2_layout
    elif pathname == '/application-analytics': return page3_layout
    elif pathname == '/views-analytics': return page4_layout
    elif pathname == '/country-jobs-posted': return page5_layout
    elif pathname == '/application-country': return page6_layout
    elif pathname == '/views-country': return page7_layout
    elif pathname == '/category-analytics': return page8_layout # New Route
    else: return page1_layout

if __name__ == '__main__':
    app.run(debug=True, port=8050)