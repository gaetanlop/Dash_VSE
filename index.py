from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
# Connect to main app.py file
from app import app, db
from app import server
# Connect to your app pages
from apps import group1, group2, group3, eval
from flask import request
import dash_auth

auth = dash_auth.BasicAuth(app,
                           {"group1":"group1",
                            "group2":"group2",
                            "group3":"group3",
                            "group4":"group4"}
                           )

NAVBAR = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(
                "Group1",
                href='/apps/group1',
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Group2",
                href='/apps/group2',
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Group3",
                href='/apps/group3',
            )
        ),
    ],
    brand="Fact checking evaluation method",
    brand_href="#",
    color="dark",
    dark=True,
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    NAVBAR,
    dcc.Store(id= "number", data=None),
    dcc.Store(id= "number_gr2", data=None),
    dcc.Store(id= "number_gr3", data=None),

    dcc.Loading(dcc.Store(id= "stored_evaluation_data", data=None)),
    dcc.Loading(dcc.Store(id= "stored_dataset_gr1", data=None)),
    dcc.Loading(dcc.Store(id= "stored_clustering_gr1", data=None)),
    dcc.Loading(dcc.Store(id= "assigned_cluster", data=None)),
    dcc.Loading(dcc.Store(id= "random_cluster", data=None)),
    dcc.Loading(dcc.Store(id= "uid_gr1", data=None)),
    dcc.Loading(dcc.Store(id= "username", data=None)),
    dcc.Store(id= "score", data=None),

    dcc.Loading(dcc.Store(id= "stored_clustering_gr2", data=None)),
    dcc.Loading(dcc.Store(id= "stored_dataset_gr2", data=None)),
    dcc.Loading(dcc.Store(id= "stored_evaluation_data_gr2", data=None)),
    dcc.Loading(dcc.Store(id= "assigned_cluster_gr2", data=None)),
    dcc.Loading(dcc.Store(id= "random_cluster_gr2", data=None)),
    dcc.Loading(dcc.Store(id= "uid_gr2", data=None)),
    dcc.Loading(dcc.Store(id= "username_gr2", data=None)),
    dcc.Store(id= "score_gr2", data=None),

    dcc.Loading(dcc.Store(id= "stored_clustering_gr3", data=None)),
    dcc.Loading(dcc.Store(id= "stored_dataset_gr3", data=None)),
    dcc.Loading(dcc.Store(id= "stored_evaluation_data_gr3", data=None)),
    dcc.Loading(dcc.Store(id= "assigned_cluster_gr3", data=None)),
    dcc.Loading(dcc.Store(id= "random_cluster_gr3", data=None)),
    dcc.Loading(dcc.Store(id= "uid_gr3", data=None)),
    dcc.Loading(dcc.Store(id= "username_gr3", data=None)),
    dcc.Store(id= "score_gr3", data=None),
    dcc.Store(id= "store_gr3", data=None),
    dcc.Store(id= "store_cluster_gr3", data=None),

    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/group3':
        return group3.layout
    if pathname == '/apps/group1':
        return group1.layout
    if pathname == '/apps/group2':
        return group2.layout
    else:
        return group1.layout


if __name__ == '__main__':
    app.run_server(debug=True)