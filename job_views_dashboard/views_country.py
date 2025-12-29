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
        dbc.Col(html.H3("View Analytics by Country", className="my-4", style={'fontWeight': '800', 'color': '#2c3e50'}),
                width=12)
    ]),

    # --- FILTERS ---
    dbc.Row([
        # 1. Date Range
        dbc.Col([
            html.Label("Date Range", className="fw-bold small text-muted"),
            dcc.DatePickerRange(
                id='vc-date-picker',
                display_format='YYYY-MM-DD',
                clearable=True,
                style={'width': '100%', 'borderRadius': '8px'}
            )
        ], width=12, md=3),

        # 2. Month Filter
        dbc.Col([
            html.Label("Filter by Month", className="fw-bold small text-muted"),
            dcc.Dropdown(
                id='vc-month-dropdown',
                options=[{'label': calendar.month_name[i], 'value': i} for i in range(1, 13)],
                multi=True,
                placeholder="Select Months..."
            )
        ], width=12, md=3),

        # 3. Country Filter (Primary Focus)
        dbc.Col([
            html.Label("Country", className="fw-bold small text-muted"),
            dcc.Dropdown(id='vc-country-dropdown', multi=True, placeholder="All Countries")
        ], width=12, md=3),

        # 4. Category Filter
        dbc.Col([
            html.Label("Job Category", className="fw-bold small text-muted"),
            dcc.Dropdown(id='vc-category-dropdown', multi=True, placeholder="All Categories")
        ], width=12, md=3),

    ], className="p-4 mb-4 bg-white shadow-sm", style={'borderRadius': '15px', 'borderLeft': '5px solid #17a2b8'}),

    # --- KPI GRID ---
    dbc.Row([
        # Row 1: General Stats
        dbc.Col(create_detail_card("Total Views", "0", "Global Volume", "dark", "vc-card-total"), width=12,
                sm=6, lg=4, xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Avg Views/Country", "0", "Mean per Region", "info", "vc-card-avg-country"),
                width=12, sm=6,
                lg=4, xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Active Countries", "0", "Countries with Views", "info", "vc-card-active-countries"),
                width=12, sm=6, lg=4, xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Top Country Share", "0%", "Dominance", "primary", "vc-card-share"), width=12,
                sm=6, lg=4, xl=2, className="mb-3"),
        dbc.Col(create_detail_card("Conversion Rate", "0%", "Global Apps/Views", "danger", "vc-card-conv"), width=12,
                sm=6,
                lg=4, xl=2, className="mb-3"),

        # Row 2: Highs & Lows
        dbc.Col(create_detail_card("Top Country (Traffic)", "-", "Name: Total Views", "success", "vc-card-top-country"),
                width=12, sm=6, lg=4, className="mb-3"),
        dbc.Col(
            create_detail_card("Lowest Country (Traffic)", "-", "Name: Total Views", "warning", "vc-card-low-country"),
            width=12, sm=6, lg=4, className="mb-3"),

        # Row 3: Top Lists
        dbc.Col(create_detail_card("Top 3 Markets", "-", "Country: Views", "secondary", "vc-card-top3"),
                width=12, md=4, className="mb-3"),
        dbc.Col(create_detail_card("Top 3 Categories", "-", "Category: Views", "secondary", "vc-card-top3-cat"),
                width=12, md=4, className="mb-3"),
        dbc.Col(create_detail_card("Top 3 Companies", "-", "Company: Views", "secondary", "vc-card-top3-comp"),
                width=12, md=4, className="mb-3"),
    ]),

    # --- GRAPHS ---
    dbc.Row([
        # Graph 1: Bar Chart (Countries)
        dbc.Col(dbc.Card([
            dbc.CardHeader("1. Total Views by Country (Top 20)", className="bg-transparent fw-bold border-0"),
            dbc.CardBody(dcc.Graph(id='vc-bar-graph', style={'height': '350px'}, config={'displayModeBar': False}))
        ], style=glass_style), width=12),

        # Graph 2: Pie Chart (Share)
        dbc.Col(dbc.Card([
            dbc.CardHeader("2. View Traffic Market Share Distribution", className="bg-transparent fw-bold border-0"),
            dbc.CardBody(dcc.Graph(id='vc-pie-graph', style={'height': '350px'}, config={'displayModeBar': False}))
        ], style=glass_style), width=12),
    ]),

    # --- DATA TABLE ---
    dbc.Row([
        dbc.Col([
            html.H5("Detailed Country View Statistics", className="mb-3 text-muted fw-bold"),
            html.Div(id='vc-table-container', className="styled-table-container")
        ], width=12)
    ], className="mb-5")

], fluid=True)


# --- 3. CALLBACKS ---

def register_callbacks(app):
    # 1. Populate Dropdowns
    @app.callback(
        [Output('vc-country-dropdown', 'options'),
         Output('vc-category-dropdown', 'options')],
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

    # 2. Update Dashboard
    @app.callback(
        [
            Output('vc-card-total', 'children'),
            Output('vc-card-avg-country', 'children'),
            Output('vc-card-active-countries', 'children'),
            Output('vc-card-share', 'children'),
            Output('vc-card-conv', 'children'),
            Output('vc-card-top-country', 'children'),
            Output('vc-card-low-country', 'children'),
            Output('vc-card-top3', 'children'),
            Output('vc-card-top3-cat', 'children'),
            Output('vc-card-top3-comp', 'children'),
            Output('vc-bar-graph', 'figure'),
            Output('vc-pie-graph', 'figure'),
            Output('vc-table-container', 'children')
        ],
        [
            Input('global-data-store', 'data'),
            Input('vc-date-picker', 'start_date'),
            Input('vc-date-picker', 'end_date'),
            Input('vc-month-dropdown', 'value'),
            Input('vc-country-dropdown', 'value'),
            Input('vc-category-dropdown', 'value')
        ]
    )
    def update_analytics(data, start_date, end_date, selected_months, selected_countries, selected_cats):
        empty_fig = px.bar(title="No Data")

        if not data:
            return "0", "0", "0", "0%", "0%", "-", "-", "-", "-", "-", empty_fig, empty_fig, None

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

        if df.empty or 'Country' not in df.columns:
            return "0", "0", "0", "0%", "0%", "-", "-", "-", "-", "-", empty_fig, empty_fig, None

        # --- KPI CALCULATIONS ---

        # 1. Total Views
        total_views = df['Total_Views'].sum()

        # 2. Group by Country (Summing Views)
        country_stats = df.groupby('Country')['Total_Views'].sum()

        if country_stats.empty:
            return "0", "0", "0", "0%", "0%", "-", "-", "-", "-", "-", empty_fig, empty_fig, None

        # 3. Averages & Counts
        avg_views_country = round(country_stats.mean(), 1)
        active_countries = len(country_stats)

        # 4. Top & Low Country
        top_val = country_stats.max()
        top_name = country_stats.idxmax()
        top_str = f"{top_val} ({top_name})"

        low_val = country_stats.min()
        low_name = country_stats.idxmin()
        low_str = f"{low_val} ({low_name})"

        # 5. Market Share (Dominance)
        share_pct = (top_val / total_views * 100) if total_views > 0 else 0
        share_str = f"{share_pct:.1f}%"

        # 6. Top 3 Markets (Countries by Views)
        top3 = country_stats.nlargest(3)
        top3_str = ", ".join([f"{k}: {v}" for k, v in top3.items()])

        # 7. Top 3 Categories (by Views)
        if 'Job_Category' in df.columns:
            top3_cats = df.groupby('Job_Category')['Total_Views'].sum().nlargest(3)
            top3_cat_str = ", ".join([f"{k}: {v}" for k, v in top3_cats.items()])
        else:
            top3_cat_str = "-"

        # 8. Top 3 Companies (by Views)
        if 'Company' in df.columns:
            top3_comps = df.groupby('Company')['Total_Views'].sum().nlargest(3)
            top3_comp_str = ", ".join([f"{k}: {v}" for k, v in top3_comps.items()])
        else:
            top3_comp_str = "-"

        # 9. Conversion Rate
        total_apps = df['Total_Applications'].sum()
        conv_rate = (total_apps / total_views * 100) if total_views > 0 else 0

        # --- GRAPHS ---

        # Bar Graph (Top 20 Countries by Views)
        bar_df = country_stats.nlargest(20).reset_index(name='Views')
        fig_bar = px.bar(bar_df, x='Country', y='Views', text='Views', template="plotly_white")
        fig_bar.update_traces(marker_color='#17a2b8', textposition='outside')  # Cyan color
        fig_bar.update_layout(margin=dict(l=20, r=20, t=20, b=50), plot_bgcolor='rgba(0,0,0,0)')

        # Pie Graph (Share)
        pie_df = country_stats.nlargest(10).reset_index(name='Views')
        fig_pie = px.pie(pie_df, values='Views', names='Country', hole=0.4, template="plotly_white")
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), showlegend=True)

        # --- TABLE (Aggregated by Country) ---
        table_df = df.groupby('Country').agg({
            'Job_Title': 'count',
            'Total_Views': 'sum',
            'Total_Applications': 'sum'
        }).reset_index()

        table_df.columns = ['Country', 'Total Jobs', 'Total Views', 'Total Applications']
        table_df['Conversion (%)'] = (table_df['Total Applications'] / table_df['Total Views'] * 100).fillna(0).round(2)

        table = dash_table.DataTable(
            data=table_df.sort_values('Total Views', ascending=False).to_dict('records'),
            columns=[{'name': i, 'id': i} for i in table_df.columns],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Segoe UI'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ]
        )

        return (
            f"{total_views:,}",
            f"{avg_views_country}",
            f"{active_countries}",
            share_str,
            f"{conv_rate:.2f}%",
            top_str,
            low_str,
            top3_str,
            top3_cat_str,
            top3_comp_str,
            fig_bar,
            fig_pie,
            table
        )