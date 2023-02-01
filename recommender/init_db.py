""" write to a SQLite database with forms, templates
    add new record, delete a record, edit/update a record
    """

from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from datetime import date
import os

app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = os.getenv("RECOMMENDER_SECRET_KEY")

# Flask-Bootstrap requires this line
Bootstrap(app)

# # the name of the database; add path if necessary
# db_name = 'sockmarket.db'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# # this variable, db, will be used for all SQLAlchemy commands
# db = SQLAlchemy(app)
