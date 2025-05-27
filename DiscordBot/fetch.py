from dotenv import load_dotenv
import os, requests

# Load .env variables
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
CX      = os.getenv("GOOGLE_CX")

# Refined prompts to emphasize actual photos of each figure
TERMS = [
    # Kamala Harris
    "photo of Kamala Harris speaking at a campaign rally",
    "official portrait of Kamala Harris",
    "press photo of Kamala Harris in a press conference",
    "photo of Kamala Harris meeting small business owners",
    "photo of Kamala Harris touring a factory",

    # Donald Trump
    "photo of Donald Trump at a campaign rally",
    "official portrait of Donald Trump",
    "press photo of Donald Trump signing an executive order",
    "photo of Donald Trump golfing at Mar-a-Lago",
    "photo of Donald Trump in an interview on set",

    # Joe Biden
    "photo of Joe Biden giving a keynote speech",
    "official portrait of Joe Biden",
    "photo of Joe Biden meeting school children",
    "photo of Joe Biden visiting a manufacturing plant",
    "press photo of Joe Biden in a press briefing",

    # Barack Obama
    "photo of Barack Obama delivering commencement address",
    "official portrait of Barack Obama",
    "photo of Barack Obama meeting community leaders",
    "press photo of Barack Obama in a televised interview",
    "photo of Barack Obama participating in a discussion panel",

    # Nancy Pelosi
    "photo of Nancy Pelosi presiding over a House session",
    "official portrait of Nancy Pelosi",
    "press photo of Nancy Pelosi speaking at a press conference",
    "photo of Nancy Pelosi touring a hospital",
    "photo of Nancy Pelosi meeting veterans",

    # Bernie Sanders
    "photo of Bernie Sanders at a town hall meeting",
    "official portrait of Bernie Sanders",
    "press photo of Bernie Sanders speaking at a rally",
    "photo of Bernie Sanders in a one-on-one interview",
    "photo of Bernie Sanders visiting a union hall",

    # Alexandria Ocasio-Cortez
    "photo of Alexandria Ocasio-Cortez on the House floor",
    "official portrait of Alexandria Ocasio-Cortez",
    "photo of Alexandria Ocasio-Cortez speaking to constituents",
    "photo of Alexandria Ocasio-Cortez in a panel discussion",
    "photo of Alexandria Ocasio-Cortez at a community event",

    # Mitch McConnell
    "photo of Mitch McConnell addressing the Senate",
    "official portrait of Mitch McConnell",
    "press photo of Mitch McConnell in a press briefing",
    "photo of Mitch McConnell at a fundraising dinner",
    "photo of Mitch McConnell meeting foreign dignitaries",
]

MAX_TOTAL     = 500       # total cap across all terms
MAX_PER_TERM  = 15       # cap per term to avoid too many calls
BASE_SAVE_DIR = "real_photos"

def fetch_images(term, global_counter):
    term_folder = term.replace(' ', '_')
    downloaded  = 0

    for start in range(1, MAX_PER_TERM + 1, 10):
        if global_counter["count"] >= MAX_TOTAL or downloaded >= MAX_PER_TERM:
            return

        params = {
            "q": term,
            "cx": CX,
            "key": API_KEY,
            "searchType": "image",
            "num": 10,
            "start": start
        }
        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if not items:
            break

        for item in items:
            if global_counter["count"] >= MAX_TOTAL or downloaded >= MAX_PER_TERM:
                return

            url = item.get("link")
            if not url:
                continue

            ext = os.path.splitext(url)[1].split("?")[0] or ".jpg"
            fname = f"{term_folder}_{downloaded:04d}{ext}"
            path  = os.path.join(BASE_SAVE_DIR, fname)

            try:
                img_data = requests.get(url, timeout=5).content
                with open(path, "wb") as f:
                    f.write(img_data)
                downloaded += 1
                global_counter["count"] += 1
            except Exception:
                continue

if __name__ == "__main__":
    if not API_KEY or not CX:
        print("❗️ Set GOOGLE_API_KEY and GOOGLE_CX in your environment or .env file.")
    else:
        os.makedirs(BASE_SAVE_DIR, exist_ok=True)
        global_counter = {"count": 0}

        for term in TERMS:
            print(f"Fetching images for '{term}' ({global_counter['count']}/{MAX_TOTAL}) ...")
            fetch_images(term, global_counter)
            if global_counter["count"] >= MAX_TOTAL:
                break

        print(f"Done. Total images downloaded: {global_counter['count']}")
