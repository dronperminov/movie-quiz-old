import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup


class CiteParser:
    def parse_films(self) -> Optional[List[dict]]:
        response = requests.get("https://цитаты-из-фильмов.рф/allmovies/")

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        block = soup.find_all("div", class_="all")[0]
        films = []

        for div in block.find_all("div"):
            child = div.findChild()

            if not child or child.name != "a":
                continue

            while child and child.get("class", []) != ["all"]:
                child.extract()
                child = div.findChild()

            match = re.search(r"^(?P<name>.*) \(.*(?P<year>\d\d\d\d)\)$", div.text)

            if not match:
                continue

            films.append({"url": f'https://цитаты-из-фильмов.рф/{child["href"]}', "name": match.group("name"), "year": int(match.group("year"))})

        return films

    def parse_cites(self, film_url: str) -> List[str]:
        response = requests.get(film_url)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        block = soup.find_all("div", {"id": "phrases"})[0]
        lines = [line.strip() for line in block.get_text(separator="\n").split("\n") if line.strip()]
        cites = []
        cite = []
        for line in lines:
            if line == "* * *":
                if len(cite) < 13:
                    cites.append("\n".join(cite))
                cite = []
            elif line not in {"Смотреть (добавить) отзывы", "Наверх"}:
                cite.append(re.sub(r"^- ", "— ", line))

        if cite and cites:
            cites.append("\n".join(cite))

        if len(cites) < 3:
            return []

        return cites[1:]
