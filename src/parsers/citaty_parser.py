import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup


class CitatyParser:
    def parse_movie(self, page: int) -> Optional[List[dict]]:
        url = f"https://citaty.info/movie?page={page}"
        response = requests.get(url)

        if response.status_code != 200:
            return None

        content = response.text
        soup = BeautifulSoup(content, "html.parser")
        cites = []

        for node in soup.find_all("article", class_="node-quote-film"):
            cite = node.find_all("p")[0].text.strip()
            movie_link = node.find_all("a", href=re.compile("^https://citaty.info/movie/.*"))[0]

            print(cite)
            print(movie_link.text, movie_link["href"])
            print("-------------------------------")
            cites.append({"text": cite, "movie_name": movie_link.text, "url": movie_link["href"]})

        return cites
