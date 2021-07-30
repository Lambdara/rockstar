# Rockstar

## Installing the application
I used Python 3.8.10 and Ubuntu 20.04 LTS.

Create a virtualenv and install the packages in requirements.txt. You can use `pip install -r requirements.txt`, though if your python version is slightly different that may not work.

## Running the application
Under your virtualenv with all the packages, do `flask run`. You wouldn't expect it, but Flask is now running and you can talk to it using the provided URL, probably http://127.0.0.1:5000/. You can talk to it using postman, for example.

## The API

- Invalid fields will just be ignored
- All strings are case sensitive unless stated otherwise
- If a requests contains a body, the application expects the header `Content-Type` to be `application/json`.

### Reading artists
You can use a `GET` request on `/artists` to get the info about artists. You can `GET` `/artists/ARTIST_ID` to get info about artist with id `ARTIST_ID`.

You can also filter the list of `/artists` using get parameters `name` and `name[contains]`. `name` will find the artist with the exact name (case sensitive), and `name[contains]` will find the artists whose name contains that string (case insensitive). For example `/artists?name=Metallica` will find Metallica. `/artists/?name[contains]=metal` will find all artists with 'metal' in their name.

### Creating artists
You can use a `POST` request on `/artists` to create a new artist. It is expected that the body is JSON containing the field `name` containing the name. Other parameters are ignored. If successful, the request returns JSON containing `id` which tells you the id of the new artist.

### Modifying artists
You can use a `PATCH` request on `/artists/ARTIST_ID` to modify the artist with id `ARTIST_ID`. Just supply the new `name`.

### Deleting artists
You can use a `DELETE` request on `/artists/ARTIST_ID` to delete the artist, supplied that there's no song using this artist.

### Reading songs
You can use `GET` on `/songs` to get the info about songs. You can `GET` `/songs/SONG_ID` to get info about the song with id `SONG_ID`.

You can also filter the list of `/songs` using get parameters, akin to how you can do so with artists. The full list of parameters is this:

- `id`
- `name`
- `name[contains]`
- `year`
- `year[greater]`
- `year[smaller]`
- `year[geq]`
- `year[seq]`
- `artist_id`
- `shortname`
- `shortname[contains]`
- `bpm`
- `bpm[greater]`
- `bpm[smaller]`
- `bpm[geq]`
- `bpm[seq]`
- `duration`
- `duration[greater]`
- `duration[smaller]`
- `duration[geq]`
- `duration[seq]`
- `genre`
- `genre[contains]`
- `spotify_id`
- `album`
- `album[contains]`

A field without square brackets is just a literal match for that field. With square brackets the filtering is a little different:

- `[contains]` means it will case-insensitively match when the string is contained.
- `[greater]` means it will match numbers which are greater
- `[smaller]` ... smaller
- `[geq]` ... greater or equal
- `[seq]` ... smaller or equal.

These may be combined. For example: `/songs?year[smaller]=2000&genre[contains]=metal` will find metal songs from before 2000.

### Creating songs
You can `POST` to `/songs` to create one. You need to supply JSON in the body containing the following:

- `name`
- `year`
- `artist_id`
- `shortname`
- `bpm`
- `duration`
- `genre`
- `spotify_id`
- `album`

The `year`, `artist_id`, `bpm` and `duration` are integers, the other fields are strings.

Example:

{
    "name": "woop woop",
    "year": 2021,
    "artist_id": 23,
    "shortname": "woopwoop",
    "bpm": 200,
    "duration": 6342,
    "genre": "Snoeiharde Metal",
    "spotify_id": "130-9128390",
    "album": "metaru"
}

The response will contain the `id` of the new song.

### Modifying songs
You can `PATCH` `/songs/SONG_ID` to modify the song with id `SONG_ID`.

The specification of the body is exactly that of when creating a song, omitting any fields you do not want to modify.

### Deleting songs
You can `DELETE` `/songs/SONG_ID` to delete the song with id `SONG_ID`.