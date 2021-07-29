from flask import Flask, g, request, abort
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


def row_to_artist(row):
    # This translates a database row from artists table to a dict
    return {
        "id": row[0],
        "name": row[1],
    }


@app.route("/artists")
def get_artists():
    db = get_db()
    artists = [row_to_artist(row) for row in db.execute("SELECT * FROM artists")]

    return jsonify(artists)


@app.route("/artists/<int:artist_id>", methods=["GET"])
def get_artist(artist_id):
    db = get_db()
    try:
        artist = [row_to_artist(row) for row in db.execute("SELECT * FROM artists WHERE id = ?", (artist_id,))][0]
    except IndexError:
        return jsonify(error="NOT FOUND"), 404
    return jsonify(artist)


@app.route("/artists/<int:artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    db = get_db()
    db.execute("DELETE FROM artists WHERE id = ?", (artist_id,))
    db.commit()
    return jsonify(success=True), 200


def row_to_song(row):
    # This translates a database row from artists table to a dict
    return {
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


@app.route("/songs")
def get_songs():
    db = get_db()
    songs = [row_to_song(row) for row in db.execute("SELECT * FROM songs")]
    return jsonify(songs)


@app.route("/songs/<int:song_id>", methods=["GET"])
def get_song(song_id):
    db = get_db()
    try:
        song = [row_to_song(row) for row in db.execute("SELECT * FROM songs WHERE id = ?", (song_id,))][0]
    except IndexError:
        return jsonify(error="NOT FOUND"), 404
    return jsonify(song)


@app.route("/songs/<int:song_id>", methods=["DELETE"])
def delete_song(song_id):
    db = get_db()
    db.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    db.commit()
    return jsonify(success=True), 200