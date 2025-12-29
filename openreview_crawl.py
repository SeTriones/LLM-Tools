import openreview
import json
from tqdm import tqdm

BASE_URL = "https://api2.openreview.net"
VENUE_ID = "NeurIPS.cc/2025/Conference"
OUTPUT_FILE = "neurips2025_all_papers.json"

client = openreview.api.OpenReviewClient(
    baseurl=BASE_URL
)

def fetch_all_submissions():
    print(f"Fetching all submissions for venue: {VENUE_ID}")
    all_notes = client.get_all_notes(
        content={"venueid": VENUE_ID}
    )
    print(f"Total notes fetched: {len(all_notes)}")
    return all_notes

def save_papers(notes, filename):
    papers = []
    for note in notes:
        papers.append({
            "id": note.id,
            "title": note.content.get("title", {}).get("value"),
            "abstract": note.content.get("abstract", {}).get("value"),
            "authors": note.content.get("authorids", {}).get("value"),
            "pdf": note.content.get("pdf", {}).get("value")
        })
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(papers)} papers to {filename}")

if __name__ == "__main__":
    notes = fetch_all_submissions()
    save_papers(notes, OUTPUT_FILE)

