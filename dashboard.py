import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Mayiladuthurai Tenders", page_icon="📋", layout="centered")

KEYWORDS = [
    "mayiladuthurai", "nagapattinam", "sirkazhi",
    "tharangambadi", "kuthalam", "poompuhar", "sembanarkoil",
]

URL = "https://tntenders.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


@st.cache_data(ttl=900)
def fetch_tenders():
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    tenders = []
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 4:
            title_cell = cells[0]
            link_tag = title_cell.find("a")
            title = title_cell.get_text(strip=True)
            ref_no = cells[1].get_text(strip=True)
            closing_date = cells[2].get_text(strip=True)
            link = link_tag["href"] if link_tag else None
            if title and ref_no:
                tenders.append({
                    "title": title, "ref_no": ref_no,
                    "closing_date": closing_date, "link": link,
                })
    return tenders


def filter_for_mayiladuthurai(tenders):
    return [t for t in tenders if any(k in t["title"].lower() for k in KEYWORDS)]


st.title("📋 Mayiladuthurai Tenders")
st.caption(f"Last checked: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

if st.button("🔄 Refresh now"):
    st.cache_data.clear()

all_tenders = fetch_tenders()
relevant = filter_for_mayiladuthurai(all_tenders)

st.metric("Matching tenders found", len(relevant))

if not relevant:
    st.info("No Mayiladuthurai-related tenders right now. Check back later.")
else:
    for t in relevant:
        with st.container(border=True):
            st.subheader(t["title"])
            st.write(f"**Ref No:** {t['ref_no']}")
            st.write(f"**Closing date:** {t['closing_date']}")
            if t["link"]:
                st.markdown(f"[Open tender ↗](https://tntenders.gov.in{t['link']})")

with st.expander("See all active tenders state-wide (unfiltered)"):
    for t in all_tenders:
        st.write(f"- {t['title']} ({t['ref_no']})")
