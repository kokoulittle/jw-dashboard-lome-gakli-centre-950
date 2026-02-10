import os
import base64
from datetime import date

import pandas as pd  # type: ignore
from babel.dates import format_date

import dash  # type: ignore
from dash import dcc, html, Input, Output, State  # type: ignore
import plotly.graph_objects as go  # type: ignore
import plotly.io as pio  # type: ignore

from flask import send_from_directory

# ======================================================
# CONSTANTS & PATHS (ABSOLUTE – SAFE IN DOCKER)
# ======================================================

BASE_DIR = os.getcwd()

DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
EXPORT_DIR = os.path.join(BASE_DIR, "exports", "pdf")

os.makedirs(EXPORT_DIR, exist_ok=True)

DATA_FILE = os.path.join(DATA_DIR, "Random_Attendant_Crew_Schedule_2026.csv")
LOGO_FILE = os.path.join(ASSETS_DIR, "JW_Logo.png")

# ======================================================
# DATA LOADING
# ======================================================

df = pd.read_csv(DATA_FILE)
df["Date"] = pd.to_datetime(df["Date"])
df["ISO_Year"] = df["Date"].dt.isocalendar().year
df["ISO_Week"] = df["Date"].dt.isocalendar().week

# ======================================================
# HELPERS
# ======================================================

def week_date_range(year: int, week: int):
    monday = date.fromisocalendar(year, week, 1)
    sunday = date.fromisocalendar(year, week, 7)
    return monday, sunday


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_week_options(dataframe: pd.DataFrame):
    weeks = (
        dataframe[["ISO_Year", "ISO_Week"]]
        .drop_duplicates()
        .sort_values(["ISO_Year", "ISO_Week"])
    )

    options = []
    for _, r in weeks.iterrows():
        y, w = int(r.ISO_Year), int(r.ISO_Week)
        monday, sunday = week_date_range(y, w)
        options.append({
            "label": (
                f"Semaine {w} "
                f"({format_date(monday, 'short', locale='fr_FR')} – "
                f"{format_date(sunday, 'short', locale='fr_FR')})"
            ),
            "value": f"{y}-W{w}"
        })
    return options


def filter_week(dataframe: pd.DataFrame, year: int, week: int):
    return dataframe[
        (dataframe["ISO_Year"] == year) &
        (dataframe["ISO_Week"] == week)
    ].sort_values("Date")


def build_table_figure(data: pd.DataFrame):
    return go.Figure(go.Table(
        header=dict(
            values=["Date", "Entrée", "Porte", "Intérieur", "Comptage"],
            fill_color="#4F6FA0",
            font=dict(color="white", size=13),
            align="left"
        ),
        cells=dict(
            values=[
                [format_date(d, "full", locale="fr_FR") for d in data["Date"]],
                data["Entrée"],
                data["Porte"],
                data["Intérieur"],
                data["Comptage"]
            ],
            fill_color="#E9EEF7",
            align="left"
        )
    ))

# ======================================================
# APP INITIALIZATION
# ======================================================

JW_LOGO = encode_image(LOGO_FILE)

app = dash.Dash(__name__)
server = app.server

# ======================================================
# FLASK ROUTE – PDF DOWNLOAD (PRODUCTION SAFE)
# ======================================================

@server.route("/download/<path:filename>")
def download_pdf(filename):
    return send_from_directory(
        EXPORT_DIR,
        filename,
        as_attachment=True,
        mimetype="application/pdf"
    )

# ======================================================
# LAYOUT
# ======================================================

today = date.today()
current_week_value = f"{today.isocalendar().year}-W{today.isocalendar().week}"

app.layout = html.Div(
    style={"fontFamily": "Arial", "backgroundColor": "#F4F6F9"},
    children=[

        # HEADER
        html.Div(
            style={
                "backgroundColor": "#4F6FA0",
                "color": "white",
                "padding": "20px",
                "display": "flex",
                "alignItems": "center"
            },
            children=[
                html.Img(
                    src=f"data:image/png;base64,{JW_LOGO}",
                    style={"height": "70px", "marginRight": "20px"}
                ),
                html.H2(id="dashboard-title", style={"margin": 0})
            ]
        ),

        # CONTROLS
        html.Div(
            style={"padding": "20px"},
            children=[
                dcc.Dropdown(
                    id="week-selector",
                    options=build_week_options(df),
                    value=current_week_value,
                    clearable=False
                ),
                html.Br(),
                html.Button("Exporter en PDF", id="export-pdf"),
                html.Div(id="download-link", style={"marginTop": "15px"})
            ]
        ),

        # TABLE
        dcc.Graph(id="week-table")
    ]
)

# ======================================================
# CALLBACK – TABLE + TITLE
# ======================================================

@app.callback(
    Output("week-table", "figure"),
    Output("dashboard-title", "children"),
    Input("week-selector", "value")
)
def update_dashboard(selected_week):
    year, week = map(int, selected_week.replace("W", "").split("-"))
    data = filter_week(df, year, week)

    monday, sunday = week_date_range(year, week)

    title = (
        f"Tableau de Bord des Préposés à l’Accueil — "
        f"Semaine du {format_date(monday, 'long', locale='fr_FR')} "
        f"au {format_date(sunday, 'long', locale='fr_FR')}"
    )

    fig = build_table_figure(data)
    fig.update_layout(margin=dict(t=20, b=20))

    return fig, title

# ======================================================
# CALLBACK – PDF EXPORT
# ======================================================

@app.callback(
    Output("download-link", "children"),
    Input("export-pdf", "n_clicks"),
    State("week-selector", "value"),
    prevent_initial_call=True
)
def export_pdf(_, selected_week):
    year, week = map(int, selected_week.replace("W", "").split("-"))
    data = filter_week(df, year, week)

    monday, sunday = week_date_range(year, week)

    fig = build_table_figure(data)

    fig.add_layout_image(
        source=f"data:image/png;base64,{JW_LOGO}",
        xref="paper", yref="paper",
        x=0, y=1.5,
        sizex=0.18, sizey=0.18,
        xanchor="left", yanchor="top"
    )

    fig.add_annotation(
        text="<b>Assemblée locale : Lomé Gakli Centre (950)</b>",
        xref="paper", yref="paper",
        x=0.5, y=1.18,
        showarrow=False,
        font=dict(size=12, color="#4F6FA0")
    )

    fig.add_annotation(
        text=(
            "<b>Préposés à l’accueil pour la semaine "
            f"du {format_date(monday, 'medium', locale='fr_FR')} "
            f"au {format_date(sunday, 'medium', locale='fr_FR')}</b>"
        ),
        xref="paper", yref="paper",
        x=0.5, y=1.08,
        showarrow=False,
        font=dict(size=14, color="#4F6FA0")
    )

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        margin=dict(t=160, l=30, r=30, b=30)
    )

    filename = f"preposes_accueil_semaine_{year}_W{week}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    pio.write_image(fig, filepath, format="pdf")

    return html.A(
        "⬇ Télécharger le PDF",
        href=f"/download/{filename}",
        target="_blank"
    )

# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
