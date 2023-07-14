# Import packages
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_mantine_components as dmc

from dash import Dash, dcc, callback, Output, Input
from graph_helpers import (
    MANUAL_SHOT_LIMITS,
    shot_type,
    SHOT_COLOR,
    HOVER_TEMPLATE,
    CLUB_ORDER,
)


# Incorporate data
data = pd.read_excel(
    "/workspaces/topyardage/data/Golf Range.xlsx", sheet_name=["PdH", "LG"]
)

# Initialize the app
app = Dash(
    __name__,
    external_stylesheets=[
        # include google fonts
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap"
    ],
)

# App layout
app.layout = dmc.MantineProvider(
    withGlobalStyles=True,
    theme={"colors": dmc.theme.DEFAULT_COLORS["green"]},
    children=[
        dmc.Stack(
            [
                dmc.Header(
                    height=70,
                    fixed=True,
                    px=25,
                    pt=12,
                    children=[
                        dmc.Text(
                            "Pablo's Yardage Book",
                            size="xl",
                            color=dmc.theme.DEFAULT_COLORS["green"][8],
                            align="left",
                        )
                    ],
                ),
                dmc.Space(h=70),
                dmc.RadioGroup(
                    [
                        dmc.Radio("Puerta de Hierro", "PdH"),
                        dmc.Radio("La Granja", "LG"),
                    ],
                    id="golf-bag",
                    value="PdH",
                    label="Select Golf Bag",
                ),
                dmc.Center(
                    style={"width": "100%"},
                    children=[dcc.Graph(figure={}, id="shot-tracer")],
                ),
            ],
            spacing="xl",
        )
    ],
)


def basic_shapes(fig):
    fig.add_shape(
        type="circle",
        xref="x",
        yref="y",
        x0=15,
        y0=15,
        x1=-15,
        y1=-15,
        line_color="#55A868",
        fillcolor="#55A868",
        layer="below",
    )

    fig.add_shape(
        type="line",
        x0=15,
        x1=-15,
        y0=0,
        y1=0,
        line={"dash": "dot"},
    )

    fig.add_shape(
        type="rect",
        x0=15,
        y0=-18,
        x1=-15,
        y1=-23,
        line={"color": SHOT_COLOR["Miss Hit"]},
    )

    fig.add_trace(
        go.Scatter(
            x=[0],
            y=[0],
            mode="markers",
            marker={"color": "red"},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    return fig


def good_shots(fig, shots):
    club_name = shots["Club"].unique()[0]
    try:
        good = shots.groupby("Shot").get_group("Good")
    except KeyError:
        return fig, 0

    median_carry = good["Flat Carry"].median()
    fig.add_trace(
        go.Scatter(
            x=[-18],
            y=[0],
            mode="text",
            text=[f"{median_carry:.0f}m"],
            visible=club_name == 8,
            hoverinfo="skip",
            showlegend=False,
        )
    )

    median_offline = good["Offline"].median()
    fig.add_trace(
        go.Scatter(
            x=[median_offline, median_offline],
            y=[-15, 15],
            mode="lines",
            visible=club_name == 8,
            hoverinfo="skip",
            showlegend=False,
            line={
                "dash": "dot",
                "color": fig._layout["template"]["layout"]["shapedefaults"]["line"][
                    "color"
                ],
            },
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[median_offline],
            y=[16],
            mode="text",
            text=[f"{median_offline:.0f}m"],
            visible=club_name == 8,
            hoverinfo="skip",
            showlegend=False,
        )
    )

    good_roll = good["Roll"].mean()
    fig.add_trace(
        go.Scatter(
            x=[0, 0],
            y=[0, min(good_roll, 15)],
            mode="lines",
            line={"color": "red"},
            visible=club_name == 8,
            hoverinfo="text",
            text=f"Roll: {good_roll:.0f}m",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=good["Offline"].to_list(),
            y=(good["Flat Carry"] - median_carry).to_list(),
            mode="markers",
            marker={"color": SHOT_COLOR["Good"]},
            name="",
            showlegend=False,
            hovertemplate=HOVER_TEMPLATE,
            customdata=np.stack((good["Total Distance"], good["Flat Carry"]), axis=1),
            visible=club_name == 8,
        )
    )

    return fig, 5


def soft_shots(fig, shots):
    club_name = shots["Club"].unique()[0]
    try:
        soft = shots.groupby("Shot").get_group("Soft")
        try:
            good = shots.groupby("Shot").get_group("Good")
        except KeyError:
            good = shots.groupby("Shot").get_group("Soft")
    except KeyError:
        return fig, 0

    median_carry = soft["Flat Carry"].median()
    fig.add_trace(
        go.Scatter(
            x=[-15, 15],
            y=[
                median_carry - good["Flat Carry"].median(),
                median_carry - good["Flat Carry"].median(),
            ],
            mode="lines",
            visible=club_name == 8,
            hoverinfo="skip",
            showlegend=False,
            line={"dash": "dot", "color": SHOT_COLOR["Soft"]},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[-18],
            y=[median_carry - good["Flat Carry"].median()],
            mode="text",
            text=[f"{median_carry:.0f}m"],
            visible=club_name == 8,
            hoverinfo="skip",
            showlegend=False,
        )
    )

    return fig, 2


def bad_bar(fig, shots):
    club_name = shots["Club"].unique()[0]
    shot_pct = shots["Shot"].value_counts(normalize=True)
    total_len = 30
    num = 0

    try:
        miss_pct = shot_pct["Miss Hit"]
    except KeyError:
        miss_len = 0
    else:
        miss_len = miss_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[-15, miss_len - 15, miss_len - 15, -15],
                y=[-23, -23, -18, -18],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Miss Hit"],
                hoveron="fills",
                text=f"<b>Miss Hits</b> ({miss_pct:.0%})",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    try:
        flat_pct = shot_pct["Flat"]
    except KeyError:
        flat_len = 0
    else:
        flat_len = flat_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[
                    miss_len - 15,
                    flat_len + miss_len - 15,
                    flat_len + miss_len - 15,
                    miss_len - 15,
                ],
                y=[-23, -23, -18, -18],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Flat"],
                hoveron="fills",
                text=f"<b>Flat</b> ({flat_pct:.0%})",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    return fig, num


def good_bar(fig, shots):
    club_name = shots["Club"].unique()[0]
    shot_pct = shots["Shot"].value_counts(normalize=True)
    total_len = 30
    num = 0

    try:
        good_pct = shot_pct["Good"]
    except KeyError:
        good_pct = 0

    try:
        soft_pct = shot_pct["Soft"]
    except KeyError:
        soft_pct = 0

    good_soft_len = (good_pct + soft_pct) * total_len / 2

    if good_soft_len > 0:
        fig.add_trace(
            go.Scatter(
                x=[
                    good_soft_len * -1,
                    good_soft_len,
                    good_soft_len,
                    good_soft_len * -1,
                ],
                y=[23, 23, 18, 18],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Good"],
                hoveron="fills",
                text=f"<b>Good</b> ({good_pct:.0%})<br><b>Soft</b> ({soft_pct:.0%})",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    try:
        fade_pct = shot_pct["Fade"]
    except KeyError:
        pass
    else:
        fade_carry = shots.groupby("Shot").get_group("Fade")["Flat Carry"].median()
        fade_offline = shots.groupby("Shot").get_group("Fade")["Offline"].mean()

        fade_len = fade_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[
                    good_soft_len,
                    good_soft_len + fade_len,
                    good_soft_len + fade_len,
                    good_soft_len,
                ],
                y=[23, 23, 18, 18],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Fade"],
                hoveron="fills",
                text=f"<b>Fade</b> ({fade_pct:.0%})<br>Flat Carry: {fade_carry:.0f}m<br>Offline: {fade_offline:.0f}m",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    try:
        draw_pct = shot_pct["Draw"]
    except KeyError:
        pass
    else:
        draw_carry = shots.groupby("Shot").get_group("Draw")["Flat Carry"].median()
        draw_offline = shots.groupby("Shot").get_group("Draw")["Offline"].mean()

        draw_len = draw_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[
                    -good_soft_len,
                    -good_soft_len - draw_len,
                    -good_soft_len - draw_len,
                    -good_soft_len,
                ],
                y=[23, 23, 18, 18],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Draw"],
                hoveron="fills",
                text=f"<b>Draw</b> ({draw_pct:.0%})<br>Flat Carry: {draw_carry:.0f}m<br>Offline: {draw_offline:.0f}m",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    return fig, num


def slice_bar(fig, shots):
    club_name = shots["Club"].unique()[0]
    shot_pct = shots["Shot"].value_counts(normalize=True)
    total_len = 30
    num = 0

    try:
        push_pct = shot_pct["Push"]
    except KeyError:
        push_len = 0
    else:
        push_len = push_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[23, 23, 18, 18],
                y=[-15, push_len - 15, push_len - 15, -15],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Push"],
                hoveron="fills",
                text=f"<b>Push</b> ({push_pct:.0%})",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    try:
        slice_pct = shot_pct["Slice"]
    except KeyError:
        slice_len = 0
    else:
        slice_len = slice_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[23, 23, 18, 18],
                y=[
                    push_len - 15,
                    slice_len + push_len - 15,
                    slice_len + push_len - 15,
                    push_len - 15,
                ],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Slice"],
                hoveron="fills",
                text=f"<b>Slice</b> ({slice_pct:.0%})",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    try:
        slice_push_pct = shot_pct["Slice/Push"]
    except KeyError:
        slice_push_len = 0
    else:
        slice_push_len = slice_push_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[23, 23, 18, 18],
                y=[
                    slice_len + push_len - 15,
                    slice_push_len + slice_len + push_len - 15,
                    slice_push_len + slice_len + push_len - 15,
                    slice_len + push_len - 15,
                ],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Slice/Push"],
                hoveron="fills",
                text=f"<b>Slice/Push</b> ({slice_push_pct:.0%})",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    return fig, num


def hook_bar(fig, shots):
    club_name = shots["Club"].unique()[0]
    shot_pct = shots["Shot"].value_counts(normalize=True)
    total_len = 30
    num = 0

    try:
        pull_pct = shot_pct["Pull"]
    except KeyError:
        pull_len = 0
    else:
        pull_len = pull_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[-23, -23, -18, -18],
                y=[-15, pull_len - 15, pull_len - 15, -15],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Pull"],
                hoveron="fills",
                text=f"<b>Pull</b> ({pull_pct:.0%})",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    try:
        hook_pct = shot_pct["Hook"]
    except KeyError:
        hook_len = 0
    else:
        hook_len = hook_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[-23, -23, -18, -18],
                y=[
                    pull_len - 15,
                    hook_len + pull_len - 15,
                    hook_len + pull_len - 15,
                    pull_len - 15,
                ],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Hook"],
                hoveron="fills",
                text=f"<b>Hook</b> ({hook_pct:.0%})",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    try:
        hook_pull_pct = shot_pct["Hook/Pull"]
    except KeyError:
        hook_pull_len = 0
    else:
        hook_pull_len = hook_pull_pct * total_len
        fig.add_trace(
            go.Scatter(
                x=[-23, -23, -18, -18],
                y=[
                    hook_len + pull_len - 15,
                    hook_pull_len + hook_len + pull_len - 15,
                    hook_pull_len + hook_len + pull_len - 15,
                    hook_len + pull_len - 15,
                ],
                fill="toself",
                mode="none",
                fillcolor=SHOT_COLOR["Hook/Pull"],
                hoveron="fills",
                text=f"<b>Hook/Pull</b> ({hook_pull_pct:.0%})",
                hoverinfo="text",
                visible=club_name == 8,
                showlegend=False,
            )
        )
        num += 1

    return fig, num


# Add controls to build the interaction
@callback(
    Output(component_id="shot-tracer", component_property="figure"),
    Input(component_id="golf-bag", component_property="value"),
)
def update_graph(golf_bag):
    df = data[golf_bag]
    df["Offset"] = df["Offline"] - df["Curve"]
    df["Roll"] = df["Total Distance"] - df["Flat Carry"]
    df["Shot"] = df.apply(lambda x: shot_type(x, MANUAL_SHOT_LIMITS), axis=1)

    club_trace = []
    clubs = df.groupby("Club")

    fig = go.Figure()

    fig = basic_shapes(fig)

    for club_name, club_data in clubs:
        fig, num = good_shots(fig, club_data)
        club_trace = club_trace + [club_name] * num

        fig, num = soft_shots(fig, club_data)
        club_trace = club_trace + [club_name] * num

        fig, num = bad_bar(fig, club_data)
        club_trace = club_trace + [club_name] * num

        fig, num = good_bar(fig, club_data)
        club_trace = club_trace + [club_name] * num

        fig, num = slice_bar(fig, club_data)
        club_trace = club_trace + [club_name] * num

        fig, num = hook_bar(fig, club_data)
        club_trace = club_trace + [club_name] * num

    fig.update_layout(
        updatemenus=[
            {
                "active": 7,
                "buttons": list(
                    [
                        {
                            "label": club,
                            "args": [
                                {
                                    "visible": [True]
                                    + [club_name == club for club_name in club_trace]
                                },
                                {"title": club, "showlegend": True},
                            ],
                        }
                        for club in [
                            club for club in CLUB_ORDER if club in clubs.groups.keys()
                        ]
                    ]
                ),
                "pad": {"r": 10, "t": 10},
                "showactive": True,
                "x": 0,
                "xanchor": "left",
                "y": 1.05,
                "yanchor": "top",
            }
        ]
    )

    fig.update_layout(
        xaxis={"range": [-30, 30], "visible": False, "showticklabels": False},
        yaxis={"range": [-30, 30], "visible": False, "showticklabels": False},
        width=1000,
        height=1000,
        title="Approach",
        plot_bgcolor="#FFFFFF",
    )
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
