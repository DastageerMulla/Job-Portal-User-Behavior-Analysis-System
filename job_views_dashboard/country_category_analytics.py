import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import calendar

# --- 1. COLOR THEMES ---
CARD_THEMES = {
    'black': {'bg': 'linear-gradient(135deg, #212529 0%, #343a40 100%)', 'text': '#ffffff'},
    'blue': {'bg': 'linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)', 'text': '#ffffff'},
    'purple': {'bg': 'linear-gradient(135deg, #6f42c1 0%, #59359a 100%)', 'text': '#ffffff'},
    'red': {'bg': 'linear-gradient(135deg, #dc3545 0%, #b02a37 100%)', 'text': '#ffffff'},
    'green': {'bg': 'linear-gradient(135deg, #198754 0%, #146c43 100%)', 'text': '#ffffff'},
    'orange': {'bg': 'linear-gradient(135deg, #fd7e14 0%, #e35d0b 100%)', 'text': '#ffffff'},
    'cyan': {'bg': 'linear-gradient(135deg, #0dcaf0 0%, #0aa2c0 100%)', 'text': '#ffffff'},
}


# --- 2. HELPER FUNCTION ---
def create_solid_card(card_id, title, value, subtext, theme_key):
    theme = CARD_THEMES.get(theme_key, CARD_THEMES['black'])
    return html.Div([
        html.H6(title, className="text-uppercase fw-bold",
                style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
        # Updated font size and line height to accommodate Top 3 lists
        html.H2(value, className="fw-bold",
                style={'margin': '5px 0', 'fontSize': '1.1rem', 'lineHeight': '1.4', 'whiteSpace': 'normal',
                       'wordWrap': 'break-word'}),
        html.Small(subtext, style={'fontSize': '0.75rem', 'opacity': '0.8'})
    ],
        id=card_id,
        style={
            'background': theme['bg'],
            'color': theme['text'],
            'borderRadius': '12px',
            'padding': '20px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
            'height': '100%',
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center',
            'border': 'none'
        },
        className="kpi-card-hover"
    )


# --- 3. LAYOUT ---
layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col(html.H3("Country vs. Category Performance", className="my-4",
                        style={'fontWeight': '800', 'color': '#2c3e50'}), width=12)
    ]),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Date Range", className="fw-bold small text-muted"),
            dcc.DatePickerRange(id='cca-date-picker', display_format='YYYY-MM-DD', clearable=True,
                                style={'width': '100%', 'borderRadius': '8px'})
        ], width=12, md=3),
        dbc.Col([
            html.Label("Month", className="fw-bold small text-muted"),
            dcc.Dropdown(id='cca-month-dropdown',
                         options=[{'label': calendar.month_name[i], 'value': i} for i in range(1, 13)], multi=True,
                         placeholder="Select Months...")
        ], width=12, md=3),
        dbc.Col([
            html.Label("Country", className="fw-bold small text-muted"),
            dcc.Dropdown(id='cca-country-dropdown', multi=True, placeholder="All Countries")
        ], width=12, md=3),
        dbc.Col([
            html.Label("Job Category", className="fw-bold small text-muted"),
            dcc.Dropdown(id='cca-category-dropdown', multi=True, placeholder="All Categories")
        ], width=12, md=3),
    ], className="p-4 mb-4 bg-white shadow-sm", style={'borderRadius': '15px', 'borderLeft': '5px solid #fd7e14'}),

    # --- KPI CARDS ---

    # Row 1: High Level Overview
    dbc.Row([
        dbc.Col(create_solid_card("cca-total-cats", "Total Categories", "0", "Active Globally", "black"), width=12,
                sm=6, lg=4, className="mb-4"),
        dbc.Col(create_solid_card("cca-top-global", "Top 3 Global Categories", "-", "Most Jobs Posted", "blue"),
                width=12, sm=6, lg=4, className="mb-4"),
        dbc.Col(create_solid_card("cca-top-country", "Top Country (Supply)", "-", "Most Jobs Posted", "purple"),
                width=12, sm=6, lg=4, className="mb-4"),
    ]),

    # Row 2: Job Supply Stats (Jobs Posted)
    dbc.Row([
        dbc.Col(create_solid_card("cca-job-total", "Total Jobs Posted", "0", "Global Sum", "blue"), width=12, sm=6,
                lg=4, className="mb-4"),
        dbc.Col(create_solid_card("cca-job-avg", "Avg Jobs/Category", "0", "Mean per Category", "blue"), width=12, sm=6,
                lg=4, className="mb-4"),
        dbc.Col(create_solid_card("cca-job-max", "Top 3 Categories (Volume)", "-", "Highest Job Counts", "blue"),
                width=12, sm=12, lg=4, className="mb-4"),
    ]),

    # Row 3: Demand Stats (Applications)
    dbc.Row([
        dbc.Col(create_solid_card("cca-app-total", "Total Applications", "0", "Global Sum", "green"), width=12, sm=6,
                lg=4, className="mb-4"),
        dbc.Col(create_solid_card("cca-app-avg", "Avg Apps/Job", "0", "Mean per Job Posting", "green"), width=12, sm=6,
                lg=4, className="mb-4"),
        dbc.Col(create_solid_card("cca-app-max", "Top 3 Categories (Demand)", "-", "Highest Applications", "green"),
                width=12, sm=12, lg=4, className="mb-4"),
    ]),

    # Row 4: Engagement Stats (Views)
    dbc.Row([
        dbc.Col(create_solid_card("cca-view-total", "Total Views", "0", "Global Sum", "cyan"), width=12, sm=6, lg=4,
                className="mb-4"),
        dbc.Col(create_solid_card("cca-view-avg", "Avg Views/Job", "0", "Mean per Job Posting", "cyan"), width=12, sm=6,
                lg=4, className="mb-4"),
        dbc.Col(create_solid_card("cca-view-max", "Top 3 Categories (Traffic)", "-", "Highest Views", "cyan"), width=12,
                sm=12, lg=4, className="mb-4"),
    ]),

    # --- GRAPHS ---
    dbc.Row([
        # Graph 1: Sunburst (Hierarchy) - Full Width
        dbc.Col(dbc.Card([
            dbc.CardHeader("1. Global Distribution: Country > Category (Jobs)",
                           className="bg-transparent fw-bold border-0"),
            dbc.CardBody(dcc.Graph(id='cca-sunburst', style={'height': '500px'}, config={'displayModeBar': False}))
        ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'},
            className="mb-4"), width=12),
    ]),

    # --- TABLE ---
    dbc.Row([
        dbc.Col([
            html.H5("Detailed Country & Category Performance Matrix", className="mb-3 text-muted fw-bold"),
            html.Div(id='cca-table-container', style={'background': 'white', 'padding': '20px', 'borderRadius': '12px',
                                                      'boxShadow': '0 4px 12px rgba(0,0,0,0.05)'})
        ], width=12)
    ], className="mb-5")

], fluid=True)


# --- 4. CALLBACKS ---
def register_callbacks(app):
    # --- 1. Populate Dropdowns ---
    @app.callback(
        [Output('cca-country-dropdown', 'options'),
         Output('cca-category-dropdown', 'options')],
        Input('global-data-store', 'data')
    )
    def update_filters(data):
        if not data: return [], []
        df = pd.DataFrame(data)
        countries = [{'label': c, 'value': c} for c in
                     sorted(df['Country'].dropna().unique().astype(str))] if 'Country' in df.columns else []
        cats = [{'label': c, 'value': c} for c in
                sorted(df['Job_Category'].dropna().unique().astype(str))] if 'Job_Category' in df.columns else []
        return countries, cats

    # --- 2. Update Analytics ---
    @app.callback(
        [
            # Row 1
            Output('cca-total-cats', 'children'), Output('cca-top-global', 'children'),
            Output('cca-top-country', 'children'),
            # Row 2 (Jobs)
            Output('cca-job-total', 'children'), Output('cca-job-avg', 'children'), Output('cca-job-max', 'children'),
            # Row 3 (Apps)
            Output('cca-app-total', 'children'), Output('cca-app-avg', 'children'), Output('cca-app-max', 'children'),
            # Row 4 (Views)
            Output('cca-view-total', 'children'), Output('cca-view-avg', 'children'),
            Output('cca-view-max', 'children'),
            # Graphs & Table
            Output('cca-sunburst', 'figure'),
            Output('cca-table-container', 'children')
        ],
        [
            Input('global-data-store', 'data'),
            Input('cca-date-picker', 'start_date'),
            Input('cca-date-picker', 'end_date'),
            Input('cca-month-dropdown', 'value'),
            Input('cca-country-dropdown', 'value'),
            Input('cca-category-dropdown', 'value')
        ]
    )
    def update_analytics(data, start_date, end_date, selected_months, selected_countries, selected_cats):
        empty_fig = px.bar(title="No Data")

        # Helper for Card Content
        def make_content(title, val, sub):
            return [
                html.H6(title, className="text-uppercase fw-bold",
                        style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
                html.H2(val, className="fw-bold",
                        style={'margin': '5px 0', 'fontSize': '1.1rem', 'lineHeight': '1.4', 'whiteSpace': 'normal',
                               'wordWrap': 'break-word'}),
                html.Small(sub, style={'fontSize': '0.75rem', 'opacity': '0.8'})
            ]

        defaults = [make_content("Metric", "0", "No Data")] * 12 + [empty_fig, None]

        if not data: return defaults

        df = pd.DataFrame(data)

        # --- PREPROCESSING ---
        if 'Created_At' in df.columns:
            df['Created_At'] = pd.to_datetime(df['Created_At'], errors='coerce')

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
        if selected_countries and 'Country' in df.columns:
            df = df[df['Country'].isin(selected_countries)]
        if selected_cats and 'Job_Category' in df.columns:
            df = df[df['Job_Category'].isin(selected_cats)]

        if df.empty or 'Country' not in df.columns or 'Job_Category' not in df.columns:
            return defaults

        # --- AGGREGATION LOGIC ---

        # 1. Group by Category (Global Stats)
        cat_stats = df.groupby('Job_Category').agg({
            'Job_Title': 'count',
            'Total_Applications': 'sum',
            'Total_Views': 'sum'
        }).rename(columns={'Job_Title': 'Job_Count'})

        # 2. Group by Country (For Table)
        country_stats = df.groupby('Country').agg({
            'Job_Title': 'count',
            'Total_Applications': 'sum',
            'Total_Views': 'sum'
        }).rename(columns={'Job_Title': 'Job_Count'})

        # --- KPI CALCULATIONS ---

        # Row 1
        total_cats = len(cat_stats)

        # Top 3 Global Categories (Names only)
        top3_global = cat_stats['Job_Count'].nlargest(3).index.tolist()
        top_global_str = ", ".join(top3_global) if top3_global else "-"

        top_country = country_stats['Job_Count'].idxmax() if not country_stats.empty else "-"
        top_country_val = country_stats['Job_Count'].max() if not country_stats.empty else 0

        # Row 2 (Jobs)
        total_jobs = cat_stats['Job_Count'].sum()
        avg_jobs = round(cat_stats['Job_Count'].mean(), 1)  # Avg Jobs per Category

        # Top 3 Categories by Jobs (Name + Value)
        top3_jobs = cat_stats['Job_Count'].nlargest(3)
        max_jobs_str = ", ".join([f"{idx} ({val})" for idx, val in top3_jobs.items()])

        # Row 3 (Apps)
        total_apps = cat_stats['Total_Applications'].sum()
        avg_apps = round(total_apps / total_jobs, 1) if total_jobs > 0 else 0  # Avg Apps per Job

        # Top 3 Categories by Apps (Name + Value)
        top3_apps = cat_stats['Total_Applications'].nlargest(3)
        max_apps_str = ", ".join([f"{idx} ({val})" for idx, val in top3_apps.items()])

        # Row 4 (Views)
        total_views = cat_stats['Total_Views'].sum()
        avg_views = round(total_views / total_jobs, 1) if total_jobs > 0 else 0  # Avg Views per Job

        # Top 3 Categories by Views (Name + Value)
        top3_views = cat_stats['Total_Views'].nlargest(3)
        max_views_str = ", ".join([f"{idx} ({val})" for idx, val in top3_views.items()])

        # --- GRAPHS ---

        # 1. Sunburst (Country -> Category -> Jobs)
        sunburst_df = df.groupby(['Country', 'Job_Category']).size().reset_index(name='Jobs')
        top_countries = sunburst_df.groupby('Country')['Jobs'].sum().nlargest(15).index
        sunburst_df = sunburst_df[sunburst_df['Country'].isin(top_countries)]

        fig_sun = px.sunburst(sunburst_df, path=['Country', 'Job_Category'], values='Jobs',
                              color='Jobs', color_continuous_scale='Blues')
        fig_sun.update_layout(margin=dict(l=0, r=0, t=0, b=0))

        # --- TABLE LOGIC ---

        # 1. Base Aggregation by Country
        table_base = df.groupby('Country').agg({
            'Job_Title': 'count',
            'Total_Applications': 'sum',
            'Total_Views': 'sum',
            'Job_Category': 'nunique'  # Count unique categories
        }).reset_index()

        # Flatten columns
        table_base.columns = ['Country', 'Total Jobs', 'Total Apps', 'Total Views', 'Cat Count']

        # 2. Calculate Averages
        table_base['Avg Jobs'] = (table_base['Total Jobs'] / table_base['Cat Count']).round(1)  # Jobs per Category
        table_base['Avg Apps'] = (table_base['Total Apps'] / table_base['Total Jobs']).round(1)  # Apps per Job
        table_base['Avg Views'] = (table_base['Total Views'] / table_base['Total Jobs']).round(1)  # Views per Job

        # 3. Find Top 3 Categories per Country
        cc_counts = df.groupby(['Country', 'Job_Category']).size().reset_index(name='Count')
        cc_counts = cc_counts.sort_values(['Country', 'Count'], ascending=[True, False])

        def get_top_3_cols(x):
            cats = x['Job_Category'].head(3).tolist()
            while len(cats) < 3: cats.append("-")
            return pd.Series(cats, index=['Top 1 Cat', 'Top 2 Cat', 'Top 3 Cat'])

        top_cats_df = cc_counts.groupby('Country').apply(get_top_3_cols).reset_index()

        # 4. Merge
        final_table = pd.merge(table_base, top_cats_df, on='Country', how='left')
        final_table = final_table.sort_values('Total Jobs', ascending=False)

        # 5. Reorder Columns
        cols_order = ['Country', 'Top 1 Cat', 'Top 2 Cat', 'Top 3 Cat', 'Total Jobs', 'Avg Jobs', 'Total Apps',
                      'Avg Apps', 'Total Views', 'Avg Views']

        table = dash_table.DataTable(
            data=final_table.head(50).to_dict('records'),
            columns=[{'name': i, 'id': i} for i in cols_order],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Segoe UI'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ]
        )

        return (
            # Row 1
            make_content("Total Categories", f"{total_cats}", "Active Globally"),
            make_content("Top 3 Global Categories", top_global_str, "By Job Volume"),
            make_content("Top Country (Supply)", f"{top_country}", f"{top_country_val} Jobs"),
            # Row 2
            make_content("Total Jobs Posted", f"{total_jobs:,}", "Global Sum"),
            make_content("Avg Jobs/Category", f"{avg_jobs}", "Mean per Category"),
            make_content("Top 3 Categories (Volume)", max_jobs_str, "Highest Job Counts"),
            # Row 3
            make_content("Total Applications", f"{total_apps:,}", "Global Sum"),
            make_content("Avg Apps/Job", f"{avg_apps}", "Mean per Job"),
            make_content("Top 3 Categories (Demand)", max_apps_str, "Highest Applications"),
            # Row 4
            make_content("Total Views", f"{total_views:,}", "Global Sum"),
            make_content("Avg Views/Job", f"{avg_views}", "Mean per Job"),
            make_content("Top 3 Categories (Traffic)", max_views_str, "Highest Views"),
            # Visuals
            fig_sun,
            table
        )