import re
from typing import List

from bs4 import BeautifulSoup
from yandex_music import Artist, Client


TRACK_REGEX = re.compile(r"^.*/album/(?P<album>\d+)/track/(?P<track>\d+)(/?\?.*)?$")
PLAYLIST_REGEX = re.compile(r"^.*/users/(?P<username>[-\w]+)/playlists/(?P<playlist_id>\d+)(/?\?.*)?$")
ARTIST_REGEX = re.compile(r"^.*/artist/(?P<artist>\d+)(/tracks)?(/?\?.*)?$")


def parse_link(link: str) -> str:
    regex = re.compile(r"/album/(?P<album>\d+)/track/(?P<track>\d+)")
    match = regex.search(link)
    album = match.group("album")
    track = match.group("track")
    return f"{track}:{album}"


def get_track_ids(code: str, token: str) -> List[str]:
    client = Client(token).init()
    tracks = []

    for line in code.split("\n"):
        line = line.strip()

        if not line:
            continue

        if match := TRACK_REGEX.search(line):
            tracks.append(f'{match.group("track")}:{match.group("album")}')
            continue

        if match := PLAYLIST_REGEX.search(line):
            playlist = client.users_playlists(match.group("playlist_id"), match.group("username"))
            tracks.extend(track.track.track_id for track in playlist.tracks)
            continue

        if match := ARTIST_REGEX.search(line):
            artist_tracks = client.artists_tracks(match.group("artist"), page_size=500)
            tracks.extend(track.track_id for track in artist_tracks.tracks)

    if tracks:
        return tracks

    soup = BeautifulSoup(code, "html.parser")
    links = [f'https://music.yandex.ru/{a["href"]}' for a in soup.findAll("a", class_="d-track__title", href=True)]
    return [parse_link(link) for link in links]


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


def parse_tracks(track_ids: List[str], token: str, make_link: bool) -> List[dict]:
    client = Client(token).init()
    audios = []

    for track in client.tracks(track_ids):
        track_id, album_id = track.track_id.split(":")

        audio = {
            "album_id": album_id,
            "track_id": track_id,
            "link": f"{track_id}:{album_id}",
            "title": track.title,
            "artist": parse_artist(track.artists)
        }

        if make_link:
            info = track.get_specific_download_info("mp3", 192)
            audio["direct_link"] = info.get_direct_link()

        audios.append(audio)

    return audios
