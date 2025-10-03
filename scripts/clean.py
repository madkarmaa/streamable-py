import shutil
from pathlib import Path
from os import system, name


ROOT: Path = Path(__file__).parent.parent.resolve()

if __name__ == "__main__":
    system("cls" if name == "nt" else "clear")

    to_remove: list[Path] = []
    to_remove.extend(ROOT.glob("**/*cache*"))
    to_remove.extend(ROOT.glob("**/*egg-info*"))

    for path in to_remove:
        shutil.rmtree(path, ignore_errors=True)
