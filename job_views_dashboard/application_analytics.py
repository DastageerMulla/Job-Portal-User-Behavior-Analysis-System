import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import calendar

# --- 1. STYLING & HELPER FUNCTIONS ---

glass_style = {
    'background': 'rgba(255, 255, 255, 0.8)',
    'backdropFilter': 'blur(12px)',
    'border': '1px solid rgba(255, 255, 255, 0.9)',
    'boxShadow': '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
    'borderRadius': '15px',
    'marginBottom': '25px'
}


def create_detail_card(title, value, subtext, color, val_id=None):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-uppercase text-white-100",
                    style={'fontSize': '0.8rem', 'fontWeight': 'bold'}),
            html.H3(value, id=val_id if val_id else "", className="text-white",
                    style={'fontWeight': 'bold', 'margin': '5px 0', 'fontSize': '1.8rem'}),
            html.Small(subtext, className="text-white-90", style={'fontSize': '0.75rem'})
        ]),
        color=color,
        inverse=True,
        className="kpi-card shadow-sm h-100",
        style={'borderRadius': '12px', 'border': 'none'}
    )


# --- 2. LAYOUT DEFINITION ---

layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col(html.H3("Application Analytics", className="my-4", style={'fontWeight': '800', 'color': '#2c3e50'}),
                width=12)
    ]),

    # --- FILTERS ---
    dbc.Row([
        # 1. Date Range
        dbc.Col([
            html.Label("Job Posted Date Range", className="fw-bold small text-muted"),
            dcc.DatePickerRange(
                id='app-date-picker',
                display_format='YYYY-MM-DD',
                clearable=True,
                style={'width': '100%', 'borderRadius': '8px'}
            )
        ], width=12, md=3),

        # 2. Month Filter
        dbc.Col([
            html.Label("Filter by Month", className="fw-bold small text-muted"),
            dcc.Dropdown(
                id='app-month-dropdown',
                options=[{'label': calendar.month_name[i], 'value': i} for i in range(1, 13)],
                multi=True,
                placeholder="Select Months..."
            )
        ], width=12, md=3),

        # 3. Category
        dbc.Col([
            html.Label("Job Category", className="fw-bold small text-muted"),
            dcc.Dropdown(id='app-category-dropdown', multi=True, placeholder="All Categories")
        ], width=12, md=3),

        # 4. Company
        dbc.Col([
            html.Label("Company", className="fw-bold small text-muted"),
            dcc.Dropdown(id='app-company-dropdown', multi=True, placeholder="All Companies")
        ], width=12, md=3),

    ], className="p-4 mb-4 bg-white shadow-sm", style={'borderRadius': '15px', 'borderLeft': '5px solid #28a745'}),

    # --- KPI GRID ---
    dbc.Row([
        # Row 1: General Stats
        dbc.Col(create_detail_card("Total Applications", "0", "Sum of all apps", "dark", "app-card-total"), width=12,
                sm=6, lg=4,
                xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Avg Apps/Job", "0", "Apps per Posting", "info", "app-card-avg-job"), width=12, sm=6,
                lg=4,
                xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Median Apps/Job", "0", "Median per Posting", "info", "app-card-median-job"),
                width=12, sm=6,
                lg=4, xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Avg Apps/Month", "0", "Monthly Volume", "primary", "app-card-avg-month"), width=12,
                sm=6,
                lg=4, xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Conversion Rate", "0%", "Apps / Views", "danger", "app-card-conv"), width=12, sm=6,
                lg=4, xl=2,
                className="mb-3"),

        # Row 2: Highs & Lows
        dbc.Col(create_detail_card("Best Day (Volume)", "-", "Date: Total Apps", "success", "app-card-high-day"),
                width=12, sm=6,
                lg=4, className="mb-3"),
        dbc.Col(create_detail_card("Lowest Day (Volume)", "-", "Date: Total Apps", "warning", "app-card-low-day"),
                width=12, sm=6, lg=4,
                className="mb-3"),

        # Row 3: Top Lists
        dbc.Col(create_detail_card("Top 3 Categories", "-", "By Application Vol", "secondary", "app-card-top3-cat"),
                width=12, md=6,
                className="mb-3"),
        dbc.Col(create_detail_card("Top 3 Companies", "-", "By Application Vol", "secondary", "app-card-top3-comp"),
                width=12, md=6,
                className="mb-3"),
    ]),

    # --- GRAPHS ---
    dbc.Row([
        # Graph 1: Daily Trend
        dbc.Col(dbc.Card([
            dbc.CardHeader("1. Application Volume vs Job Creation Date", className="bg-transparent fw-bold border-0"),
            dbc.CardBody(dcc.Graph(id='app-daily-graph', style={'height': '350px'}, config={'displayModeBar': False}))
        ], style=glass_style), width=12),

        # Graph 2: Monthly Trend
        dbc.Col(dbc.Card([
            dbc.CardHeader("2. Application Volume (Monthly)", className="bg-transparent fw-bold border-0"),
            dbc.CardBody(dcc.Graph(id='app-monthly-graph', style={'height': '350px'}, config={'displayModeBar': False}))
        ], style=glass_style), width=12),
    ]),

    # --- DATA TABLE ---
    dbc.Row([
        dbc.Col([
            html.H5("Top Performing Jobs (By Applications)", className="mb-3 text-muted fw-bold"),
            html.Div(id='app-table-container', className="styled-table-container")
        ], width=12)
    ], className="mb-5")

], fluid=True)


# --- 3. CALLBACKS ---

def register_callbacks(app):
    # 1. Populate Dropdowns
    @app.callback(
        [Output('app-category-dropdown', 'options'),
         Output('app-company-dropdown', 'options')],
        Input('global-data-store', 'data')
    )
    def update_filters(data):
        if not data: return [], []
        df = pd.DataFrame(data)

        # UPDATED: Use mapped column names 'Job_Category' and 'Company'
        cats = [{'label': c, 'value': c} for c in
                sorted(df['Job_Category'].dropna().unique().astype(str))] if 'Job_Category' in df.columns else []
        comps = [{'label': c, 'value': c} for c in
                 sorted(df['Company'].dropna().unique().astype(str))] if 'Company' in df.columns else []
        return cats, comps

    # 2. Update Dashboard
    @app.callback(
        [
            Output('app-card-total', 'children'),
            Output('app-card-avg-job', 'children'),
            Output('app-card-median-job', 'children'),
            Output('app-card-avg-month', 'children'),
            Output('app-card-conv', 'children'),
            Output('app-card-high-day', 'children'),
            Output('app-card-low-day', 'children'),
            Output('app-card-top3-cat', 'children'),
            Output('app-card-top3-comp', 'children'),
            Output('app-daily-graph', 'figure'),
            Output('app-monthly-graph', 'figure'),
            Output('app-table-container', 'children')
        ],
        [
            Input('global-data-store', 'data'),
            Input('app-date-picker', 'start_date'),
            Input('app-date-picker', 'end_date'),
            Input('app-month-dropdown', 'value'),
            Input('app-category-dropdown', 'value'),
            Input('app-company-dropdown', 'value')
        ]
    )
    def update_analytics(data, start_date, end_date, selected_months, cats, comps):
        empty_fig = px.line(title="No Data")
        if not data:
            return "0", "0", "0", "0", "0%", "-", "-", "-", "-", empty_fig, empty_fig, None

        df = pd.DataFrame(data)

        # --- PREPROCESSING (Using Mapped Columns) ---
        # UPDATED: 'Created_At' instead of 'jobCreatedAtUTC'
        if 'Created_At' in df.columns:
            df['Created_At'] = pd.to_datetime(df['Created_At'], errors='coerce')

        # UPDATED: 'Total_Applications' and 'Total_Views'
        for col in ['Total_Applications', 'Total_Views']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # --- FILTERING ---
        if start_date and 'Created_At' in df.columns:
            df = df[df['Created_At'].dt.date >= pd.to_datetime(start_date).date()]
        if end_date and 'Created_At' in df.columns:
            df = df[df['Created_At'].dt.date <= pd.to_datetime(end_date).date()]

        if selected_months and 'Created_At' in df.columns:
            df = df[df['Created_At'].dt.month.isin(selected_months)]

        if cats and 'Job_Category' in df.columns:
            df = df[df['Job_Category'].isin(cats)]
        if comps and 'Company' in df.columns:
            df = df[df['Company'].isin(comps)]

        if df.empty:
            return "0", "0", "0", "0", "0%", "-", "-", "-", "-", empty_fig, empty_fig, None

        # --- KPI CALCULATIONS ---

        # 1. Total Applications
        total_apps = df['Total_Applications'].sum()

        # 2. Averages per Job
        avg_apps_per_job = round(df['Total_Applications'].mean(), 1)
        median_apps_per_job = round(df['Total_Applications'].median(), 1)

        # 3. Daily Aggregations
        if 'Created_At' in df.columns:
            daily_app_sum = df.groupby(df['Created_At'].dt.date)['Total_Applications'].sum()
        else:
            daily_app_sum = pd.Series()

        # Highest Day
        if not daily_app_sum.empty:
            high_val = daily_app_sum.max()
            high_date = daily_app_sum.idxmax().strftime('%b %d')
            high_str = f"{high_val} ({high_date})"
            low_val = daily_app_sum.min()
            low_date = daily_app_sum.idxmin().strftime('%b %d')
            low_str = f"{low_val} ({low_date})"
        else:
            high_str, low_str = "-", "-"

        # 4. Monthly Aggregations
        if 'Created_At' in df.columns:
            df['Month_Year'] = df['Created_At'].dt.to_period('M')
            monthly_app_sum = df.groupby('Month_Year')['Total_Applications'].sum()
            avg_apps_month = round(monthly_app_sum.mean(), 1)
        else:
            monthly_app_sum = pd.Series()
            avg_apps_month = 0

        # 5. Top 3 Categories
        if 'Job_Category' in df.columns:
            top3_cats = df.groupby('Job_Category')['Total_Applications'].sum().nlargest(3)
            top3_cat_str = ", ".join([f"{k}: {v}" for k, v in top3_cats.items()])
        else:
            top3_cat_str = "-"

        # 6. Top 3 Companies
        if 'Company' in df.columns:
            top3_comps = df.groupby('Company')['Total_Applications'].sum().nlargest(3)
            top3_comp_str = ", ".join([f"{k}: {v}" for k, v in top3_comps.items()])
        else:
            top3_comp_str = "-"

        # 7. Conversion
        tot_views = df['Total_Views'].sum()
        conv_rate = (total_apps / tot_views * 100) if tot_views > 0 else 0

        # --- GRAPHS ---

        # Daily Graph
        if not daily_app_sum.empty:
            daily_df = daily_app_sum.reset_index(name='Applications')
            fig_daily = px.area(daily_df, x='Created_At', y='Applications', markers=True, template="plotly_white")
            fig_daily.update_traces(line_color='#28a745', line_shape='spline', fill='tozeroy')
            fig_daily.update_layout(margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)')
        else:
            fig_daily = empty_fig

        # Monthly Graph
        if not monthly_app_sum.empty:
            monthly_df = monthly_app_sum.reset_index(name='Applications')
            monthly_df['Month_Year'] = monthly_df['Month_Year'].astype(str)
            fig_monthly = px.bar(monthly_df, x='Month_Year', y='Applications', template="plotly_white")
            fig_monthly.update_traces(marker_color='#17a2b8')
            fig_monthly.update_layout(margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)')
        else:
            fig_monthly = empty_fig

        # --- TABLE ---
        # UPDATED: Use mapped column names
        display_cols = ['Job_Title', 'Company', 'Job_Category', 'Created_At', 'Total_Views', 'Total_Applications']
        final_cols = [c for c in display_cols if c in df.columns]

        table = dash_table.DataTable(
            data=df[final_cols].sort_values('Total_Applications', ascending=False).head(50).to_dict('records'),
            columns=[{'name': i.replace('_', ' '), 'id': i} for i in final_cols],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Segoe UI'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ]
        )

        return (
            f"{total_apps:,}",
            f"{avg_apps_per_job}",
            f"{median_apps_per_job}",
            f"{avg_apps_month}",
            f"{conv_rate:.2f}%",
            high_str,
            low_str,
            top3_cat_str,
            top3_comp_str,
            fig_daily,
            fig_monthly,
            table
        )