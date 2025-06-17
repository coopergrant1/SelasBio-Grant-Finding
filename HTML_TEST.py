import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# ------------------------------------------------------------------------------
# STEP 1: Use Selenium to render the page first
# ------------------------------------------------------------------------------

def fetch_grant_summary(opp_id):
    url = f"https://www.grants.gov/search-results-detail/{opp_id}"

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(5)

    rendered_html = driver.page_source
    driver.quit()

    # ------------------------------------------------------------------------------
    # STEP 2: Parse rendered page with BeautifulSoup
    # ------------------------------------------------------------------------------

    soup = BeautifulSoup(rendered_html, 'html.parser')
    tds = soup.select('td[data-v-f8e12040]')

    for td in tds:
        p = td.select_one('p')
        if p and p.text.startswith('Summary:'):
            return p.text.replace('Summary: ', '')

    return "Summary not found."

# ------------------------------------------------------------------------------
# STEP 3: Example usage
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    opportunity_id = "358730"  # Example opportunityId
    summary = fetch_grant_summary(opportunity_id)
    print("Summary :", summary)
