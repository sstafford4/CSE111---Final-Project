from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

# ok, so this will create a new sqlite database file for us if it doesnt already exist.
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Checkpoint3.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db = SQLAlchemy(app)