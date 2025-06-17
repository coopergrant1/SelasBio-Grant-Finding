import requests
from bs4 import BeautifulSoup

url = f"https://www.grants.gov/search-results-detail/358730"
response = requests.get(url, timeout=5)
soup = BeautifulSoup(response.text, 'html.parser')
print(soup)
td = soup.select_one('td[data-v-f8e12040]')
if td:
    p = td.select_one('p')  # first <p> in this <td>
    if p:
        summary = p.get_text(strip=True).replace('Summary: ', '')
        print("Summary:", summary)
    else:
        print("oops")
else:
    print("huh")