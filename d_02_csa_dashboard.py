import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table

import pandas as pd

from csa_app.database import DatabaseSqlLite


database = DatabaseSqlLite()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for charts
df = database.lookup_sentiment_summaries(return_limit=10)
query_count = 0

COL_SENTIMENT = "sentiment"
COL_METHOD = "method"
COL_TOPIC = "topic"

ANY_VALUE = "!any!"

lst_columns = [
    {"label":"Sentiment","value":COL_SENTIMENT},
    {"label":"Method", "value":COL_METHOD},
    {"label":'Topic', "value":COL_TOPIC}
]


default_top_left_column = COL_SENTIMENT
default_top_right_column = COL_TOPIC


# Pie chart configuration
pie_chart = dcc.Graph(
    id="pie-chart",
    figure=px.pie(),
)

# Bar chart configuration
bar_chart = dcc.Graph(
    id="bar-chart", figure=px.bar()
)

# Map with timeline
map_timeline = dcc.Graph(
    id="map-timeline",
    figure=px.scatter_geo(),
    #px.scatter_geo(
    #    df,
    #    locations="iso_alpha",
    #    color="continent",
    #    hover_name="country",
    #    size="pop",
    #    animation_frame="year",
    #    projection="natural earth",
    #),
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
                                id="search-contributor",
                                placeholder="Cause lookup...",
                                type="text",
                            ),
                            dcc.Dropdown(
                                id="dropdown-contributor",
                                options=[
                                    {"label": "Any", "value": ANY_VALUE},
                                    {"label": "Option 2", "value": "2"},
                                ],
                                value=ANY_VALUE,
                            ),
                        ],
                        className="d-inline-block ml-auto",
                    ),
                    html.Div(
                        [
                            dbc.Input(
                                id="search-method",
                                placeholder="Action lookup...",
                                type="text",
                            ),
                            dcc.Dropdown(
                                id="dropdown-method",
                                options=[
                                    {"label": "Any", "value": ANY_VALUE},
                                    {"label": "Option 2", "value": "2"},
                                ],
                                value=ANY_VALUE,
                            ),
                        ],
                        className="d-inline-block mx-2",
                    ),
                    html.Div(
                        [
                            dbc.Input(
                                id="search-topic",
                                placeholder="Topic lookup...",
                                type="text",
                            ),
                            dcc.Dropdown(
                                id="dropdown-topic",
                                options=[
                                    {"label": "Any", "value": ANY_VALUE},
                                    {"label": "Option 2", "value": "2"},
                                ],
                                value=ANY_VALUE,
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
        dcc.Loading(
            id="loading-screen",
            type="circle",
            children=html.Div(
                children=[
                    dcc.Store(id='data-loading-number', storage_type='memory'),
                    html.Div(
                        [
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Justifications"),
                                        dash_table.DataTable(id='tbl_justifications')
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
                                dbc.Col(html.Div(
                                    children=[
                                        pie_chart,
                                        # Dropdown to select the pie column
                                        dcc.Dropdown(
                                            id='pie-dropdown-column',
                                            options=lst_columns,
                                            value=default_top_left_column, 
                                        )
                                    ],
                                ), width=6),
                                dbc.Col(html.Div(
                                    children=[
                                        # Dropdown to select the x-column of bar chart
                                        dcc.Dropdown(
                                            id='bar-dropdown-column',
                                            options=lst_columns,
                                            value=default_top_right_column
                                        ),
                                        bar_chart,
                                    ],
                                ), width=6),
                            ]
                        ),
                        dbc.Row([dbc.Col(map_timeline, width=12)]),
                    ],
                    id="main-content",
                    style={"margin-left": "20%", "margin-right": "20%", "padding": "10px"},
                ),  # Adjust based on side panels
            ]
            ),
            target_components={"data-loading-number": "data" }
        )
    ],
)


# Callback to update the bar chart based on dropdown selection
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('bar-dropdown-column', 'value')]
)
def update_bar_chart(selected_column):
    # Create the bar chart

    grouped_df = df.groupby([selected_column, COL_SENTIMENT]).size().reset_index(name='Count')

    print(grouped_df.head())
    fig = px.bar(grouped_df, x=selected_column, y="Count", color=COL_SENTIMENT)
    return fig


# Callback to update the bar chart based on dropdown selection
@app.callback(
    Output('pie-chart', 'figure'),
    [
        Input('pie-dropdown-column', 'value'),
        Input('data-loading-number', 'data')
    ]
)
def update_pie_chart(selected_column, _):
    # Create the bar chart
    fig = px.pie(df, names=selected_column, values="pop")
    return fig


@app.callback(
    Output('data-loading-number', 'data'),
    [
        Input('dropdown-contributor', 'value'),
        Input('dropdown-method', 'value'),
        Input('dropdown-topic', 'value'),
    ]
)
def update_data(contributor_id, method_id, topic_id):

    if contributor_id == ANY_VALUE:
        contributor_id = None
    if method_id == ANY_VALUE:
        method_id = None
    if topic_id == ANY_VALUE:
        topic_id = None
    # Create the bar chart
    global query_count
    global df

    df = database.lookup_sentiment_summaries(
        topic_id=topic_id,
        method_id=method_id,
        contributor_id=contributor_id,
    )
    import time
    time.sleep(3)
    query_count += 1
    return query_count

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
    app.run(debug=True)
