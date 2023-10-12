from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent


def get_filtered_text(dom_elem):
    sup = dom_elem.find("sup")
    if sup:
        text = dom_elem.text.rstrip(sup.text)
        return text
    else:
        text = dom_elem.text
        return text


necessary_criteria = [
    "",  # The first row always
    "1. osoba",
    "2. osoba",
    "3. osoba",
    "1. pád",
    "2. pád",
    "3. pád",
    "4. pád",
    "5. pád",
    "6. pád",
    "7. pád",
]

useragent = UserAgent()
headers = {
    "user-agent": useragent.random
}

word_to_translate = "máš"
main_link = f"https://prirucka.ujc.cas.cz/?slovo={word_to_translate}"
req = requests.get(main_link, headers=headers)
soup = BeautifulSoup(req.text, "html.parser")

results = {}
infinitive_form = soup.find(class_="hlavicka").find("strong").text
results["title"] = infinitive_form
descriptions = soup.find_all(class_="polozky")
results["description"] = []
for description in descriptions:
    description_text = get_filtered_text(description)
    results["description"].append(description_text)

results["table"] = []
try:
    table = soup.find(class_="para").find_all("tr")
    for tr in table:
        tr_items = tr.find_all("td")
        row_title = get_filtered_text(tr_items[0])
        if row_title in necessary_criteria:
            singular = get_filtered_text(tr_items[1])
            plural = \
                singular if len(tr_items) == 2 \
                else get_filtered_text(tr_items[2])
            row = [row_title, singular, plural]
            results["table"].append(row)


except AttributeError:
    print("TABLE NOT FOUND!")

# Final result
print(results)
