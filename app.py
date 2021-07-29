from flask import Flask, g
from flask.json import jsonify
import sqlite3

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
    artists = [
        {
            "id": row[0],
            "name": row[1],
        }
        for row in db.execute("SELECT * FROM artists")
    ]

    return jsonify(artists)


@app.route("/songs")
def list_songs():
    db = get_db()
    artists = [
        {
            "id": row[0],
            "name": row[1],
            "year": row[2],
            "artist": row[3],
            "shortname": row[4],
            "bpm": row[5],
            "duration": row[6],
            "genre": row[7],
            "spotify_id": row[8],
            "album": row[9],
        }
        for row in db.execute("SELECT * FROM songs")
    ]

    return jsonify(artists)
