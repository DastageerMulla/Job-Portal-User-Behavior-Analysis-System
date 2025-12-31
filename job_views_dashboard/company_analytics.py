import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import calendar
import numpy as np

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
        html.H2(value, className="fw-bold",
                style={'margin': '5px 0', 'fontSize': '1.4rem', 'lineHeight': '1.4', 'whiteSpace': 'normal',
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


def create_graph_card(title, graph_id):
    return dbc.Card([
        dbc.CardHeader(title, className="bg-transparent fw-bold border-0", style={'color': '#343a40'}),
        dbc.CardBody(dcc.Graph(id=graph_id, style={'height': '400px'}, config={'displayModeBar': False}))
    ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'}, className="mb-4")


# --- 3. LAYOUT ---
layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col(
            html.H3("Company & Traffic Analytics", className="my-4", style={'fontWeight': '800', 'color': '#2c3e50'}),
            width=12)
    ]),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Date Range", className="fw-bold small text-muted"),
            dcc.DatePickerRange(id='com-date-picker', display_format='YYYY-MM-DD', clearable=True,
                                style={'width': '100%', 'borderRadius': '8px'})
        ], width=12, md=3),
        dbc.Col([
            html.Label("Country", className="fw-bold small text-muted"),
            dcc.Dropdown(id='com-country-dropdown', multi=True, placeholder="All Countries")
        ], width=12, md=3),
        # UPDATED: Changed from Job Category to Company
        dbc.Col([
            html.Label("Company", className="fw-bold small text-muted"),
            dcc.Dropdown(id='com-company-dropdown', multi=True, placeholder="Select Companies")
        ], width=12, md=3),
        dbc.Col([
            html.Label("Traffic Source", className="fw-bold small text-muted"),
            dcc.Dropdown(id='com-traffic-dropdown', multi=True, placeholder="All Sources")
        ], width=12, md=3),
    ], className="p-4 mb-4 bg-white shadow-sm", style={'borderRadius': '15px', 'borderLeft': '5px solid #212529'}),

    # --- KPI CARDS ---

    # Row 1: Company Supply Stats
    dbc.Row([
        dbc.Col(create_solid_card("com-total", "Total Companies", "0", "Active Posters", "black"), width=12, sm=6, lg=4,
                className="mb-4"),
        dbc.Col(create_solid_card("com-avg-jobs", "Avg Jobs/Company", "0", "Mean Posting Volume", "blue"), width=12,
                sm=6, lg=4, className="mb-4"),
        dbc.Col(create_solid_card("com-top-jobs", "Top 3 Companies (Supply)", "-", "Highest Job Volume", "blue"),
                width=12, sm=12, lg=4, className="mb-4"),
    ]),

    # Row 2: Application Stats
    dbc.Row([
        dbc.Col(create_solid_card("com-total-apps", "Total Applications", "0", "Global Demand", "green"), width=12,
                sm=6, lg=4, className="mb-4"),
        dbc.Col(create_solid_card("com-avg-apps", "Avg Apps/Company", "0", "Mean Demand per Company", "green"),
                width=12, sm=6, lg=4, className="mb-4"),
        dbc.Col(create_solid_card("com-top-apps", "Top 3 Companies (Demand)", "-", "Highest Applications", "green"),
                width=12, sm=12, lg=4, className="mb-4"),
    ]),

    # Row 3: View Stats
    dbc.Row([
        dbc.Col(create_solid_card("com-total-views", "Total Views", "0", "Global Traffic", "cyan"), width=12, sm=6,
                lg=4, className="mb-4"),
        dbc.Col(create_solid_card("com-avg-views", "Avg Views/Company", "0", "Mean Traffic per Company", "cyan"),
                width=12, sm=6, lg=4, className="mb-4"),
        dbc.Col(create_solid_card("com-top-views", "Top 3 Companies (Traffic)", "-", "Highest Views", "cyan"), width=12,
                sm=12, lg=4, className="mb-4"),
    ]),

    # Row 4: Traffic Source Stats
    dbc.Row([
        dbc.Col(create_solid_card("com-total-sources", "Unique Traffic Sources", "0", "Channels Used", "orange"),
                width=12, sm=6, lg=4, className="mb-4"),
        dbc.Col(create_solid_card("com-top-source", "Top Traffic Source", "-", "Most Volume", "orange"), width=12, sm=6,
                lg=4, className="mb-4"),
        dbc.Col(create_solid_card("com-top3-sources", "Top 3 Traffic Sources", "-", "By Job Volume", "orange"),
                width=12, sm=12, lg=4, className="mb-4"),
    ]),

    # --- GRAPHS (Stacked Vertically) ---

    # 1. Traffic Source vs Applications (DONUT CHART)
    dbc.Row([
        dbc.Col(create_graph_card("1. Traffic Source Effectiveness (Applications)", "com-graph-traffic-apps"), width=12)
    ]),

    # 2. Traffic Source vs Views
    dbc.Row([
        dbc.Col(create_graph_card("2. Traffic Source Reach (Views)", "com-graph-traffic-views"), width=12)
    ]),

    # 3. Traffic Source vs Top 20 Companies
    dbc.Row([
        dbc.Col(create_graph_card("3. Traffic Source Distribution by Top 20 Companies", "com-graph-traffic-company"),
                width=12)
    ]),

    # 4. Job Posted Range vs Company Count
    dbc.Row([
        dbc.Col(create_graph_card("4. Company Posting Frequency (Job Count Ranges)", "com-graph-job-ranges"), width=12)
    ]),

    # --- TABLE ---
    dbc.Row([
        dbc.Col([
            html.H5("Detailed Company Performance Matrix", className="mb-3 text-muted fw-bold"),
            html.Div(id='com-table-container', style={'background': 'white', 'padding': '20px', 'borderRadius': '12px',
                                                      'boxShadow': '0 4px 12px rgba(0,0,0,0.05)'})
        ], width=12)
    ], className="mb-5")

], fluid=True)


# --- 4. CALLBACKS ---
def register_callbacks(app):
    # --- 1. Populate Dropdowns ---
    @app.callback(
        [Output('com-country-dropdown', 'options'),
         Output('com-company-dropdown', 'options'),  # Updated Output
         Output('com-traffic-dropdown', 'options')],
        Input('global-data-store', 'data')
    )
    def update_filters(data):
        if not data: return [], [], []
        df = pd.DataFrame(data)
        countries = [{'label': c, 'value': c} for c in
                     sorted(df['Country'].dropna().unique().astype(str))] if 'Country' in df.columns else []

        # Updated: Get Companies instead of Categories
        comps = [{'label': c, 'value': c} for c in
                 sorted(df['Company'].dropna().unique().astype(str))] if 'Company' in df.columns else []

        sources = [{'label': c, 'value': c} for c in
                   sorted(df['Traffic_Source'].dropna().unique().astype(str))] if 'Traffic_Source' in df.columns else []

        return countries, comps, sources

    # --- 2. Update Analytics ---
    @app.callback(
        [
            # Row 1 (Company Supply)
            Output('com-total', 'children'), Output('com-avg-jobs', 'children'), Output('com-top-jobs', 'children'),
            # Row 2 (Apps)
            Output('com-total-apps', 'children'), Output('com-avg-apps', 'children'),
            Output('com-top-apps', 'children'),
            # Row 3 (Views)
            Output('com-total-views', 'children'), Output('com-avg-views', 'children'),
            Output('com-top-views', 'children'),
            # Row 4 (Traffic)
            Output('com-total-sources', 'children'), Output('com-top-source', 'children'),
            Output('com-top3-sources', 'children'),
            # Graphs
            Output('com-graph-traffic-apps', 'figure'),
            Output('com-graph-traffic-views', 'figure'),
            Output('com-graph-traffic-company', 'figure'),
            Output('com-graph-job-ranges', 'figure'),
            # Table
            Output('com-table-container', 'children')
        ],
        [
            Input('global-data-store', 'data'),
            Input('com-date-picker', 'start_date'),
            Input('com-date-picker', 'end_date'),
            Input('com-country-dropdown', 'value'),
            Input('com-company-dropdown', 'value'),  # Updated Input
            Input('com-traffic-dropdown', 'value')
        ]
    )
    def update_analytics(data, start_date, end_date, selected_countries, selected_companies, selected_sources):
        empty_fig = px.bar(title="No Data")

        # Helper for Card Content
        def make_content(title, val, sub):
            return [
                html.H6(title, className="text-uppercase fw-bold",
                        style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
                html.H2(val, className="fw-bold",
                        style={'margin': '5px 0', 'fontSize': '1.4rem', 'lineHeight': '1.4', 'whiteSpace': 'normal',
                               'wordWrap': 'break-word'}),
                html.Small(sub, style={'fontSize': '0.75rem', 'opacity': '0.8'})
            ]

        defaults = [make_content("Metric", "0", "No Data")] * 12 + [empty_fig, empty_fig, empty_fig, empty_fig, None]

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
        if selected_countries and 'Country' in df.columns:
            df = df[df['Country'].isin(selected_countries)]

        # Updated: Filter by Company
        if selected_companies and 'Company' in df.columns:
            df = df[df['Company'].isin(selected_companies)]

        if selected_sources and 'Traffic_Source' in df.columns:
            df = df[df['Traffic_Source'].isin(selected_sources)]

        if df.empty or 'Company' not in df.columns:
            return defaults

        # --- AGGREGATION LOGIC ---

        # Group by Company
        comp_stats = df.groupby('Company').agg({
            'Job_Title': 'count',
            'Total_Applications': 'sum',
            'Total_Views': 'sum'
        }).rename(columns={'Job_Title': 'Job_Count'})

        # Group by Traffic Source
        traffic_stats = df.groupby('Traffic_Source').agg({
            'Job_Title': 'count',
            'Total_Applications': 'sum',
            'Total_Views': 'sum'
        }).rename(columns={'Job_Title': 'Job_Count'})

        # --- KPI CALCULATIONS ---

        # Row 1: Company Supply
        total_companies = len(comp_stats)
        avg_jobs = round(comp_stats['Job_Count'].mean(), 1)
        top3_jobs = comp_stats['Job_Count'].nlargest(3)
        top3_jobs_str = ", ".join([f"{idx} ({val})" for idx, val in top3_jobs.items()])

        # Row 2: Applications
        total_apps = df['Total_Applications'].sum()
        avg_apps = round(comp_stats['Total_Applications'].mean(), 1)
        top3_apps = comp_stats['Total_Applications'].nlargest(3)
        top3_apps_str = ", ".join([f"{idx} ({val})" for idx, val in top3_apps.items()])

        # Row 3: Views
        total_views = df['Total_Views'].sum()
        avg_views = round(comp_stats['Total_Views'].mean(), 1)
        top3_views = comp_stats['Total_Views'].nlargest(3)
        top3_views_str = ", ".join([f"{idx} ({val})" for idx, val in top3_views.items()])

        # Row 4: Traffic
        total_sources = len(traffic_stats)
        top_source = traffic_stats['Job_Count'].idxmax() if not traffic_stats.empty else "-"
        top_source_val = traffic_stats['Job_Count'].max() if not traffic_stats.empty else 0
        top3_sources = traffic_stats['Job_Count'].nlargest(3)
        top3_sources_str = ", ".join([f"{idx} ({val})" for idx, val in top3_sources.items()])

        # --- GRAPHS ---

        # 1. Traffic Source vs Applications (DONUT CHART)
        traffic_apps_df = traffic_stats.sort_values('Total_Applications', ascending=False).reset_index().head(10)

        fig_traffic_apps = px.pie(traffic_apps_df, values='Total_Applications', names='Traffic_Source',
                                  hole=0.4, template="plotly_white", title="Applications by Traffic Source")
        fig_traffic_apps.update_traces(textposition='inside', textinfo='percent+label')
        fig_traffic_apps.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=True)

        # 2. Traffic Source vs Views
        traffic_views_df = traffic_stats.sort_values('Total_Views', ascending=False).reset_index().head(15)
        fig_traffic_views = px.bar(traffic_views_df, x='Traffic_Source', y='Total_Views',
                                   text='Total_Views', template="plotly_white", title="Views by Traffic Source")
        fig_traffic_views.update_traces(marker_color='#0dcaf0')
        fig_traffic_views.update_layout(plot_bgcolor='rgba(0,0,0,0)')

        # 3. Traffic Source vs Top 20 Companies (Stacked Bar)
        top20_comps = comp_stats.nlargest(20, 'Job_Count').index
        df_top20 = df[df['Company'].isin(top20_comps)]
        comp_traffic = df_top20.groupby(['Company', 'Traffic_Source']).size().reset_index(name='Count')

        fig_comp_traffic = px.bar(comp_traffic, x='Company', y='Count', color='Traffic_Source',
                                  title="Traffic Source Distribution for Top 20 Companies", template="plotly_white")
        fig_comp_traffic.update_layout(plot_bgcolor='rgba(0,0,0,0)', barmode='stack')

        # 4. Job Posted Range vs Company Count
        bins = [0, 1, 5, 10, 15, 20, 25, 10000]
        labels = ['1', '2-5', '6-10', '11-15', '16-20', '21-25', '25+']

        comp_stats['Job_Range'] = pd.cut(comp_stats['Job_Count'], bins=bins, labels=labels, right=True)

        range_counts = comp_stats['Job_Range'].value_counts().reindex(labels).reset_index()
        range_counts.columns = ['Job Range', 'Company Count']

        fig_ranges = px.bar(range_counts, x='Job Range', y='Company Count', text='Company Count',
                            title="Company Distribution by Job Posting Volume", template="plotly_white")
        fig_ranges.update_traces(marker_color='#6610f2')
        fig_ranges.update_layout(plot_bgcolor='rgba(0,0,0,0)')

        # --- TABLE ---
        table_df = comp_stats.reset_index().sort_values('Job_Count', ascending=False)
        table_df['Avg Apps/Job'] = (table_df['Total_Applications'] / table_df['Job_Count']).round(1)
        table_df['Avg Views/Job'] = (table_df['Total_Views'] / table_df['Job_Count']).round(1)

        top_traffic_per_comp = df.groupby('Company')['Traffic_Source'].agg(
            lambda x: x.mode()[0] if not x.mode().empty else "-").reset_index()
        table_df = pd.merge(table_df, top_traffic_per_comp, on='Company', how='left')

        cols_order = ['Company', 'Job_Count', 'Total_Applications', 'Avg Apps/Job', 'Total_Views', 'Avg Views/Job',
                      'Traffic_Source']

        table = dash_table.DataTable(
            data=table_df.head(50).to_dict('records'),
            columns=[{'name': i.replace('_', ' '), 'id': i} for i in cols_order],
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
            make_content("Total Companies", f"{total_companies}", "Active Posters"),
            make_content("Avg Jobs/Company", f"{avg_jobs}", "Mean Volume"),
            make_content("Top 3 Companies (Supply)", top3_jobs_str, "Most Jobs"),
            # Row 2
            make_content("Total Applications", f"{total_apps:,}", "Global Demand"),
            make_content("Avg Apps/Company", f"{avg_apps}", "Mean Demand"),
            make_content("Top 3 Companies (Demand)", top3_apps_str, "Most Apps"),
            # Row 3
            make_content("Total Views", f"{total_views:,}", "Global Traffic"),
            make_content("Avg Views/Company", f"{avg_views}", "Mean Traffic"),
            make_content("Top 3 Companies (Traffic)", top3_views_str, "Most Views"),
            # Row 4
            make_content("Unique Traffic Sources", f"{total_sources}", "Channels"),
            make_content("Top Traffic Source", f"{top_source}", f"{top_source_val} Jobs"),
            make_content("Top 3 Traffic Sources", top3_sources_str, "By Job Volume"),
            # Graphs
            fig_traffic_apps,
            fig_traffic_views,
            fig_comp_traffic,
            fig_ranges,
            # Table
            table
        )