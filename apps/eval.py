# import dash
# import dash_table
# from dash.dependencies import Input, Output, State
# import dash_html_components as html
# import dash_core_components as dcc
# import dash_bootstrap_components as dbc
# import pandas as pd
# from random import shuffle
#
# from app import app, db
# from apps.Help_eval import *
#
# MY_LOADER = dcc.Upload(
#     id='upload_evaluation_data',
#     children=html.Div([
#         'Drag and Drop your dataset or ',
#         html.A('Select Files')
#     ]),
#     style={
#         'width': '100%',
#         'height': '60px',
#         'lineHeight': '60px',
#         'borderWidth': '1px',
#         'borderStyle': 'dashed',
#         'borderRadius': '5px',
#         'textAlign': 'center',
#         'margin': '10px'
#     },
#     # Allow multiple files to be uploaded
#     multiple=False
# )
#
# MY_CHECKLIST = dbc.RadioItems(
#     options=[],
#     value=[],
#     id="checklist",
#     labelStyle={"margin-bottom": "50px"},
#     # inputStyle={"margin-top": "50px"}
# )
#
# MY_BUTTON = html.Button('Start the evaluation process', id='btn', n_clicks=0)
#
# MY_DROPDOWN = dcc.Dropdown(id="my_dropdown",
#                            options=[],
#                            value=[],
#                            multi=True,
#                            optionHeight=35,
#                            placeholder="Please select two columns",
#                            clearable=True
#                            )
#
# MY_TABLE = html.Div([
#     html.Div(id="postgres_datatable"),
#     html.Button('Save to PostgreSQL', id='save_to_postgres', n_clicks=0),
#
#     # Create notification when saving to excel
#     html.Div(id='placeholder', children=[]),
#     dcc.Store(id="store", data=0),
#     # update once a week
#     dcc.Interval(id='interval', interval=86400000 * 7, n_intervals=0),
# ])
#
# MY_RESULT = html.Div(id="result")
# PLAIN_TEXT = html.Div(id="plain_text")
#
# card = [
#     dbc.CardHeader(html.H5("Evaluate your models")),
#     dbc.CardBody(
#         [
#             dbc.Row([dbc.Col(MY_LOADER)], align="center", style={"marginTop": 30, "width": "100%"}),
#             dbc.Row([dbc.Col(MY_DROPDOWN)], align="center", style={"marginTop": 30}),
#             dbc.Row([dbc.Col(MY_BUTTON)], align="center", style={"marginTop": 30}),
#             dbc.Row([dbc.Col(PLAIN_TEXT)], align="center", style={"marginTop": 30}),
#             dbc.Row([dbc.Col(MY_CHECKLIST)], align="center", style={"marginTop": 30}),
#             dbc.Row([dbc.Col(MY_RESULT)], align="center", style={"marginTop": 30}),
#             # dbc.Row([dbc.Col(MY_TABLE)], align="center", style={"marginTop": 30})
#         ],
#         style={"marginTop": 0, "marginBottom": 0},
#     )
# ]
#
# BODY = dbc.Container(
#     [
#      dbc.Row([dbc.Col(dbc.Card(card)), ], style={"marginTop": 30}),
#      ],
#     className="mt-12",
# )
# layout = html.Div([BODY])
#
#
# @app.callback(
#     Output("stored_evaluation_data", "data"),
#     Input('upload_evaluation_data', 'contents'),
#     State('upload_evaluation_data', 'filename')
# )
# def get_data(list_of_contents, list_of_names):
#     if list_of_contents is not None:
#         children = get_dataframe(list_of_contents, list_of_names)
#         if children is not None:
#             return children
#         else:
#             return None
#     return None
#
#
# @app.callback(
#     Output("my_dropdown", "options"),
#     Output("my_dropdown", "value"),
#     Input("stored_evaluation_data", "data"),
# )
# def show_dropdown(df):
#     if df is not None:
#         df = pd.DataFrame.from_dict(df)
#         samples = {}
#         options = [{"label": col, "value": col} for col in df.columns]
#         return options, []
#     else:
#         return [], []
#
#
# @app.callback(
#     Output("checklist", "options"),
#     Output("checklist", "value"),
#     Output("number", "data"),
#     Output("score", "data"),
#     Output("result", "children"),
#     Output("plain_text", "children"),
#     Output("prev_n_clicks", "data"),
#     State("stored_evaluation_data", "data"),
#     Input("btn", "n_clicks"),
#     Input("checklist", "value"),
#     State("number", "data"),
#     State("my_dropdown", "value"),
#     State("score", "data"),
#     State("prev_n_clicks", "data"),
#     prevent_initial_call=True
# )
# def show_samples(df, n_clicks, value, i, columns, score, prev_n_clicks):
#     if df is not None:
#         print(columns)
#         df = pd.DataFrame.from_dict(df)
#         samples = {}
#         if (i is None)|(prev_n_clicks!=n_clicks):
#             i = 0
#         shuffle(columns)
#         for col in columns:
#             print(i)
#             if i == len(df):
#                 if len(value) != 0:
#                     score[value] += 1
#
#                 return [], [], i, score, html.Plaintext(f"{score}", style={'color': 'green', 'font-weight': 'bold',
#                                                                            'font-size': 'large'}), [], prev_n_clicks
#             samples[col] = df[col].iloc[i]
#         if ((score is None) & (len(columns) > 0))|(i==0):
#             score = dict()
#             for col in columns:
#                 score[col] = 0
#             score["both are good"] = 0
#             score["both are bad"] = 0
#
#         options = [{"label": samples[x], "value": x} for x in samples]
#         options.append({"label": "both are good", "value": "both are good"})
#         options.append({"label": "both are bad", "value": "both are bad"})
#         sample = df[df.columns[0]].iloc[i]
#         if len(value) > 0:
#             score[value] += 1
#         if (len(columns) > 0):
#             i += 1
#
#         prev_n_clicks = n_clicks
#         return options, [], i, score, [], html.Plaintext(f"{sample}", style={'color': 'blue', 'font-weight': 'bold',
#                                                                              'font-size': 'large'}), prev_n_clicks
#     else:
#         prev_n_clicks = n_clicks
#         return [], [], None, None, [], [], prev_n_clicks
#
#
#
# # @app.callback(
# #     Output("our_table", "data"),
# #     [Input("btn", "n_clicks")],
# #     [State("checklist", "value"),
# #      State("our_table", "data"),
# #      State("assigned_cluster", "data")]
# # )
# # def store_results(n_clicks, choice, rows, label):
# #     if n_clicks > 1:
# #         if choice == label:
# #             rows.append({"Name":"tester", "Result":True})
# #         else:
# #             rows.append({"Name": "tester", "Result": False})
# #     return rows
# #
# #
# # @app.callback(Output("postgres_datatable", "children"),
# #               Input("interval", "n_intervals"))
# # def populate_datatable(n_intervals):
# #     df = pd.read_sql_table("evaluation", con=db.engine)
# #     return [
# #         dash_table.DataTable(
# #             id = "our_table",
# #             columns = [{
# #                 "name": str(x),
# #                 "id": str(x),
# #                 "deletable": False
# #             } for x in df.columns],
# #             data=df.to_dict("records"),
# #             editable = True,
# #             row_deletable = True
# #         )
# #     ]
