import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup


class CitatyParser:
    def parse_movie_cites(self, page: int) -> Optional[List[dict]]:
        response = requests.get(f"https://citaty.info/movie?page={page}")

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        cites = []

        for node in soup.find_all("article", class_="node-quote-film"):
            cite = node.find_all("p")[0].text.strip()
            movie_link = node.find_all("a", href=re.compile("^https://citaty.info/movie/.*"))[0]
            cites.append({"text": cite, "movie_name": movie_link.text, "url": movie_link["href"]})

        return cites

    def parse_movie(self, movie_link: str, movie_name: str) -> Optional[dict]:
        response = requests.get(movie_link)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        description = "\n".join([p.text for p in soup.find_all("div", class_="field-name-description-field")[0].find_all("p")])
        slogan = soup.find_all("div", class_="field-name-field-tagline")
        slogan = slogan[0].find_all("div", class_="field-items")[0].text.strip() if slogan else ""

        return {"name": movie_name, "description": description, "slogan": slogan}
