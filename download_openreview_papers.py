import json
import os
import re
import time
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_JSON = "neurips2025_all_papers.json"
OUT_DIR = "pdfs"
BASE_PDF_URL = "https://openreview.net/pdf?id="

MAX_WORKERS = 32
REQUEST_TIMEOUT = 30
RETRY = 3
SLEEP_BETWEEN_RETRY = 1

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

os.makedirs(OUT_DIR, exist_ok=True)

def safe_filename(name, max_len=120):
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name[:max_len]

def pdf_path(paper):
    title = paper.get("title", paper["id"])
    filename = safe_filename(f"{paper['id']}_{title}.pdf")
    return os.path.join(OUT_DIR, filename)

def download_one(paper):
    out_path = pdf_path(paper)

    if os.path.exists(out_path):
        return "skip", paper["id"]

    url = BASE_PDF_URL + paper["id"]

    for attempt in range(1, RETRY + 1):
        try:
            r = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            r.raise_for_status()

            with open(out_path, "wb") as f:
                f.write(r.content)

            return "ok", paper["id"]

        except Exception as e:
            if attempt == RETRY:
                return f"fail: {e}", paper["id"]
            time.sleep(SLEEP_BETWEEN_RETRY)

def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        papers = json.load(f)

    print(f"Total papers: {len(papers)}")
    print(f"Output dir  : {OUT_DIR}")
    print(f"Workers     : {MAX_WORKERS}\n")

    stats = {"ok": 0, "skip": 0, "fail": 0}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(download_one, p) for p in papers]

        with tqdm(total=len(futures), desc="Downloading PDFs") as pbar:
            for future in as_completed(futures):
                status, pid = future.result()

                if status == "ok":
                    stats["ok"] += 1
                elif status == "skip":
                    stats["skip"] += 1
                else:
                    stats["fail"] += 1
                    tqdm.write(f"[FAIL] {pid} -> {status}")

                pbar.update(1)

    print("\n====== Summary ======")
    print(f"Downloaded : {stats['ok']}")
    print(f"Skipped    : {stats['skip']} (already exists)")
    print(f"Failed     : {stats['fail']}")

if __name__ == "__main__":
    main()
