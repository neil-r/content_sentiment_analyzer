import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

from csa_app.database import DatabaseSqlLite
from csa_app.synset_database import SynsetDatabaseWordNet


database = DatabaseSqlLite()
synset_database = SynsetDatabaseWordNet()

synset_database.get_noun_synsets("events")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for charts
df = database.lookup_sentiment_summaries(return_limit=1000)
query_count = 0

COL_SENTIMENT = "sentiment"
COL_METHOD = "method"
COL_CONTRIBUTOR = "contributor"
COL_TOPIC = "topic"

ANY_VALUE = "!any!"

lst_columns = [
    {"label": "Sentiment", "value": COL_SENTIMENT},
    {"label": "Method", "value": COL_METHOD},
    {"label": "Contributor", "value": COL_CONTRIBUTOR},
    {"label": "Topic", "value": COL_TOPIC},
]


def convert_sentiment_col(series):
    return [
        "Neutral" if s is None else "Negative" if s == 0.0 else "Positive"
        for s in series
    ]


SENTIMENT_COLORS = {
    "Positive": "#1f77b4",  # blue
    "Negative": "#ff7f0e",  # orange
    "Neutral": "#2ca02c",  # green
}


DEFAULT_TOP_LEFT_COLUMN = COL_SENTIMENT
DEFAULT_TOP_RIGHT_COLUMN = COL_TOPIC


# Pie chart configuration
pie_chart = dcc.Graph(
    id="pie-chart",
    figure=px.pie(),
)

# Bar chart configuration
bar_chart = dcc.Graph(id="bar-chart", figure=px.bar())

# Map with timeline
map_timeline = dcc.Graph(
    id="map-timeline",
    figure=px.scatter_geo(),
    # px.scatter_geo(
    #    df,
    #    locations="iso_alpha",
    #    color="continent",
    #    hover_name="country",
    #    size="pop",
    #    animation_frame="year",
    #    projection="natural earth",
    # ),
)

side_panel = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5("Filter Options"),
                        html.P("Contributor", style={"padding-top": "10px"}),
                        dbc.Input(
                            id="txt-s-cont",
                            placeholder="Contributor lookup...",
                            type="text",
                            debounce=True,
                        ),
                        dcc.Dropdown(
                            id="dropdown-contributor",
                            options=[
                                {"label": "Any", "value": ANY_VALUE},
                            ],
                            value=ANY_VALUE,
                            clearable=False,
                            style={
                                "white-space": "nowrap",
                                "text-overflow": "ellipsis",
                            },
                        ),
                        html.P("Methods", style={"padding-top": "10px"}),
                        dbc.Input(
                            id="txt-s-method",
                            placeholder="Method lookup...",
                            type="text",
                            debounce=True,
                        ),
                        dcc.Dropdown(
                            id="dropdown-method",
                            options=[
                                {"label": "Any", "value": ANY_VALUE},
                            ],
                            value=ANY_VALUE,
                            clearable=False,
                            style={
                                "white-space": "nowrap",
                                "text-overflow": "ellipsis",
                            },
                        ),
                        html.P("Topics", style={"padding-top": "10px"}),
                        dbc.Input(
                            id="txt-s-topic",
                            placeholder="Topic lookup...",
                            type="text",
                            debounce=True,
                        ),
                        dcc.Dropdown(
                            id="dropdown-topic",
                            options=[
                                {"label": "Any", "value": ANY_VALUE},
                            ],
                            clearable=False,
                            style={
                                "white-space": "nowrap",
                                "text-overflow": "ellipsis",
                            },
                            value=ANY_VALUE,
                        ),
                    ]
                )
            ]
        )
    ]
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
                    html.H3("Content Sentiment Analysis"),
                ]
            ),
            className="mb-4",
        ),
        # Collapsible left panel (Facts)
        dcc.Store(id="data-loading-number", storage_type="memory"),
        html.Div(
            [
                dbc.Collapse(
                    children=side_panel,
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
        html.Div(
            [
                dcc.Loading(
                    id="loading-screen",
                    type="circle",
                    children=html.Div(
                        children=[
                            # Main body
                            html.Div(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div(
                                                    children=[
                                                        pie_chart,
                                                        # Dropdown to select the pie column
                                                        dcc.Dropdown(
                                                            id="pie-dropdown-column",
                                                            options=lst_columns,
                                                            value=DEFAULT_TOP_LEFT_COLUMN,
                                                            clearable=False,
                                                        ),
                                                    ],
                                                ),
                                                width=6,
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    children=[
                                                        # Dropdown to select the x-column of bar chart
                                                        dcc.Dropdown(
                                                            id="bar-dropdown-column",
                                                            options=lst_columns,
                                                            value=DEFAULT_TOP_RIGHT_COLUMN,
                                                            clearable=False,
                                                        ),
                                                        bar_chart,
                                                    ],
                                                ),
                                                width=6,
                                            ),
                                        ]
                                    ),
                                    dbc.Row([dbc.Col(map_timeline, width=12)]),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div(
                                                    children=[
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
                                                ),
                                                width=12,
                                            )
                                        ]
                                    ),
                                ],
                                style={
                                    "padding": "10px",
                                },
                            ),  # Adjust based on side panels
                        ]
                    ),
                    target_components={"data-loading-number": "data"},
                ),
            ],
            id="main-content",
            style={
                "margin-left": "20%",
                "padding": "10px",
            },
        ),
    ],
)


# Callback to update the bar chart based on dropdown selection
@app.callback(Output("bar-chart", "figure"), [Input("bar-dropdown-column", "value")])
def update_bar_chart(selected_column: str):
    # Create the bar chart
    grouped_df = (
        df.groupby([selected_column, COL_SENTIMENT]).size().reset_index(name="Count")
    )

    grouped_df[COL_SENTIMENT] = convert_sentiment_col(grouped_df[COL_SENTIMENT])

    print(grouped_df.head())
    fig = px.bar(
        grouped_df,
        x=selected_column,
        y="Count",
        color=COL_SENTIMENT,
        color_discrete_map=SENTIMENT_COLORS,
    )

    return fig


# Callback to update the bar chart based on dropdown selection
@app.callback(
    Output("pie-chart", "figure"),
    [Input("pie-dropdown-column", "value"), Input("data-loading-number", "data")],
)
def update_pie_chart(selected_column, _):
    # Create the bar chart
    grouped_df = df.groupby([selected_column]).size().reset_index(name="Count")

    grouped_df[COL_SENTIMENT] = convert_sentiment_col(grouped_df[COL_SENTIMENT])

    fig = px.pie(
        grouped_df,
        names=selected_column,
        values="Count",
        color_discrete_map=SENTIMENT_COLORS,
    )
    return fig


@app.callback(
    Output("data-loading-number", "data"),
    [
        Input("dropdown-contributor", "value"),
        Input("dropdown-method", "value"),
        Input("dropdown-topic", "value"),
    ],
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

    time.sleep(1)
    query_count += 1
    return query_count


@app.callback(Output("dropdown-contributor", "options"), Input("txt-s-cont", "value"))
def toggle_contributor_search(search_term):

    options = []
    if search_term is not None and search_term != "":
        options = synset_database.get_noun_synsets(search_term)

    l = list(
        {
            "label": o.gloss,
            "value": o.id,
        }
        for o in options
    )
    l.insert(0, {"label": "Any", "value": ANY_VALUE})
    return l


@app.callback(
    Output("dropdown-method", "options"),
    Input("txt-s-method", "value"),
)
def toggle_method_search(search_term):

    options = []

    if search_term is not None and search_term != "":
        options = synset_database.get_noun_synsets(search_term)

    l = list(
        {
            "label": o.gloss,
            "value": o.id,
        }
        for o in options
    )
    l.insert(0, {"label": "Any", "value": ANY_VALUE})
    return l


@app.callback(
    Output("dropdown-topic", "options"),
    Input("txt-s-topic", "value"),
)
def toggle_topic_search(search_term):

    options = []

    if search_term is not None and search_term != "":
        options = synset_database.get_noun_synsets(search_term)

    l = list(
        {
            "label": o.gloss,
            "value": o.id,
        }
        for o in options
    )
    l.insert(0, {"label": "Any", "value": ANY_VALUE})
    return l


# Callbacks for collapsible panels
@app.callback(
    [
        Output("collapse-left", "is_open"),
        Output("left-panel", "style"),
        Output("main-content", "style"),
    ],
    [Input("toggle-left", "n_clicks")],
    [State("collapse-left", "is_open")],
)
def toggle_panels(n_left, is_left_open):
    ctx = dash.callback_context
    left_style = {"float": "left", "width": "20%", "padding": "10px"}
    main_content_style = {"padding": "10px"}
    main_content_int_style = {"padding": "10px"}

    # Determine which button was clicked
    if ctx.triggered and "toggle-left" in ctx.triggered[0]["prop_id"]:
        is_left_open = not is_left_open

    # Adjust main content style based on collapsed panels
    if not is_left_open:
        main_content_style["margin-left"] = "0%"
    else:
        main_content_style["margin-left"] = "20%"

    # Hide left and right panels if they are collapsed
    left_style["display"] = "block" if is_left_open else "none"

    return (
        is_left_open,
        left_style,
        main_content_style,
    )


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
