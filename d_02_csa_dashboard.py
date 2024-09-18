import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for charts
df = px.data.gapminder()

# Pie chart configuration (example)
pie_chart = dcc.Graph(
    id="pie-chart",
    figure=px.pie(df, names="continent", values="pop", title="Pie Chart"),
)

# Bar chart configuration (example)
bar_chart = dcc.Graph(
    id="bar-chart", figure=px.bar(df, x="continent", y="pop", title="Bar Chart")
)

# Map with timeline (example)
map_timeline = dcc.Graph(
    id="map-timeline",
    figure=px.scatter_geo(
        df,
        locations="iso_alpha",
        color="continent",
        hover_name="country",
        size="pop",
        animation_frame="year",
        projection="natural earth",
    ),
)

# Layout
app.layout = html.Div(
    [
        # Top toolbar with toggle buttons
        dbc.Navbar(
            dbc.Container(
                [
                    html.Div(
                        [
                            html.H1("Content Sentiment Browser"),
                        ],
                        className="d-inline-block ml-auto",
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                "Toggle Justifications List",
                                id="toggle-left",
                            ),
                        ],
                        className="d-inline-block ml-auto",
                    ),
                    html.Div(
                        [
                            dbc.Input(
                                id="search-1",
                                placeholder="Cause lookup...",
                                type="text",
                            ),
                            dcc.Dropdown(
                                id="dropdown-1",
                                options=[
                                    {"label": "Option 1", "value": "1"},
                                    {"label": "Option 2", "value": "2"},
                                ],
                                value="1",
                            ),
                        ],
                        className="d-inline-block ml-auto",
                    ),
                    html.Div(
                        [
                            dbc.Input(
                                id="search-2",
                                placeholder="Action lookup...",
                                type="text",
                            ),
                            dcc.Dropdown(
                                id="dropdown-2",
                                options=[
                                    {"label": "Option 1", "value": "1"},
                                    {"label": "Option 2", "value": "2"},
                                ],
                                value="1",
                            ),
                        ],
                        className="d-inline-block mx-2",
                    ),
                    html.Div(
                        [
                            dbc.Input(
                                id="search-3",
                                placeholder="Topic lookup...",
                                type="text",
                            ),
                            dcc.Dropdown(
                                id="dropdown-3",
                                options=[
                                    {"label": "Option 1", "value": "1"},
                                    {"label": "Option 2", "value": "2"},
                                ],
                                value="1",
                            ),
                        ],
                        className="d-inline-block mx-2",
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                "Toggle Content List",
                                id="toggle-right",
                            ),
                        ],
                        className="d-inline-block ml-auto",
                    ),
                ]
            ),
            color="dark",
            dark=True,
            className="mb-4",
        ),
        # Collapsible left panel (Facts)
        html.Div(
            [
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Justifications"),
                                html.Ul(
                                    [html.Li(f"Fact {i}") for i in range(1, 6)]
                                ),  # Example facts
                            ]
                        )
                    ),
                    id="collapse-left",
                    is_open=True,
                ),
            ],
            id="left-panel",
            style={
                "float": "left",
                "width": "20%",
                "padding": "10px",
                "display": "block",
                "background-color": "#DDD",
            },
        ),
        # Collapsible right panel (Content)
        html.Div(
            [
                dbc.Collapse(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Content"),
                                dcc.Checklist(
                                    id="content-list",
                                    options=[
                                        {
                                            "label": f"Content {i}",
                                            "value": f"content-{i}",
                                        }
                                        for i in range(1, 6)
                                    ],
                                    value=["content-1"],
                                ),
                                html.Div(id="content-display"),
                            ]
                        )
                    ),
                    id="collapse-right",
                    is_open=True,
                ),
            ],
            id="right-panel",
            style={
                "float": "right",
                "width": "20%",
                "padding": "10px",
                "display": "block",
                "background-color": "#DDD",
            },
        ),
        # Main body for charts and map
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(pie_chart, width=6),
                        dbc.Col(bar_chart, width=6),
                    ]
                ),
                dbc.Row([dbc.Col(map_timeline, width=12)]),
            ],
            id="main-content",
            style={"margin-left": "20%", "margin-right": "20%", "padding": "10px"},
        ),  # Adjust based on side panels
    ]
)


# Callbacks for collapsible panels
@app.callback(
    [
        Output("collapse-left", "is_open"),
        Output("collapse-right", "is_open"),
        Output("left-panel", "style"),
        Output("right-panel", "style"),
        Output("main-content", "style"),
    ],
    [Input("toggle-left", "n_clicks"), Input("toggle-right", "n_clicks")],
    [State("collapse-left", "is_open"), State("collapse-right", "is_open")],
)
def toggle_panels(n_left, n_right, is_left_open, is_right_open):
    ctx = dash.callback_context
    left_style = {"float": "left", "width": "20%", "padding": "10px"}
    right_style = {"float": "right", "width": "20%", "padding": "10px"}
    main_content_style = {"padding": "10px"}

    # Determine which button was clicked
    if ctx.triggered and "toggle-left" in ctx.triggered[0]["prop_id"]:
        is_left_open = not is_left_open
    if ctx.triggered and "toggle-right" in ctx.triggered[0]["prop_id"]:
        is_right_open = not is_right_open

    # Adjust main content style based on collapsed panels
    if not is_left_open and not is_right_open:
        main_content_style["margin-left"] = "0%"
        main_content_style["margin-right"] = "0%"
    elif not is_left_open:
        main_content_style["margin-left"] = "0%"
        main_content_style["margin-right"] = "20%"
    elif not is_right_open:
        main_content_style["margin-left"] = "20%"
        main_content_style["margin-right"] = "0%"
    else:
        main_content_style["margin-left"] = "20%"
        main_content_style["margin-right"] = "20%"

    # Hide left and right panels if they are collapsed
    left_style["display"] = "block" if is_left_open else "none"
    right_style["display"] = "block" if is_right_open else "none"

    return is_left_open, is_right_open, left_style, right_style, main_content_style


# Callback to update content display based on checklist
@app.callback(Output("content-display", "children"), [Input("content-list", "value")])
def display_content(selected_contents):
    if selected_contents:
        return html.Div(
            [html.P(f"Showing details for {content}") for content in selected_contents]
        )
    return html.P("No content selected.")


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
