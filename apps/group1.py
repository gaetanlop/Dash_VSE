import dash
import dash_table
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from random import randint
from flask import request
import os
import psycopg2
from sqlalchemy import create_engine
import random


# DATABASE_URL = "test"
DATABASE_URL = os.environ['DATABASE_URL']



from app import app, db
from apps.Help_eval import fact_checking_assignment, get_dataframe


MY_LOADER = dcc.Upload(
    id='upload_dataset_gr1',
    children=html.Div([
        'Drag and Drop the dataset provided (it needs to have a "Tweets" column) or ',
        html.A('Select Files')
    ]),
    style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
    },
    # Allow multiple files to be uploaded
    multiple=False
)


MY_WORDCLOUD = html.Img(id = "wordcloud")


DATATABLE = html.Div([
    html.Div(id = "postgres_datatable"),
    # update once a week
    dcc.Interval(id='interval', interval=86400000*7, n_intervals = 0),
    ],
    style={"display":"none"}
)


MY_INPUT = html.Div(
    [
        dbc.Label("Your expertise"),
        dbc.Input(
            placeholder="Enter up to 10 keywords that most reflect your expertise (topics need to be related to the wordcloud)",
            type="text",
            id="input_gr1",
            size = "lg",
            n_submit=0,
            autoFocus=True,
        ),
        dbc.FormText("Enter your expertise in the box above and click on 'Start task' when you are ready to begin the experiment"),
    ]
)


TEXT = html.Div(id='profile')


BUTTON = dcc.Loading(html.Button('Start task', id='btn', n_clicks=0))
BUTTON_NEXT = html.Div([dcc.Loading(html.Button('Next samples', id='btn_next', n_clicks=0))], style={"display":"none"}, id="display_button_next_gr1")


ASSIGNED_CHECKLIST = dbc.RadioItems(
    options=[],
    value=[],
    id="checklist_assigned",
    labelStyle={"margin-bottom": "50px"},
    # inputStyle={"margin-top": "50px"}
)


TEXT_CHECKLIST = html.Div(id = "text")


INTERVAL = dcc.Interval(id = "interval_pg", interval=86400000*7, n_intervals=0)


DIV_SAVE = html.Div([
    html.Div(id='placeholder', children=[]),
    html.Button('Finish experiment', id='save_to_postgres', n_clicks=0),
    dcc.Store(id="store", data=0),
    dcc.Interval(id='interval', interval=1000)], id = "div_save_gr1", style = {"display":"none"})


card = [
    dbc.CardHeader(html.H5("Group1 assignment")),
    dbc.CardBody(
        [
            dbc.Row([dbc.Col(MY_LOADER)], align="center", style={"marginTop": 30, "width": "100%"}),
            dbc.Row([dbc.Col(MY_WORDCLOUD, width={"size": 6, "offset": 3})], align="center", style={"marginTop": 30, "width": "100%"}),
            dbc.Row([dbc.Col(MY_INPUT)], align="center", style={"marginTop": 30}),
            dbc.Row([dbc.Col(TEXT)], align="center", style={"marginTop": 30}),
            dbc.Row([dbc.Col(BUTTON)], align="center", style={"marginTop": 30}),
            dbc.Row([dbc.Col(TEXT_CHECKLIST)], align="center", style={"marginTop": 30}),
            dbc.Row([dbc.Col(ASSIGNED_CHECKLIST)], align="center", style={"marginTop": 30}),
            dbc.Row([dbc.Col(BUTTON_NEXT)], align="center", style={"marginTop": 30}),
            dbc.Row([dbc.Col(INTERVAL)], align="center", style={"marginTop": 30}),
            dbc.Row([dbc.Col(DATATABLE)], align="center", style={"marginTop": 30}),
            dbc.Row([dbc.Col(DIV_SAVE)], align="center", style={"marginTop": 30}),

        ],
        style={"marginTop": 0, "marginBottom": 0},
    )
]


BODY = dbc.Container(
    [
     dbc.Row([dbc.Col(dbc.Card(card)), ], style={"marginTop": 30}),
     ],
    className="mt-12",
)


layout = html.Div([BODY])


@app.callback(
    Output("stored_dataset_gr1", "data"),
    Output("uid_gr1", "data"),
    Input('upload_dataset_gr1', 'contents'),
    State('upload_dataset_gr1', 'filename')
)
def get_data(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = get_dataframe(list_of_contents, list_of_names)
        if children is not None:
            id = randint(0,100000)
            return children, id
        else:
            return None, None
    return None, None


@app.callback(
    Output("stored_clustering_gr1", "data"),
    Input("btn","n_clicks"),
    State("input_gr1", "value"),
    State("stored_dataset_gr1","data"),
    prevent_initial_call = True
)
def save_clustering(n_clicks, text, df):
    if n_clicks>0:
        if df is not None:
            print("test1")
            df = pd.DataFrame.from_dict(df)
            print("test2")
            df = df[["Tweets"]]
            text = {"Tweets": text}
            df = df.append(text, ignore_index=True)
            dff = fact_checking_assignment(df, 3)
            return dff
        else:
            return None
    else:
        return None


@app.callback(
    Output("wordcloud", "style"),
    Output('wordcloud', 'src'),
    Input("stored_dataset_gr1", "data"),
    prevent_initial_call = True
)
def show_wordcloud(data):
    if data is not None:
        df = pd.DataFrame.from_dict(data)
        tweets = df.Tweets

        plt.subplots(figsize=(8, 8))
        wordcloud = WordCloud(
            background_color='white',
            width=512,
            height=384
        ).generate(' '.join(tweets))

        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        return {'height':'100%', 'width':'100%'}, 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())
    else:
        return {}, ""



@app.callback(Output('postgres_datatable', 'children'),
              [Input('interval_pg', 'n_intervals')])
def populate_datatable(n_intervals):
    con = psycopg2.connect(DATABASE_URL)
    cur = con.cursor()

    query = f"""SELECT * FROM evaluation"""

    df = pd.read_sql(query, con)
    print(df)
    return [
        dash_table.DataTable(
            id="our_table",
            columns=[{
                "name": str(x),
                "id": str(x),
                "deletable": False
            } for x in df.columns],
            data=df.to_dict("records"),
            editable=True,
            row_deletable=True
        )
    ]


@app.callback(
    Output("checklist_assigned", "options"),
    Output("checklist_assigned", "value"),
    Output("text", "children"),
    Output("display_button_next_gr1","style"),
    Output("div_save_gr1","style"),
    Input("btn", "n_clicks"),
    Input("btn_next", "n_clicks"),
    Input("stored_clustering_gr1", "data"),
    prevent_initial_call=True
)
def show_samples(clicks, n_clicks, data):
    if (clicks>0)|(n_clicks>0):
        if data is not None:
            df = pd.DataFrame.from_dict(data)
            df.Tweets = df.Tweets.apply(lambda x: " ".join(x.split()[:100]))
            my_cluster = int(df.tail(1).cluster_labels)
            df.drop(df.tail(1).index, inplace=True)
            samples = {}

            for x in df.cluster_labels.unique(): # totally randomly
                samples[x] = df[df.cluster_labels == x].Tweets.sample(1).values[0]

            options = [{"label": samples[x], "value": y} for x,y in zip(samples,range(3))]
            random.shuffle(options)

            return options, [], html.Plaintext("We ranked tweets from most relevant to less relavant based on your profile.\nFrom those tweets, which one is the most relevant to your expertise?\nClick on the relevant checkbox then press 'Next samples' button.\nRepeat the experiment 5 times and then click on 'Finish experiment'.",
                                                               style={'color': 'green', 'font-weight': 'bold',
                                                                      'font-size': 'large'}), {"display":"block"}, {"display":"block"}
        else:
            return [], [], [()], {"display":"none"}, {"display":"none"}
    else:
        return [], [], [()], {"display":"none"}, {"display":"none"}


@app.callback(
    [Output('placeholder', 'children'),
     Output("store", "data")],
    [Input('save_to_postgres', 'n_clicks'),
     Input("interval", "n_intervals")],
    [State('our_table', 'data'),
     State('store', 'data')],
    prevent_initial_call=True)
def df_to_csv(n_clicks, n_intervals, dataset, s):
    output = html.Plaintext("You have successfully finished the experiment. Thank you for your participation!",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})

    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if input_triggered == "save_to_postgres":
        s = 6
        pg = pd.DataFrame(dataset)

        engine = create_engine(os.environ['DATABASE_URL'])
        # to change
        pg.to_sql("evaluation", engine, if_exists='replace', index=False)

        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s - 1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s


@app.callback(
    Output("our_table", "data"),
    Input("btn_next", "n_clicks"),
    State("checklist_assigned", "value"),
    State("our_table", "data"),
    State("uid_gr1", "data"),
    # State("username", "data"),
    prevent_initial_call = True
)
def store_results(n_clicks, val_assigned, rows, id):
    username = request.authorization['username']
    print(username)
    if n_clicks>0:
        if val_assigned == 0:
            rows.append({"id": id, "group": username, "answer": "True"})
        else:
            rows.append({"id": id,"group": username, "answer": "False"})
    return rows

