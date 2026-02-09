import os
import base64
from datetime import date
import pandas as pd  # type: ignore
from babel.dates import format_date

import dash  # type: ignore
from dash import dcc, html, Input, Output, State  # type: ignore
import plotly.graph_objects as go  # type: ignore
import plotly.io as pio  # type: ignore

# =========================
# DATA
# =========================
df = pd.read_csv("data/Random_Attendant_Crew_Schedule_2026.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["ISO_Year"] = df["Date"].dt.isocalendar().year
df["ISO_Week"] = df["Date"].dt.isocalendar().week

# =========================
# HELPERS
# =========================


def week_date_range(year, week):
    monday = date.fromisocalendar(year, week, 1)
    sunday = date.fromisocalendar(year, week, 7)
    return monday, sunday


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


JW_LOGO = encode_image("JW_Logo.png")

PDF_EXPORT_DIR = "exports"
os.makedirs(PDF_EXPORT_DIR, exist_ok=True)


# =========================
# WEEK OPTIONS (ASCENDING)
# =========================
week_options = (
    df[["ISO_Year", "ISO_Week"]]
    .drop_duplicates()
    .sort_values(["ISO_Year", "ISO_Week"])
)

week_labels = []
for _, r in week_options.iterrows():
    y, w = int(r.ISO_Year), int(r.ISO_Week)
    monday, sunday = week_date_range(y, w)
    label = (
        f"Semaine {w} "
        f"({format_date(monday, 'short', locale='fr_FR')} – "
        f"{format_date(sunday, 'short', locale='fr_FR')})"
    )
    week_labels.append({
        "label": label,
        "value": f"{y}-W{w}"
    })

today = date.today()
current_week_value = f"{today.isocalendar().year}-W{today.isocalendar().week}"

# =========================
# APP
# =========================
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"fontFamily": "Arial", "backgroundColor": "#F4F6F9"},
    children=[

        # =========================
        # HEADER
        # =========================
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
                html.Div([
                    html.H2(
                        id="dashboard-title",
                        style={"margin": "0"}
                    )
                ])
            ]
        ),

        # =========================
        # CONTROLS
        # =========================
        html.Div(
            style={"padding": "20px"},
            children=[
                dcc.Dropdown(
                    id="week-selector",
                    options=week_labels,  # type: ignore
                    value=current_week_value,
                    clearable=False
                ),
                html.Br(),
                html.Button("Exporter en PDF", id="export-pdf"),
                html.Div(id="export-status")
            ]
        ),

        # =========================
        # TABLE
        # =========================
        dcc.Graph(id="week-table")
    ]
)

# =========================
# CALLBACK – TABLE + TITLE
# =========================


@app.callback(
    Output("week-table", "figure"),
    Output("dashboard-title", "children"),
    Input("week-selector", "value")
)
def update_dashboard(selected_week):
    year, week = selected_week.split("-W")
    year, week = int(year), int(week)

    data = df[
        (df["ISO_Year"] == year) &
        (df["ISO_Week"] == week)
    ].sort_values("Date")

    monday, sunday = week_date_range(year, week)

    title = (
        f"Tableau de Bord des Préposés à l’Accueil — "
        f"Semaine du {format_date(monday, 'long', locale='fr_FR')} "
        f"au {format_date(sunday, 'long', locale='fr_FR')}"
    )

    fig = go.Figure(go.Table(
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

    fig.update_layout(margin=dict(t=20, b=20))

    return fig, title

# =========================
# CALLBACK – PDF EXPORT
# =========================


@app.callback(
    Output("export-status", "children"),
    Input("export-pdf", "n_clicks"),
    State("week-selector", "value"),
    prevent_initial_call=True
)
def export_pdf(n, selected_week):
    year, week = map(int, selected_week.replace("W", "").split("-"))

    data = df[
        (df["ISO_Year"] == year) &
        (df["ISO_Week"] == week)
    ].sort_values("Date")

    monday, sunday = week_date_range(year, week)

    fig = go.Figure()

    fig.add_trace(go.Table(
        header=dict(
            values=["<b>Date</b>", "<b>Entrée</b>", "<b>Porte</b>",
                    "<b>Intérieur</b>", "<b>Comptage</b>"],
            fill_color="#4F6FA0",
            font=dict(color="white", size=10),
            align="left"
        ),
        cells={
            "values": [
                [
                    format_date(d, "medium", locale="fr_FR")
                    for d in data["Date"]
                ],
                data["Entrée"],
                data["Porte"],
                data["Intérieur"],
                data["Comptage"]
            ],
            "font": dict(color="#4F6FA0", size=9),
            "fill_color": "#E9EEF7",
            "align": "left"
        }
    ))

    fig.add_layout_image(
        source=f"data:image/png;base64,{JW_LOGO}",
        xref="paper", yref="paper",
        x=0, y=1.5,
        sizex=0.18, sizey=0.18,
        xanchor="left", yanchor="top"
    )

    fig.add_annotation(
        text="<b>Assemblée locale : Lomé Gakli Centre (950)",
        xref="paper", yref="paper",
        x=0.5, y=1.18,
        showarrow=False,
        font=dict(size=12, color="#4F6FA0")
    )

    fig.add_annotation(
        text=(
            "<b>Préposés à l’accueil pour la semaine "
            f"du {format_date(monday, 'medium', locale='fr_FR')} "
            f"au {format_date(sunday, 'medium', locale='fr_FR')}"
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

    filename = os.path.join(
        PDF_EXPORT_DIR,
        f"preposes_accueil_semaine_{year}_W{week}.pdf"
    )
    pio.write_image(fig, filename, format="pdf")

    return f"PDF généré : {filename}"

# =========================
# RUN
# =========================


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)
