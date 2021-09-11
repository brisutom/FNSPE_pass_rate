import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output


department_codes = {"01": "KM", "02": "KF", "04": "KHV", "11": "KIPL", "12":
                    "KFE", "14": "KMAT", "15": "KJCH", "16": "KDAIZ", "17":
                    "KJR", "18": "KSI", "818": "Děčín", "802": "Děčín", "00":
                    "Fakultní"}
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = pd.read_csv("data/merged.csv", usecols=["name", "enrolled", "passed",
                                        "pass rate", "semester"])
df = df[df["enrolled"] != 0]
df.dropna(subset=["pass rate"], inplace=True)
df["code"] = df["name"].str.extract(r'\[([^]]+)\]')[0]
df["department"] = df["code"].str.extract(r'(\d+)')[0]
df = df.replace({"department": department_codes})
df["season"] = df["semester"].str.extract(r'(\w\w)')[0]
df["year"] = df["semester"].str.extract(r'(\d\d\d\d)')[0]
df_means_by_semester = df.groupby("semester").mean()
df_means_by_department = df.groupby(["department", "season"], as_index=False).mean()

fig = px.bar(df_means_by_department, x="department", y="pass rate",
             color="season", barmode="group", category_orders={"season":
                                                               ["ZS", "LS"]})

app.layout = html.Div(children=[
    html.H1(children='', id="headline"),

    dcc.Dropdown(id="dropdown", clearable=False,
                 style={"width": "50%"},
                 options=[
                    {"label": "2015", "value": "2015"},
                    {"label": "2016", "value": "2016"},
                    {"label": "2017", "value": "2017"},
                    {"label": "2018", "value": "2018"},
                    {"label": "All years", "value": "all"}
                 ], value="all"),
    dcc.Graph(
        id='barplot',
        figure=fig
    )
])


@app.callback(
    Output(component_id='barplot', component_property='figure'),
    Input(component_id='dropdown', component_property='value')
)
def graph_update(selected_year):
    if selected_year == "all":
        filtered_df = df
    else:
        filtered_df = df[df.year == selected_year]
    filtered_means = filtered_df.groupby(["department", "season"],
                                         as_index=False).mean()
    fig = px.bar(filtered_means, x="department", y="pass rate", color="season",
                 barmode="group", category_orders={"season": ["ZS", "LS"]})
    fig.update_layout(transition_duration=1000)
    return fig


@app.callback(
    Output(component_id="headline", component_property="children"),
    Input(component_id="dropdown", component_property="value")
)
def update_headline(selected_year):
    if selected_year == "all":
        selected_year = "all years"
    return "Mean pass rate at FNSPE by departments and season in {}".format(selected_year)


if __name__ == '__main__':
    app.run_server(debug=True)
