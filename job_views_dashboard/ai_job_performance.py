import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import numpy as np

# --- 1. COLOR THEMES ---
CARD_THEMES = {
    'black': {'bg': 'linear-gradient(135deg, #212529 0%, #343a40 100%)', 'text': '#ffffff'},
    'blue': {'bg': 'linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)', 'text': '#ffffff'},
    'green': {'bg': 'linear-gradient(135deg, #198754 0%, #146c43 100%)', 'text': '#ffffff'},
    'cyan': {'bg': 'linear-gradient(135deg, #0dcaf0 0%, #0aa2c0 100%)', 'text': '#ffffff'},
    'orange': {'bg': 'linear-gradient(135deg, #fd7e14 0%, #e35d0b 100%)', 'text': '#ffffff'},
}


# --- 2. HELPER FUNCTION ---
def create_solid_card(card_id, title, value, subtext, theme_key):
    theme = CARD_THEMES.get(theme_key, CARD_THEMES['black'])
    return html.Div([
        html.H6(title, className="text-uppercase fw-bold",
                style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
        html.H2(value, className="fw-bold", style={'margin': '5px 0', 'fontSize': '2rem'}),
        html.Small(subtext, style={'fontSize': '0.8rem', 'opacity': '0.8'})
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
        dbc.Col([
            html.H3("AI Job Performance Simulator (XGBoost)", className="my-4",
                    style={'fontWeight': '800', 'color': '#2c3e50'}),
            html.P(
                "Predict the expected Views and Applications for a new job posting based on historical performance patterns.",
                className="text-muted")
        ], width=12)
    ]),

    # --- INPUT SECTION (White Box) ---
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("1. Configure Job Details", className="bg-transparent fw-bold border-0"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Target Country", className="fw-bold small text-muted"),
                            dcc.Dropdown(id='ai-country-input', placeholder="e.g., United States")
                        ], width=12, md=5),
                        dbc.Col([
                            html.Label("Select Job Category", className="fw-bold small text-muted"),
                            dcc.Dropdown(id='ai-category-input', placeholder="e.g., IT & Software")
                        ], width=12, md=5),
                        dbc.Col([
                            html.Label("Action", className="fw-bold small text-muted"),
                            dbc.Button("Predict Performance", id="ai-predict-btn", color="primary",
                                       className="w-100 fw-bold")
                        ], width=12, md=2, style={'display': 'flex', 'alignItems': 'flex-end'}),
                    ])
                ])
            ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'},
                className="mb-4")
        ], width=12)
    ]),

    # --- PREDICTION RESULTS ---
    html.Div(id='ai-prediction-container', style={'display': 'none'}, children=[

        html.H5("Predicted 30-Day Performance", className="mb-3 text-muted fw-bold"),

        # KPI Cards
        dbc.Row([
            dbc.Col(create_solid_card("pred-views", "Predicted Views", "0", "Est. Traffic (30 Days)", "cyan"), width=12,
                    sm=6, lg=4, className="mb-4"),
            dbc.Col(create_solid_card("pred-apps", "Predicted Applications", "0", "Est. Demand (30 Days)", "green"),
                    width=12, sm=6, lg=4, className="mb-4"),
            dbc.Col(create_solid_card("pred-conv", "Expected Conversion", "0%", "Apps / Views Ratio", "orange"),
                    width=12, sm=6, lg=4, className="mb-4"),
        ]),

        # --- GRAPHS (Stacked Vertically) ---

        # Graph 1: Prediction vs Average
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Prediction vs. Global Average", className="bg-transparent fw-bold border-0"),
                dbc.CardBody(
                    dcc.Graph(id='ai-comparison-graph', style={'height': '350px'}, config={'displayModeBar': False}))
            ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'},
                className="mb-4"), width=12),
        ]),

        # Graph 2: Feature Importance
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("What drives this prediction?", className="bg-transparent fw-bold border-0"),
                dbc.CardBody(
                    dcc.Graph(id='ai-importance-graph', style={'height': '350px'}, config={'displayModeBar': False}))
            ], style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': 'none'},
                className="mb-4"), width=12),
        ])
    ]),

    # Loading Spinner
    dcc.Loading(id="loading-prediction", type="circle", children=html.Div(id="dummy-output"))

], fluid=True)


# --- 4. CALLBACKS ---
def register_callbacks(app):
    # 1. Populate Dropdowns
    @app.callback(
        [Output('ai-country-input', 'options'),
         Output('ai-category-input', 'options')],
        Input('global-data-store', 'data')
    )
    def populate_ai_dropdowns(data):
        if not data: return [], []
        df = pd.DataFrame(data)
        countries = [{'label': c, 'value': c} for c in sorted(df['Country'].dropna().unique().astype(str))]
        cats = [{'label': c, 'value': c} for c in sorted(df['Job_Category'].dropna().unique().astype(str))]
        return countries, cats

    # 2. Run XGBoost Prediction
    @app.callback(
        [
            Output('ai-prediction-container', 'style'),
            Output('pred-views', 'children'),
            Output('pred-apps', 'children'),
            Output('pred-conv', 'children'),
            Output('ai-comparison-graph', 'figure'),
            Output('ai-importance-graph', 'figure'),
            Output('dummy-output', 'children')
        ],
        [Input('ai-predict-btn', 'n_clicks')],
        [
            State('ai-country-input', 'value'),
            State('ai-category-input', 'value'),
            State('global-data-store', 'data')
        ]
    )
    def run_prediction(n_clicks, country, category, data):
        if not n_clicks or not country or not category or not data:
            return {'display': 'none'}, "", "", "", {}, {}, ""

        df = pd.DataFrame(data)

        # --- A. DATA PREPARATION FOR XGBOOST ---
        # We need to convert Text -> Numbers (Encoding)

        # 1. Select relevant columns
        model_df = df[['Country', 'Job_Category', 'Total_Views', 'Total_Applications']].dropna()

        # 2. Remove outliers for better training (Optional but recommended)
        # Removing extreme viral hits to predict "typical" performance
        q_hi = model_df["Total_Applications"].quantile(0.95)
        model_df = model_df[model_df["Total_Applications"] < q_hi]

        # 3. Label Encoding
        le_country = LabelEncoder()
        le_category = LabelEncoder()

        model_df['Country_Code'] = le_country.fit_transform(model_df['Country'])
        model_df['Category_Code'] = le_category.fit_transform(model_df['Job_Category'])

        # 4. Features (X) and Targets (y)
        X = model_df[['Country_Code', 'Category_Code']]
        y_views = model_df['Total_Views']
        y_apps = model_df['Total_Applications']

        # --- B. TRAIN MODELS ---
        # We train two separate models: one for Views, one for Apps

        # Model 1: Views
        xgb_views = XGBRegressor(n_estimators=50, learning_rate=0.1, max_depth=3, random_state=42)
        xgb_views.fit(X, y_views)

        # Model 2: Applications
        xgb_apps = XGBRegressor(n_estimators=50, learning_rate=0.1, max_depth=3, random_state=42)
        xgb_apps.fit(X, y_apps)

        # --- C. PREDICT FOR USER INPUT ---

        # Encode the user input
        try:
            # Handle case where input might not be in training data (unlikely with dropdowns)
            input_country_code = le_country.transform([country])[0]
            input_category_code = le_category.transform([category])[0]
        except ValueError:
            # Fallback for unseen labels
            input_country_code = 0
            input_category_code = 0

        input_data = np.array([[input_country_code, input_category_code]])

        # Get Predictions
        pred_views = max(0, int(xgb_views.predict(input_data)[0]))  # Ensure no negative predictions
        pred_apps = max(0, int(xgb_apps.predict(input_data)[0]))

        # Calculate Conversion
        pred_conv = (pred_apps / pred_views * 100) if pred_views > 0 else 0

        # --- D. VISUALIZATIONS ---

        # 1. Comparison Graph (Bar Chart)
        # Compare Prediction vs Global Average for that Category
        global_avg_apps = model_df[model_df['Job_Category'] == category]['Total_Applications'].mean()

        comp_data = pd.DataFrame({
            'Metric': ['Your Prediction', 'Global Average (Category)'],
            'Applications': [pred_apps, global_avg_apps],
            'Color': ['Prediction', 'Average']
        })

        fig_comp = px.bar(comp_data, x='Metric', y='Applications', color='Color',
                          title=f"Predicted vs Average for {category}",
                          color_discrete_map={'Prediction': '#198754', 'Average': '#6c757d'},
                          template="plotly_white", text_auto='.0f')
        fig_comp.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False)

        # 2. Feature Importance (Simple representation)
        # Since we only have 2 features, we show which one weighed more
        importance = xgb_apps.feature_importances_
        feat_df = pd.DataFrame({
            'Feature': ['Country', 'Job Category'],
            'Importance': importance
        })

        fig_imp = px.pie(feat_df, values='Importance', names='Feature',
                         title="What influenced this prediction?",
                         hole=0.4, template="plotly_white",
                         color_discrete_sequence=['#0d6efd', '#fd7e14'])

        # --- E. RETURN CONTENT ---

        # Helper to format card content
        def make_content(title, val, sub):
            return [
                html.H6(title, className="text-uppercase fw-bold",
                        style={'fontSize': '0.75rem', 'opacity': '0.9', 'marginBottom': '5px'}),
                html.H2(val, className="fw-bold", style={'margin': '5px 0', 'fontSize': '2rem'}),
                html.Small(sub, style={'fontSize': '0.8rem', 'opacity': '0.8'})
            ]

        return (
            {'display': 'block'},  # Show container
            make_content("Predicted Views", f"{pred_views:,}", f"In {country}"),
            make_content("Predicted Applications", f"{pred_apps:,}", f"In {country}"),
            make_content("Expected Conversion", f"{pred_conv:.1f}%", "Apps / Views"),
            fig_comp,
            fig_imp,
            ""
        )