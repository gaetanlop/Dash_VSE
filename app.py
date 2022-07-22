import dash
import dash_bootstrap_components as dbc
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import dash_auth
import os

# meta_tags are required for the app layout to be mobile responsive
server = Flask(__name__)
app = dash.Dash(__name__,  server=server, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.server.config["SQLALCHEMY_DATABASE_URI"] = os.environ['SQLALCHEMY_DATABASE_URI']
DATABASE_URL = os.environ['DATABASE_URL']
app.config.suppress_callback_exceptions = True



db = SQLAlchemy(server)
