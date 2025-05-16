from bs4 import BeautifulSoup

def extract_grant_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    data = {}

    # Find general info block
    table_rows = soup.select("table.usa-table--compact tr")
    for row in table_rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            data[label] = value

    # Add description
    description_section = soup.find("h2", string="Additional Information")
    if description_section:
        description_table = description_section.find_next("table")
        if description_table:
            for row in description_table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2 and "Description" in cells[0].text:
                    data["Description"] = cells[1].get_text(separator=" ", strip=True)

    # Add eligibility
    eligibility_section = soup.find("h2", string="Eligibility")
    if eligibility_section:
        eligibility_table = eligibility_section.find_next("table")
        if eligibility_table:
            for row in eligibility_table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(separator=" ", strip=True)
                    data[label] = value

    return data


def main():
    # Load and read the HTML file
    file_path = "grantTest.html"
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Extract and print the data
    grant_data = extract_grant_data(html_content)
    for key, value in grant_data.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()