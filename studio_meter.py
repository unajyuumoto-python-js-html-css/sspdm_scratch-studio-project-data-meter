from __future__ import annotations

import json
import sys
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from time import monotonic, sleep
from typing import Iterable
from urllib.request import Request, urlopen

import scratchattach as sa


LOGIN_USERNAME = "unajyuumoto"
LOGIN_PASSWORD = "taretogohan2"
OUTPUT_DIR = Path(__file__).resolve().parent / "data"
PROJECT_LIMIT = 10000
PROJECT_DETAIL_WORKERS = 16
PROJECT_DETAIL_TIMEOUT = 20
SCRATCH_API_HEADERS = {"User-Agent": "Mozilla/5.0"}

warnings.filterwarnings("ignore", category=sa.LoginDataWarning)


def _as_int(value: object) -> int:
    if value is None:
        return 0
    return int(value)


def _fetch_project_stats(project_id: int) -> dict[str, int]:
    request = Request(
        f"https://api.scratch.mit.edu/projects/{project_id}",
        headers=SCRATCH_API_HEADERS,
    )
    with urlopen(request, timeout=PROJECT_DETAIL_TIMEOUT) as response:
        data = json.load(response)
    stats = data.get("stats", {})
    return {
        "views": _as_int(stats.get("views")),
        "favorites": _as_int(stats.get("favorites")),
        "loves": _as_int(stats.get("loves")),
    }


class _ProgressDisplay:
    def __init__(self, message_builder):
        self._message_builder = message_builder
        self._stop_event = threading.Event()
        self._thread = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            print(f"\r{self._message_builder()}", end="", flush=True)
            sleep(1)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        print(f"\r{self._message_builder()}", end="", flush=True)
        print()


def _collect_totals(project_ids: Iterable[int]) -> dict[str, int]:
    totals = {"views": 0, "favorites": 0, "loves": 0}
    project_ids = list(project_ids)
    processed_count = 0
    count_lock = threading.Lock()
    started_at = monotonic()

    def build_message() -> str:
        with count_lock:
            current = processed_count
        elapsed = int(monotonic() - started_at)
        return f"プロジェクト情報を取得中({current}/{len(project_ids)})   [{elapsed}s]"

    progress = _ProgressDisplay(build_message)
    progress.start()
    try:
        with ThreadPoolExecutor(max_workers=PROJECT_DETAIL_WORKERS) as executor:
            for stats in executor.map(_fetch_project_stats, project_ids):
                with count_lock:
                    processed_count += 1
                totals["views"] += stats["views"]
                totals["favorites"] += stats["favorites"]
                totals["loves"] += stats["loves"]
    finally:
        progress.stop()

    return totals


def measure_studio(studio_id: int | str) -> Path:
    studio_id = int(studio_id)
    sleep(5)
    session = sa.login(LOGIN_USERNAME, LOGIN_PASSWORD)
    studio = session.connect_studio(studio_id)
    started_at = monotonic()
    progress = _ProgressDisplay(
        lambda: f"スタジオからプロジェクト取得中...[{int(monotonic() - started_at)}s]"
    )
    progress.start()
    try:
        projects = studio.projects(limit=PROJECT_LIMIT, offset=0)
    finally:
        progress.stop()
    project_ids = [int(project.id) for project in projects]

    project_count = len(project_ids)
    totals = _collect_totals(project_ids)
    total_views = totals["views"]
    total_favorites = totals["favorites"]
    total_loves = totals["loves"]

    average_views = total_views / project_count if project_count else 0
    average_favorites = total_favorites / project_count if project_count else 0
    average_loves = total_loves / project_count if project_count else 0

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"{timestamp}_studio_{studio_id}.txt"

    lines = [
        f"studio_id: {studio_id}",
        f"project_count: {project_count}",
        f"views_total: {total_views}",
        f"views_average: {average_views:.2f}",
        f"favorite_total: {total_favorites}",
        f"favorite_average: {average_favorites:.2f}",
        f"love_total: {total_loves}",
        f"love_average: {average_loves:.2f}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    if sys.version_info < (3, 11):
        print("Please run with Python 3.11 or later. Example: py -3.11 studio_meter.py 28301482")
        return 1

    if len(sys.argv) != 2:
        print("Usage: py -3.11 studio_meter.py <studio_id>")
        return 1

    try:
        output_path = measure_studio(sys.argv[1])
    except Exception as error:
        print(f"Failed to fetch studio data: {error}")
        return 1

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
