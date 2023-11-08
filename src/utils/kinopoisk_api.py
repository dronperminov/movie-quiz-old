import random
import time
from collections import defaultdict
from typing import Dict, List, Union

import requests


class KinopoiskAPI:
    def __init__(self, tokens: List[str]) -> None:
        self.tokens = {token: True for token in tokens}

    def get_films_by_ids(self, film_ids: List[Union[int, str]], bucket_size: int = 1000) -> List[dict]:
        films = []

        for bucket in range((len(film_ids) + bucket_size - 1) // bucket_size):
            films.extend(self.__get_films_by_ids_partial(film_ids[bucket * bucket_size:(bucket + 1) * bucket_size]))

        return films

    def get_images_by_ids(self, film_ids: List[int]) -> Dict[int, List[dict]]:
        params = [f"movieId={film_id}" for film_id in film_ids]
        response = self.__get_images(params)
        images = response["docs"]

        while response["page"] < response["pages"]:
            print(response["page"], "/", response["pages"])  # noqa
            response = self.__get_images(params + [f'page={response["page"] + 1}'])
            images.extend(response["docs"])

        film_id2images = defaultdict(list)

        for image in images:
            film_id2images[image["movieId"]].append(image)

        return film_id2images

    def __get_films_by_ids_partial(self, film_ids: List[Union[int, str]]) -> List[dict]:
        if not film_ids:
            return []

        params = [f"id={film_id}" for film_id in film_ids]
        response = self.__get_films(params)
        films = response["docs"]
        print(f'films: {response["pages"]} pages')  # noqa

        while response["page"] < response["pages"]:
            print(f'films {response["page"] + 1} / {response["pages"]}')  # noqa
            response = self.__get_films(params + [f'page={response["page"] + 1}'])
            films.extend(response["docs"])

        return films

    def __get_films(self, query_params: List[str]) -> dict:
        params = ["limit=250", *query_params]
        fields = [
            "id", "name", "type", "enName", "year",
            "slogan", "description", "shortDescription",
            "rating", "movieLength", "backdrop", "genres",
            "countries", "persons", "top250", "facts",
            "videos", "poster", "alternativeName", "names"
        ]

        for field in fields:
            params.append(f"selectFields={field}")

        return self.__api_request(f'/v1.4/movie?{"&".join(params)}')

    def __get_images(self, query_params: List[str]) -> dict:
        params = ["limit=250", "type=screenshot", "type=still", *query_params]
        return self.__api_request(f'/v1/image?{"&".join(params)}')

    def __api_request(self, url: str) -> dict:
        while True:
            available_tokens = [token for token, is_available in self.tokens.items() if is_available]

            if not available_tokens:
                print(f"WARNING! no available tokens")  # noqa

                for token in self.tokens:
                    self.tokens[token] = True

                time.sleep(10)
                continue

            token = random.choice(available_tokens)
            response = requests.get(f"https://api.kinopoisk.dev{url}", headers={
                "accept": "application/json",
                "X-API-KEY": token
            })

            if response.status_code == 200:
                return response.json()

            if response.status_code == 403:
                self.tokens[token] = False
                print(f"WARNING! 403 error ({response.text})")  # noqa
                continue

            time.sleep(5)
