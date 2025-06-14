"""
Created on Tue Apr 21 16:38:52 2024

@author: robertrouse
"""

import pandas as pd
import numpy as np
import dash
import torch
import random
import surrogate as sr
import visualisation as vi
from torch.autograd import Variable
from apollo import mechanics as ma
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go


# Set non-interactive backend to avoid threading issues
import matplotlib

matplotlib.use("Agg")
import geopandas as gpd

# Constraints for the model are defined here
from constraints import constraints, Constraint

### Set plotting style parameters
ma.textstyle()

random.seed(42)

### Set global model parameters
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

pareto = pd.read_csv("data/Pareto_5000.csv")


### Network Loading
net = torch.load("model.pt", weights_only=False)
net.eval()

area_dict = {
    "grassland": [11639928.2227896, 0.470769699212438],
    "organic": [11985582.5855, 0.484749476170689],
    "peatland_lo": [323753.4375, 0.0130940075809454],
    "peatland_up": [1897761.25, 0.0767537802415596],
    "silvoa": [4422140.20438513, 0.178850726056685],
    "silvop": [4268544.37239956, 0.172638637610765],
    "woodland": [9183888.07678469, 0.371436674243724],
    "woodpa": [5380110.83904161, 0.217595255997051],
    "farmland": [14725553.5855, 0.595565908955501],
    "not_used": [9999759.5395, 0.404434091044499],
}

slider_scale = {
    0: "0.0",
    0.1: "0.1",
    0.2: "0.2",
    0.3: "0.3",
    0.4: "0.4",
    0.5: "0.5",
    0.6: "0.6",
    0.7: "0.7",
    0.8: "0.8",
    0.9: "0.9",
    1.0: "1.0",
}

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(
    [
        html.Img(className="banner", src="assets/Banner_cropped.png"),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H3(
                                ["Conversion of Conventional Farmland Into:"],
                                className="graph_heading",
                            ),
                            html.Label("Grassland", className="slider_label"),
                            dcc.Slider(
                                min=0,
                                max=1,
                                step=0.0001,
                                marks=slider_scale,
                                value=0,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                updatemode="drag",
                                id="grassland",
                            ),
                            html.Label(
                                "Organic & Regenerative Farmland",
                                className="slider_label",
                            ),
                            dcc.Slider(
                                min=0,
                                max=1,
                                step=0.0001,
                                marks=slider_scale,
                                value=0,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                updatemode="drag",
                                id="organic",
                            ),
                            html.Label(
                                "Peatland (Lowland)", className="slider_label"
                            ),
                            dcc.Slider(
                                min=0,
                                max=1,
                                step=0.0001,
                                marks=slider_scale,
                                value=0,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                updatemode="drag",
                                id="peatland_lo",
                            ),
                            html.Label(
                                "Peatland (Upland)", className="slider_label"
                            ),
                            dcc.Slider(
                                min=0,
                                max=1,
                                step=0.0001,
                                marks=slider_scale,
                                value=0,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                updatemode="drag",
                                id="peatland_up",
                            ),
                            html.Label(
                                "Silvoarable (Mixed Crop Farming with Trees)",
                                className="slider_label",
                            ),
                            dcc.Slider(
                                min=0,
                                max=1,
                                step=0.0001,
                                marks=slider_scale,
                                value=0,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                updatemode="drag",
                                id="silvoa",
                            ),
                            html.Label(
                                "Silvopastoral (Mixed Livestock Grazing with Trees)",
                                className="slider_label",
                            ),
                            dcc.Slider(
                                min=0,
                                max=1,
                                step=0.0001,
                                marks=slider_scale,
                                value=0,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                updatemode="drag",
                                id="silvop",
                            ),
                            html.Label("Woodland", className="slider_label"),
                            dcc.Slider(
                                min=0,
                                max=1,
                                step=0.0001,
                                marks=slider_scale,
                                value=0,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                updatemode="drag",
                                id="woodland",
                            ),
                            html.Label(
                                "Wood Pasture", className="slider_label"
                            ),
                            dcc.Slider(
                                min=0,
                                max=1,
                                step=0.0001,
                                marks=slider_scale,
                                value=0,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                                updatemode="drag",
                                id="woodpa",
                            ),
                        ]
                    ),
                    width={"size": 4},
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                html.H3(
                                    ["Illustrative Land Use Allocation"],
                                    className="graph_heading",
                                )
                            ],
                            style={"height": "10%"},
                            align="end",
                        ),
                        dbc.Row(
                            [
                                html.Div(
                                    dcc.Graph(
                                        id="uk-map", style={"height": "60vh"}
                                    )
                                )
                            ],
                            style={"height": "75%"},
                        ),
                        dbc.Row(
                            [
                                html.Img(
                                    className="banner", src="assets/Key.png"
                                )
                            ],
                        ),
                    ],
                    width={"size": 4},
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3(
                                            [
                                                "Net CO2e Emissions",
                                                html.Br(),
                                                "% Change",
                                            ],
                                            className="graph_heading",
                                        )
                                    ],
                                    width={"size": 4},
                                    align="end",
                                ),
                                dbc.Col(
                                    [
                                        html.H3(
                                            [
                                                "Agricultural Output",
                                                html.Br(),
                                                "% Change",
                                            ],
                                            className="graph_heading",
                                        )
                                    ],
                                    width={"size": 4},
                                    align="end",
                                ),
                                dbc.Col(
                                    [
                                        html.H3(
                                            [
                                                "Bird Species",
                                                html.Br(),
                                                "Population",
                                                html.Br(),
                                                "% Change",
                                            ],
                                            className="graph_heading",
                                        )
                                    ],
                                    width={"size": 4},
                                    align="end",
                                ),
                            ],
                            style={"height": "20%"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div(
                                            dcc.Graph(
                                                id="fig1",
                                                style={"height": "60vh"},
                                            )
                                        )
                                    ],
                                    width={"size": 4},
                                    align="start",
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            dcc.Graph(
                                                id="fig2",
                                                style={"height": "60vh"},
                                            )
                                        )
                                    ],
                                    width={"size": 4},
                                    align="start",
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            dcc.Graph(
                                                id="fig3",
                                                style={"height": "60vh"},
                                            )
                                        )
                                    ],
                                    width={"size": 4},
                                    align="start",
                                ),
                            ]
                        ),
                    ],
                    width={"size": 4},
                ),
            ],
            # dbc.Row([
            #     dbc.Col([
            #         html.Div(children=[
            #                    html.H1(id='score_text'),
            #                ]),
            #         ]),
            #     ])
        ),
        dbc.Row(
            [
                dbc.Col(
                    [html.Div(dcc.Graph(id="fig4", style={"height": "60vh"}))],
                    width={"size": 4},
                    align="start",
                ),
                dbc.Col(
                    [html.Div(dcc.Graph(id="fig5", style={"height": "60vh"}))],
                    width={"size": 4},
                    align="start",
                ),
                dbc.Col(
                    [html.Div(dcc.Graph(id="fig6", style={"height": "60vh"}))],
                    width={"size": 4},
                    align="start",
                ),
            ]
        ),
    ],
    style={"margin-left": "80px", "margin-top": "0px", "margin-right": "80px"},
)


# @app.callback(Output('my-graph', 'figure'),
@app.callback(
    Output("fig1", "figure"),
    Output("fig2", "figure"),
    Output("fig3", "figure"),
    Output("uk-map", "figure"),
    Output("fig4", "figure"),
    Output("fig5", "figure"),
    Output("fig6", "figure"),
    Input("grassland", "value"),
    Input("organic", "value"),
    Input("peatland_lo", "value"),
    Input("peatland_up", "value"),
    Input("silvoa", "value"),
    Input("silvop", "value"),
    Input("woodland", "value"),
    Input("woodpa", "value"),
)


# def euclid_distance(candidates, target):
#     distances = np.linalg.norm(candidates - target, axis=1)
#     closest_idx = np.argmin(distances)
#     return closest_idx, distances[closest_idx]

# def scoring(base_dist, new_dist):
#     if new_dist>base_dist:
#         score = 0
#     else:
#         score = 100 * (1 - (base_dist/new_dist))
#     return score


def display_value(
    grassland,
    organic,
    peatland_lo,
    peatland_up,
    silvoa,
    silvop,
    woodland,
    woodpa,
    pareto=pareto,
):
    base = np.zeros((8,))
    base = torch.from_numpy(base)
    base = net(base.float()).data.numpy()
    z = np.array(
        [
            grassland,
            organic,
            peatland_lo,
            peatland_up,
            silvoa,
            silvop,
            woodland,
            woodpa,
        ]
    )
    z = torch.from_numpy(z)
    z = net(z.float()).data.numpy()
    col_list = ["gwp_rel", "food_rel", "birds_rel"]
    zf = pd.DataFrame(z.reshape(1, -1), columns=col_list)
    fig1 = vi.single_dumbell(
        "Net CO2e emissions % change",
        base[0],
        z[0],
        [-1, 1],
        ["#7DB567", "#CCA857", "#8B424B"],
    )
    fig1.update_xaxes(
        linecolor="black",
        mirror=True,
        showticklabels=False,
        title_font=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
        tickfont=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
    )
    fig1.update_yaxes(
        range=[-2, 1.25],
        linecolor="black",
        mirror=True,
        title_font=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
        tickfont=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
    )
    fig1.update_layout(
        plot_bgcolor="white", margin=dict(l=60, r=60, t=20, b=20)
    )

    fig2 = vi.single_dumbell(
        "Farmland productivity % change",
        base[1],
        z[1],
        [-1, 1],
        ["#8B424B", "#CCA857", "#7DB567"],
    )
    fig2.update_xaxes(
        linecolor="black",
        mirror=True,
        showticklabels=False,
        title_font=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
        tickfont=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
    )
    fig2.update_yaxes(
        range=[-1.25, 1.25],
        linecolor="black",
        mirror=True,
        title_font=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
        tickfont=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
    )
    fig2.update_layout(
        plot_bgcolor="white", margin=dict(l=60, r=60, t=20, b=20)
    )

    fig3 = vi.single_dumbell(
        "Geometric bird species population change",
        base[2] * 1.0081,
        z[2] * 1.0081,
        [0.9, 1.2],
        ["#8B424B", "#CCA857", "#7DB567"],
    )
    fig3.update_xaxes(
        linecolor="black",
        mirror=True,
        showticklabels=False,
        title_font=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
        tickfont=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
    )
    fig3.update_yaxes(
        range=[0.9, 1.2],
        linecolor="black",
        mirror=True,
        title_font=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
        tickfont=dict(
            size=18, family="assets/fonts/GlacialIndifference-Bold.otf"
        ),
    )
    fig3.update_layout(
        plot_bgcolor="white",
        margin=dict(l=60, r=60, t=20, b=20),
    )
    fig3.layout.font.family = "Arial Black"

    fig4 = vi.dashboard_pareto_scatter(
        "Text",
        pareto["gwp_rel"],
        pareto["food_rel"],
        pareto["birds_rel"],
        zf["gwp_rel"],
        zf["food_rel"],
        [0.9, 1.2],
        ["#8B424B", "#CCA857", "#7DB567"],
    )
    fig4.update_layout(plot_bgcolor="white")
    fig5 = vi.dashboard_pareto_scatter(
        "Text",
        pareto["birds_rel"],
        pareto["food_rel"],
        pareto["gwp_rel"],
        zf["birds_rel"],
        zf["food_rel"],
        [-1, 1],
        ["#8B424B", "#CCA857", "#7DB567"],
    )
    fig5.update_layout(plot_bgcolor="white")
    fig6 = vi.dashboard_pareto_scatter(
        "Text",
        pareto["birds_rel"],
        pareto["gwp_rel"],
        pareto["food_rel"],
        zf["birds_rel"],
        zf["gwp_rel"],
        [-1, 1],
        ["#8B424B", "#CCA857", "#7DB567"],
    )
    fig6.update_layout(plot_bgcolor="white")

    # pareto_arr = pareto[['gwp_rel','food_rel', 'birds_rel']].to_numpy()
    # _, base_dist = euclid_distance(pareto_arr, base)
    # _, new_dist = euclid_distance(pareto_arr, z)
    # score = scoring(base_dist, new_dist)
    # score_text = 'Relative geometric change across 120 terrestrial \
    #         bird species populations : {}'.format(score)
    # fig = px.scatter(x=data_x, y=data_y, trendline="ols",
    #               trendline_color_override="black",)

    # fig.update_traces(marker=dict( size=10, color=data_y,
    #                           colorscale='YlGn', showscale=True,
    #                           colorbar_x=-0.3),
    #              )

    uk_map = loadukmap_plotly(
        area_dict,
        grassland,
        organic,
        peatland_lo,
        peatland_up,
        silvoa,
        silvop,
        woodland,
        woodpa,
    )

    return [fig1, fig2, fig3, uk_map, fig4, fig5, fig6]


# Enforce invariants on the sliders
@app.callback(
    # All the sliders
    [
        Output("grassland", "value"),
        Output("organic", "value"),
        Output("peatland_lo", "value"),
        Output("silvoa", "value"),
        Output("silvop", "value"),
        Output("woodland", "value"),
        Output("woodpa", "value"),
    ],
    # All the sliders
    [
        Input("grassland", "value"),
        Input("organic", "value"),
        Input("peatland_lo", "value"),
        Input("silvoa", "value"),
        Input("silvop", "value"),
        Input("woodland", "value"),
        Input("woodpa", "value"),
    ],
)
def enforce_slider_constraints(g_val, o_val, p_lo, s_a, s_p, w_l, w_p):
    # Put the values into a model dictionary
    model = {
        "G": g_val,
        "O": o_val,
        "P_lo": p_lo,
        "S_A": s_a,
        "S_P": s_p,
        "WL": w_l,
        "WP": w_p,
    }
    # Apply balancing of the constraints when constraints are not satisfied
    for constraint in constraints:
        if isinstance(constraint, Constraint) and not constraint.isSatisfied(
            model
        ):
            model = constraint.balance(model)

    # Return the balanced values back to the UI
    return (
        model["G"],
        model["O"],
        model["P_lo"],
        model["S_A"],
        model["S_P"],
        model["WL"],
        model["WP"],
    )


def loadukmap_plotly(
    area_dict,
    grassland_value=0,
    organic_value=0,
    peatland_lo_value=0,
    peatland_up_value=0,
    silvoa_value=0,
    silvop_value=0,
    woodland_value=0,
    woodpa_value=0,
):
    """Load UK hexagon map and convert to plotly figure"""

    # Map from category to colours
    colour_map = {
        "grassland": "rgba(148, 193, 145, 0.8)",
        "organic": "rgba(216, 216, 158, 0.8)",
        "peatland_lo": "rgba(118, 179, 193, 0.8)",
        "peatland_up": "rgba(175, 165, 150, 0.8)",
        "silvoa": "rgba(195, 195, 195, 0.8)",
        "silvop": "rgba(160, 127, 145, 0.8)",
        "woodland": "rgba(61, 86, 58, 0.8)",
        "woodpa": "rgba(92, 130, 116, 0.8)",
        "farmland": "rgba(221, 181, 128, 0.8)",
        "not_used": "rgba(91, 91, 91, 0.8)",
    }

    # Load file
    geoData = gpd.read_file("geogHEXLA.json")

    # Create a plotly figure directly instead of going through matplotlib
    fig = go.Figure()

    # Sort hexagons by y-coordinate to fill from bottom up
    geoData["centroid_y"] = geoData.geometry.centroid.y
    geoData = geoData.sort_values("centroid_y")

    # Calculate how many hexagons to fill based on grassland value
    total_hexagons = len(geoData)

    # map from category to number of hexagons to fill
    hex_count = {}
    hex_count["not_used"] = int(total_hexagons * area_dict["not_used"][1])

    hex_count["grassland"] = int(
        total_hexagons * grassland_value * area_dict["grassland"][1]
    )
    hex_count["organic"] = int(
        total_hexagons * organic_value * area_dict["organic"][1]
    )
    hex_count["peatland_lo"] = int(
        total_hexagons * peatland_lo_value * area_dict["peatland_lo"][1]
    )
    hex_count["peatland_up"] = int(
        total_hexagons * peatland_up_value * area_dict["peatland_up"][1]
    )
    hex_count["silvoa"] = int(
        total_hexagons * silvoa_value * area_dict["silvoa"][1]
    )
    hex_count["silvop"] = int(
        total_hexagons * silvop_value * area_dict["silvop"][1]
    )
    hex_count["woodland"] = int(
        total_hexagons * woodland_value * area_dict["woodland"][1]
    )
    hex_count["woodpa"] = int(
        total_hexagons * woodpa_value * area_dict["woodpa"][1]
    )
    residual_count = sum(hex_count.values())
    hex_count["farmland"] = total_hexagons - residual_count

    # make list of colours
    colours = []
    # loop through the hex_count structure
    for category, count in hex_count.items():
        colours = colours + [colour_map[category]] * count
    # put white for the rest
    colours = colours + (["white"] * (len(geoData) - len(colours)))
    colours = random.sample(colours, len(colours))

    # Add each hexagon as a separate polygon
    for idx, (_, row) in enumerate(geoData.iterrows()):
        # Determine color based on fill status
        color = colours[idx]

        # Get polygon coordinates and convert to lists
        x, y = row.geometry.exterior.xy
        x_list = list(x)  # Convert array.array to list
        y_list = list(y)  # Convert array.array to list

        # Add polygon to figure
        fig.add_trace(
            go.Scatter(
                x=x_list,
                y=y_list,
                fill="toself",
                fillcolor=color,
                line=dict(color="black", width=0.5),
                mode="lines",
                showlegend=False,
            )
        )

    # Configure layout
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            visible=False,
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            visible=False,
            scaleanchor="x",
            scaleratio=1.4,
            fixedrange=True,
            # Add range to control y-axis size
        ),
    )

    return fig


if __name__ == "__main__":
    # for backwards compatibility, use the `run_server` method if its defined otherwise
    # use `run`
    if "run_server" in app.__dir__():
        app.run_server(debug=True, host="0.0.0.0", port="8051")
    else:
        app.run(debug=True, host="0.0.0.0", port="8051")
