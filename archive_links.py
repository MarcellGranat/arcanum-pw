import requests
from bs4 import BeautifulSoup
import re

def generate_archive_links(url: str) -> list[str, str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    anchors = soup.select('#content-tree a:nth-child(2)')
    for a in anchors:
        archive_link = a.get('href')
        archive_name = a.text
        if not archive_link.startswith("https://adt.arcanum.com"):
            yield archive_name, f"https://adt.arcanum.com{archive_link}"
        else:
            yield archive_name, archive_link

def generate_archive_decades(url: str) -> list[str, str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    anchors = soup.select('#page-main-content .btn-outline-primary')
    used_links = []
    pattern = re.compile(r"collection/(.*)/") # nepszava
    archive_name = re.search(pattern, url).group(1)

    for a in anchors:
        decade_link = a.get('href')
        decade_name = a.text.strip()
        if decade_link in used_links:
            continue
        used_links.append(decade_link)
        if not decade_link.startswith("https://adt.arcanum.com"):
            yield decade_name, f"https://adt.arcanum.com/hu/collection/{archive_name}/{decade_link}"
        else:
            yield decade_name, decade_link
    
if __name__ == "__main__":
    pesti_hirlap = "https://adt.arcanum.com/hu/collection/PestiHirlap/"
    for link in generate_archive_links(pesti_hirlap):
        print(link)

    for link in generate_archive_decades(pesti_hirlap):
        print(link)
    
    for link in generate_archive_links("https://adt.arcanum.com/hu/collection/PestiHirlap/?decade=1870#collection-contents"):
        print(link)
