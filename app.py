from flask import Flask, g
import sqlite3
from flask.cli import with_appcontext

app = Flask(__name__)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("database.db")
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def show_index():
    return '<a href="/artists">Artists</a><br><a href="/songs">Songs</a>'


@app.route("/artists")
def hello_world():
    db = get_db()
    return "<br>".join([str(row) for row in db.execute("SELECT * FROM artists")])


@app.route("/songs")
def list_songs():
    db = get_db()
    return "<br>".join([str(row) for row in db.execute("SELECT * FROM songs")])
