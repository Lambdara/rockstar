import sqlite3
import json

# Read artists.json
with open("artists.json") as artists_file:
    artists_data = json.load(artists_file)

# Make a list of all artists
artists = []
for artist_datum in artists_data:
    artists.append(
        {
            "id": int(artist_datum["Id"]),
            "name": artist_datum["Name"],
            "songs": [], # We fill this when assigning artists to songs
        }
    )

# Read songs.json
with open("songs.json") as songs_file:
    songs_data = json.load(songs_file)

# Make a list of all songs
songs = []
for songs_datum in songs_data:
    songs.append(
        {
            "id": int(songs_datum["Id"]),
            "name": songs_datum["Name"],
            "year": int(songs_datum["Year"]),
            "artist": songs_datum["Artist"],
            "shortname": songs_datum["Shortname"],
            "bpm": int(songs_datum["Bpm"]) if songs_datum["Bpm"] else None,
            "duration": int(songs_datum["Duration"]) if songs_datum["Duration"] else None,
            "genre": songs_datum["Genre"],
            "spotify_id": songs_datum["SpotifyId"],
            "album": songs_datum["Album"],
        }
    )

# The list of artists is missing 'A ' and 'The ', so add where missing based on the artists of the songs
# Also assign artist to song by id
# This could be done faster but it's fast enough and just a one time thing so: https://youtu.be/RAA1xgTTw9w
for song in songs:
    for artist in artists:
        if artist["name"] == song["artist"]:
            song["artist_id"] = artist["id"]
            artist["songs"].append(song)
        elif "The " + artist["name"] == song["artist"]:
            song["artist_id"] = artist["id"]
            artist["name"] = "The " + artist["name"]
            artist["songs"].append(song)
        elif "A " + artist["name"] == song["artist"]:
            song["artist_id"] = artist["id"]
            artist["name"] = "The " + artist["name"]
            artist["songs"].append(song)


# Check that we didn't fuck this up: Every song should now have an artist_id
for song in songs:
    assert song.get("artist_id") is not None


# We only want metal artists and artists of songs from before 2016
artists = list(filter(lambda artist: any(song["year"] < 2016 or "Metal" in song["genre"] for song in artist["songs"]), artists))

# We only want songs from before 2016:
songs = list(filter(lambda song: song["year"] < 2016, songs))

# We now have all the songs and artists we want so let's go create the database

# Connect
db = sqlite3.connect("database.db")

# Create table artists
db.execute(
    """
    CREATE TABLE artists (
        id INTEGER PRIMARY KEY NOT NULL,
        name TEXT NOT NULL
    )
    """
)

# Cram the artists in there
for artist in artists:
    db.execute(
        """
        INSERT INTO artists (id, name)
        VALUES (:id, :name)
        """,
        artist
    )

# Create table songs
# If this was a proper database we would be using VARCHARS instead of TEXT but it's sqlite so who cares
db.execute(
    """
    CREATE TABLE songs (
        id INTEGER PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        year INTEGER,
        artist_id INTEGER NOT NULL,
        shortname TEXT,
        bpm INTEGER,
        duration INTEGER,
        genre TEXT,
        spotify_id TEXT,
        album TEXT,
        FOREIGN KEY (artist_id) REFERENCES artists(id)
    )
    """
)

# Songs go into the database
for song in songs:
    db.execute(
        """
        INSERT INTO songs (id, name, year, artist_id, shortname, bpm, duration, genre, spotify_id, album)
        VALUES (:id, :name, :year, :artist_id, :shortname, :bpm, :duration, :genre, :spotify_id, :album)
        """,
        song
    )