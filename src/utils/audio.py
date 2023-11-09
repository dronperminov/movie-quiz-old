import re
from typing import List

from yandex_music import Artist, Client

TRACK_REGEX = re.compile(r"^.*/album/(?P<album>\d+)/track/(?P<track>\d+)(/?\?.*)?$")
TRACK_ONLY_REGEX = re.compile(r"^.*/track/(?P<track>\d+)(\?.*)?$")
PLAYLIST_REGEX = re.compile(r"^.*/users/(?P<username>[-\w]+)/playlists/(?P<playlist_id>\d+)(/?\?.*)?$")
ARTIST_REGEX = re.compile(r"^.*/artist/(?P<artist>\d+)(/tracks)?(/?\?.*)?$")
ALBUM_REGEX = re.compile(r"^.*/album/(?P<album>\d+)(/?\?.*)?$")


def get_track_ids(code: str, token: str) -> List[str]:
    client = Client(token).init()
    tracks = []

    for line in code.split("\n"):
        line = line.strip()

        if not line:
            continue

        if match := TRACK_REGEX.search(line):
            tracks.append(match.group("track"))
            continue

        if match := TRACK_ONLY_REGEX.search(line):
            tracks.extend(track.track_id.split(":")[0] for track in client.tracks(f'{match.group("track")}'))
            continue

        if match := PLAYLIST_REGEX.search(line):
            playlist = client.users_playlists(match.group("playlist_id"), match.group("username"))
            tracks.extend(track.track.track_id.split(":")[0] for track in playlist.tracks)
            continue

        if match := ARTIST_REGEX.search(line):
            artist_tracks = client.artists_tracks(match.group("artist"), page_size=500)
            tracks.extend(track.track_id.split(":")[0] for track in artist_tracks.tracks)
            continue

        if match := ALBUM_REGEX.search(line):
            album = client.albums_with_tracks(match.group("album"))

            for volume in album.volumes:
                tracks.extend(track.track_id.split(":")[0] for track in volume)
            continue

    return tracks


def parse_direct_link(track_id: str, token: str) -> str:
    client = Client(token).init()
    track = client.tracks([track_id])[0]
    info = track.get_specific_download_info("mp3", 192)
    return info.get_direct_link()


def parse_artist(artists: List[Artist]) -> str:
    parsed_artists = []

    for artist in artists:
        parsed_artists.append({"id": artist["id"], "name": artist["name"]})

        if not artist.decomposed:
            continue

        for decomposed_artist in artist.decomposed:
            if isinstance(decomposed_artist, Artist):
                parsed_artists.append({"id": decomposed_artist["id"], "name": decomposed_artist["name"]})

    return ", ".join(artist["name"] for artist in parsed_artists)


def parse_lyrics(lyrics_str: str) -> List[dict]:
    lyrics = []

    for line in lyrics_str.split("\n"):
        match = re.search(r"^\[(?P<timecode>\d+:\d+\.\d+)] (?P<text>.*)$", line)
        text = match.group("text")

        if not text:
            continue

        timecode = match.group("timecode")
        minute, second = timecode.split(":")
        time = round(int(minute) * 60 + float(second), 2)
        lyrics.append({"time": time, "text": text})

    return lyrics


def parse_tracks(track_ids: List[str], token: str, make_link: bool) -> List[dict]:
    client = Client(token).init()
    audios = []

    for track in client.tracks(track_ids):
        track_id, album_id = track.track_id.split(":")

        audio = {
            "track_id": track_id,
            "title": track.title,
            "artist": parse_artist(track.artists)
        }

        if make_link:
            info = track.get_specific_download_info("mp3", 192)
            audio["direct_link"] = info.get_direct_link()

        audios.append(audio)

    return audios
