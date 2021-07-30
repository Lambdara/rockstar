from logging import error
from re import A
from sqlite3.dbapi2 import IntegrityError
from flask import Flask, g, request
from flask.json import jsonify
import sqlite3

app = Flask(__name__)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("database.db")
        db.execute("PRAGMA foreign_keys = 1")
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


@app.route("/artists", methods=["GET"])
def get_artists():
    db = get_db()
    artists = [row_to_artist(row) for row in db.execute("SELECT * FROM artists")]

    return jsonify(artists)


@app.route("/artists", methods=["POST"])
def create_artist():
    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO artists (name)
            VALUES (:name)
            """,
            request.json,
        )
    except sqlite3.IntegrityError as error:
        return jsonify(error=str(error)), 400
    db.commit()
    return jsonify(success=True), 200


@app.route("/artists/<int:artist_id>", methods=["GET"])
def get_artist(artist_id):
    db = get_db()
    try:
        artist = [
            row_to_artist(row)
            for row in db.execute("SELECT * FROM artists WHERE id = ?", (artist_id,))
        ][0]
    except IndexError:
        return jsonify(error="NOT FOUND"), 404
    return jsonify(artist)


@app.route("/artists/<int:artist_id>", methods=["PATCH"])
def update_artist(artist_id):
    db = get_db()
    try:
        artist = [
            row_to_artist(row)
            for row in db.execute("SELECT * FROM artists WHERE id = ?", (artist_id,))
        ][0]
    except IndexError:
        return jsonify(error="NOT FOUND"), 404

    for key in request.json:
        artist[key] = request.json[key]
    artist["id"] = artist_id

    db.execute(
        """
        UPDATE artists
        SET name = :name
        WHERE id = :id
        """,
        artist,
    )

    db.commit()
    return jsonify(success=True), 200


@app.route("/artists/<int:artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    try:
        db = get_db()
        db.execute("DELETE FROM artists WHERE id = ?", (artist_id,))
        db.commit()
    except IntegrityError as error:
        return jsonify(error=str(error))
    return jsonify(success=True), 200


def row_to_song(row):
    # This translates a database row from artists table to a dict
    return {
        "id": row[0],
        "name": row[1],
        "year": row[2],
        "artist_id": row[3],
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
    query = "SELECT * FROM songs"

    arg_setup = {
        "id": "id = :id",
        "name": "name = :name",
        "name[contains]": "name LIKE :name",
        "year": "year = :year",
        "year[greater]": "year > :year",
        "year[smaller]": "year < :year",
        "year[geq]": "year >= :year",
        "year[seq]": "year <= :year",
        "artist_id": "artist_id = :artist_id",
        "shortname": "shortname = :shortname",
        "shortname[contains]": "shortname LIKE :shortname",
        "bpm": "bpm = :bpm",
        "bpm[greater]": "bpm > :bpm",
        "bpm[smaller]": "bpm < :bpm",
        "bpm[geq]": "bpm >= :bpm",
        "bpm[seq]": "bpm <= :bpm",
        "duration": "duration = :duration",
        "duration[greater]": "duration > :duration",
        "duration[smaller]": "duration < :duration",
        "duration[geq]": "duration >= :duration",
        "duration[seq]": "duration <= :duration",
        "genre": "genre = :genre",
        "genre[contains]": "genre LIKE :genre",
        "spotify_id": "spotify_id = :spotify_id",
        "album": "album = :album",
        "album[contains]": "album LIKE :album",
    }

    filters = []

    args = dict()
    for arg in request.args:
        if arg in arg_setup.keys():
            filters.append(" " + arg_setup[arg])
        arg_key = arg.split("[")[0]
        args[arg_key] = request.args[arg]
        if "LIKE" in arg_setup[arg]:
            args[arg_key] = "%" + args[arg_key] + "%"

    if filters:
        query += " WHERE " + " AND ".join(filters)
    print(query)
    print(args)

    songs = [row_to_song(row) for row in db.execute(query, args)]

    return jsonify(songs)


@app.route("/songs/<int:song_id>", methods=["GET"])
def get_song(song_id):
    db = get_db()
    try:
        song = [
            row_to_song(row)
            for row in db.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        ][0]
    except IndexError:
        return jsonify(error="NOT FOUND"), 404
    return jsonify(song)


@app.route("/songs/<int:song_id>", methods=["PATCH"])
def update_song(song_id):
    db = get_db()

    try:
        song = [
            row_to_song(row)
            for row in db.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        ][0]
    except IndexError:
        return jsonify(error="NOT FOUND"), 404

    for key in request.json:
        song[key] = request.json[key]
    song["id"] = song_id

    try:
        db.execute(
            """
            UPDATE songs 
            SET name = :name, year = :year, artist_id = :artist_id, 
                shortname = :shortname, bpm = :bpm, duration = :duration, 
                genre = :genre, spotify_id = :spotify_id, album = :album
            WHERE id = :id
            """,
            song,
        )
    except IntegrityError as error:
        return jsonify(error=str(error)), 400

    db.commit()
    return jsonify(success=True), 200


@app.route("/songs", methods=["POST"])
def create_song():
    db = get_db()

    for key in [
        "name",
        "year",
        "artist_id",
        "shortname",
        "bpm",
        "duration",
        "genre",
        "spotify_id",
        "album",
    ]:
        if key not in request.json:
            return jsonify(error=f"Missing key '{key}'")

    try:
        db.execute(
            """
            INSERT INTO songs (name, year, artist_id, shortname, bpm, duration, genre, spotify_id, album)
            VALUES (:name, :year, :artist_id, :shortname, :bpm, :duration, :genre, :spotify_id, :album)
            """,
            request.json,
        )
    except sqlite3.IntegrityError as error:
        return jsonify(error=str(error)), 400

    db.commit()
    return jsonify(success=True), 200


@app.route("/songs/<int:song_id>", methods=["DELETE"])
def delete_song(song_id):
    db = get_db()
    db.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    db.commit()
    return jsonify(success=True), 200
