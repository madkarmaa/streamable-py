from tomlkit import loads, dumps, TOMLDocument  # type: ignore
from httpx import get, Response
from pathlib import Path
from argparse import ArgumentParser


def fetch_keywords(repo_owner: str, repo_name: str) -> list[str]:
    """Fetch repository topics from GitHub API.

    Args:
        repo_owner: GitHub username or organization name
        repo_name: GitHub repository name

    Returns:
        List of topic strings from the repository
    """
    repo_owner = repo_owner.strip()
    repo_name = repo_name.strip()

    response: Response = get(
        f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    ).raise_for_status()
    return response.json()["topics"] or []


PROJECT_TOML: Path = Path(__file__).parent.parent.joinpath("pyproject.toml").resolve()

if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("repo_owner", help="GitHub repository owner")
    parser.add_argument("repo_name", help="GitHub repository name")

    args: dict[str, str] = vars(parser.parse_args())

    keywords: list[str] = fetch_keywords(
        args["repo_owner"].strip(), args["repo_name"].strip()
    )
    project_doc: TOMLDocument = loads(PROJECT_TOML.read_text())
    project_doc["project"]["keywords"] = keywords  # type: ignore
    PROJECT_TOML.write_text(dumps(project_doc))
