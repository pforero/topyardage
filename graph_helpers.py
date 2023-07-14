import pandas as pd
import plotly.express as px

MANUAL_SHOT_LIMITS = {
    "Driver": {
        "Ball Speed": 62,
        "Launch Angle": (6, 18),
        "Height": (9, 23),
        "Straight": 6,
        "Curve": 11,
        "Offset": 12,
        "Offline": 15
    },
    "3Wood": {
        "Ball Speed": 59,
        "Launch Angle": (5, 24),
        "Height": (13, 24),
        "Straight": 4,
        "Curve": 9,
        "Offset": 11,
        "Offline": 14
    },
    "5Wood": {
        "Ball Speed": 58,
        "Launch Angle": (6, 27),
        "Height": (13, 30),
        "Straight": 4,
        "Curve": 9,
        "Offset": 10,
        "Offline": 13
    },
    3: {
        "Ball Speed": 54,
        "Launch Angle": (10, 14),
        "Height": (13, 23),
        "Straight": 4,
        "Curve": 9,
        "Offset": 10,
        "Offline": 11
    },
    4: {
        "Ball Speed": 55,
        "Launch Angle": (9, 16),
        "Height": (13, 24),
        "Straight": 4,
        "Curve": 10,
        "Offset": 8,
        "Offline": 10
    },
    5: {
        "Ball Speed": 54,
        "Launch Angle": (11, 16),
        "Height": (17, 27),
        "Straight": 3,
        "Curve": 8,
        "Offset": 7,
        "Offline": 9
    },
    6: {
        "Ball Speed": 53,
        "Launch Angle": (12, 17),
        "Height": (18, 29),
        "Straight": 3,
        "Curve": 8,
        "Offset": 6,
        "Offline": 8
    },
    7: {
        "Ball Speed": 50,
        "Launch Angle": (14, 22),
        "Height": (19, 30),
        "Straight": 3,
        "Curve": 8,
        "Offset": 5,
        "Offline": 8
    },
    8: {
        "Ball Speed": 48,
        "Launch Angle": (18, 22),
        "Height": (19, 32),
        "Straight": 3,
        "Curve": 7,
        "Offset": 5,
        "Offline": 7
    },
    9: {
        "Ball Speed": 45,
        "Launch Angle": (21, 25),
        "Height": (19, 33),
        "Straight": 3,
        "Curve": 7,
        "Offset": 4,
        "Offline": 7
    },
    "PW": {
        "Ball Speed": 40,
        "Launch Angle": (24, 39),
        "Height": (18, 35),
        "Straight": 2,
        "Curve": 5,
        "Offset": 4,
        "Offline": 5
    },
    46: {
        "Ball Speed": 40,
        "Launch Angle": (22, 33),
        "Height": (16, 28),
        "Straight": 5,
        "Curve": 5,
        "Offset": 3,
        "Offline": 5
    },
    50: {
        "Ball Speed": 37,
        "Launch Angle": (28, 33),
        "Height": (20, 28),
        "Straight": 2,
        "Curve": 5,
        "Offset": 3,
        "Offline": 5
    },
    52: {
        "Ball Speed": 35,
        "Launch Angle": (26, 42),
        "Height": (17, 32),
        "Straight": 2,
        "Curve": 5,
        "Offset": 3,
        "Offline": 5
    },
    "SW": {
        "Ball Speed": 35,
        "Launch Angle": (30, 35),
        "Height": (17, 25),
        "Straight": 2,
        "Curve": 4,
        "Offset": 3,
        "Offline": 4
    },
    58: {
        "Ball Speed": 30,
        "Launch Angle": (30, 45),
        "Height": (15, 25),
        "Straight": 1,
        "Curve": 3,
        "Offset": 2,
        "Offline": 3
    },
    60: {
        "Ball Speed": 30,
        "Launch Angle": (38, 48),
        "Height": (14, 24),
        "Straight": 0,
        "Curve": 1,
        "Offset": 2,
        "Offline": 2
    },
}

SHOT_COLOR = {
    "Good": px.colors.sequential.Viridis[9],
    "Soft": px.colors.sequential.Viridis[8],
    "Fade": px.colors.sequential.Cividis[7],
    "Slice": px.colors.sequential.Cividis[5],
    "Push": px.colors.sequential.Cividis[3],
    "Slice/Push": px.colors.sequential.Cividis[1],
    "Draw": px.colors.sequential.Plasma[7],
    "Hook": px.colors.sequential.Plasma[5],
    "Pull": px.colors.sequential.Plasma[3],
    "Hook/Pull": px.colors.sequential.Plasma[1],
    "Balloon": px.colors.sequential.Hot[3],
    "Flat": px.colors.sequential.Hot[1],
    "Miss Hit": px.colors.sequential.Hot[0]
}

def shot_type(shot: pd.Series, shot_limit: dict):

    limit = shot_limit[shot["Club"]]

    if shot["Ball Speed"] < limit["Ball Speed"] - 2:
        return "Miss Hit"
    if (shot["Height"] < limit["Height"][0]) | (shot["Launch Angle"] < limit["Launch Angle"][0]):
        return "Flat"
    if (shot["Height"] > limit["Height"][1]) | (shot["Launch Angle"] > limit["Launch Angle"][1]):
        return "Balloon"
    if shot["Curve"] < limit["Curve"] * -1:
        if shot["Offset"] < limit["Offset"] * -1:
            return "Hook/Pull"
        return "Hook"
    if shot["Curve"] > limit["Curve"]:
        if shot["Offset"] > limit["Offset"]:
            return "Slice/Push"
        return "Slice"
    if shot["Offset"] < limit["Offset"] * -1:
        return "Pull"
    if shot["Offset"] > limit["Offset"]:
        return "Push"
    if limit["Straight"] * -1 > shot["Curve"] > limit["Curve"] * -1:
        return "Draw"
    if limit["Curve"] > shot["Curve"] > limit["Straight"]:
        return "Fade"
    if shot["Offline"] < limit["Offline"] * -1:
        return "Hook/Pull"
    if shot["Offline"] > limit["Offline"]:
        return "Slice/Push"
    if shot["Ball Speed"] < limit["Ball Speed"]:
        return "Soft"
    return "Good"

HOVER_TEMPLATE = "Total Distance: %{customdata[0]}m<br>Carry: %{customdata[1]}m<br>Offline: %{x}m"

CLUB_ORDER = ["Driver", "3Wood", "5Wood", 3, 4, 5, 6, 7, 8, 9, "PW", 46, 50, 52, "SW", 58, 60]
