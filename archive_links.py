import requests
from bs4 import BeautifulSoup
import re
from typing import Generator, Tuple

def send_request(url):
    # MagyarCompass
    # GET https://adt.arcanum.com/hu/collection/MagyarCompass/

    try:
        response = requests.get(
            url=url,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Sec-Fetch-Site": "none",
                "Cookie": "_ga_1N67Y7BD16=GS1.1.1743278763.22.1.1743280261.15.0.0; _ga=GA1.1.1220155975.1736329765; _gcl_au=1.1.772634911.1736329794; AWSALBAPP-0=_remove_; AWSALBAPP-1=_remove_; AWSALBAPP-2=_remove_; AWSALBAPP-3=_remove_; csrftoken=hpRInEpcc6vRFRO0Jdp672GZvQbA5OWU; sessionid=pzwflmydzh9qgz5l1lvucylusyb3k74y; g_state={\"i_p\":1745697966163,\"i_l\":4}; _fbp=fb.1.1736329764732.565159013811240797; _ga_XJSH2D56XD=GS1.1.1743278752.20.1.1743278762.0.0.0; CookieConsent={stamp:%27s+WDrd9BrQ6akHuERfn/kSLAzCJqGzbsjNf+LPaaXmpc65zNlqFgkA==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1736329793528%2Cregion:%27hu%27}",
                "Sec-Fetch-Mode": "navigate",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
                "Accept-Language": "en-GB,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Sec-Fetch-Dest": "document",
                "Priority": "u=0, i",
            },
        )
        return response
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


def generate_archive_links(url: str) -> Generator[Tuple[str, str], None, None]:
    response = send_request(url)
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
