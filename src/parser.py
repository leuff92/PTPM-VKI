import requests
from bs4 import BeautifulSoup


class ForumParser:
    def parse_page(self, url: str) -> list[dict]:
        response = requests.get(
            url,
            headers={"User-Agent": "Lab5ForumParser/1.0"},
            timeout=10,
        )
        response.raise_for_status()
        return self.parse_html(response.content)

    def parse_html(self, html: str | bytes) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        comments = []
        for block in soup.select(".comment"):
            author = block.select_one(".author")
            message = block.select_one(".message")
            comment_id = block.get("data-id", "")
            if author is None or message is None:
                continue
            try:
                comment_id = int(comment_id)
            except ValueError:
                continue
            comments.append(
                {
                    "id": comment_id,
                    "name": author.get_text(strip=True),
                    "message": message.decode_contents().strip(),
                }
            )
        return comments

    def save_to_db(self, parsed_data, repository) -> int:
        saved = 0
        for comment in parsed_data:
            if repository.get_by_id(comment["id"]) is None:
                repository.add(comment["id"], comment["name"], comment["message"])
                saved += 1
        return saved
