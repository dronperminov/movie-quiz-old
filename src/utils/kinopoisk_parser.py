import os
from typing import List, Optional

import requests
from bs4 import BeautifulSoup


class KinopoiskParser:
    def __init__(self, cookies: str, links_dir: str = "links", films_dir: str = "films", pages_dir: str = "pages") -> None:
        self.cookies = cookies
        self.links_dir = links_dir
        self.films_dir = films_dir
        self.pages_dir = pages_dir

        os.makedirs(self.links_dir, exist_ok=True)
        os.makedirs(self.films_dir, exist_ok=True)
        os.makedirs(self.pages_dir, exist_ok=True)

    def download_page(self, url: str) -> Optional[str]:
        headers = {
            "authority": "www.kinopoisk.ru",
            "method": "GET",
            "scheme": "https",
            "path": url,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.9",
            "Cache-Control": "max-age=0",
            "Cookie": self.cookies,
            "Referer": "https://sso.kinopoisk.ru/",
            "Sec-Ch-Ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }

        response = requests.get(f"https://www.kinopoisk.ru{url}", headers=headers)
        return response.text if response.status_code == 200 else None

    def get_page_text(self, page: int, top: str) -> str:
        page_path = f"{self.pages_dir}/{top}_page{page}.html"

        while not os.path.isfile(page_path):
            text = self.download_page(f"/lists/movies/{top}/?page={page}")

            if text is None:
                print(f"Unable to download page {page + 1}")  # noqa
                continue

            with open(page_path, "w", encoding="utf-8") as f:
                f.write(text)
                break

        with open(page_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_links(self, top: str, pages: int) -> List[str]:
        links = []

        for page in range(pages):
            text = self.get_page_text(page + 1, top)
            soup = BeautifulSoup(text, "html.parser")

            for link in soup.findAll("a", class_="base-movie-main-info_link__YwtP1", href=True):
                links.append(f'https://kinopoisk.ru{link["href"]}')

        return links

    def download_list(self, top: str, pages: int) -> None:
        links = self.get_links(top, pages)

        with open(f"{self.links_dir}/{top}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(links))
