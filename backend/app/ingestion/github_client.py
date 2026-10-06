import base64
from typing import Any

import httpx

class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RepoMind/0.1",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    PAGE_SIZE = 100

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.get(f"{self.BASE_URL}{path}", params=params)
            response.raise_for_status()
            return response.json()

    async def _get_paginated(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        first_url = f"{self.BASE_URL}{path}"
        next_url: str | None = first_url

        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            while next_url:
                response = await client.get(
                    next_url,
                    params=params if next_url == first_url else None,
                )
                response.raise_for_status()
                page = response.json()
                if not isinstance(page, list):
                    raise ValueError(f"Expected a list response from GitHub: {path}")
                items.extend(page)
                next_url = response.links.get("next", {}).get("url")

        return items

    async def get_repositories(self, username: str) -> list[dict[str, Any]]:
        return await self._get_paginated(
            f"/users/{username}/repos",
            {"per_page": self.PAGE_SIZE, "sort": "updated", "type": "owner"},
        )

    async def get_commits(self, owner: str, repo: str) -> list[dict[str, Any]]:
        return await self._get_paginated(
            f"/repos/{owner}/{repo}/commits",
            {"per_page": self.PAGE_SIZE},
        )

    async def get_readme(self, owner: str, repo: str):
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.get(f"{self.BASE_URL}/repos/{owner}/{repo}/readme")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
