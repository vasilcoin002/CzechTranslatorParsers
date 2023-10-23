import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class TextTypes:
    BALD = "bald"
    REGULAR = "regular"
    DESCRIPTION = "description"


class TranslationsEnum:
    EN_CZ = "anglicky_cesky"
    CZ_EN = "cesky_anglicky"


necessary_criteria = [
    "Podstatné jméno",
    "Podstatné jméno, rod ženský",
    "Podstatné jméno, rod mužský",
    "Podstatné jméno, rod střední",
    "Přídavné jméno",
    "Sloveso",
    "Nedokonavé sloveso",
    "Dokonavé sloveso"
    "Příslovce",
    "Spojka",
    "Částice",
    "Předložka",
    "Fráze",
    "Synonyma",
    "Antonyma",
]
# Parameters
word_to_translate = "potřeba"
target_language = TranslationsEnum.CZ_EN

main_url = f"https://slovnik.seznam.cz/preklad/{target_language}/" \
           + "%20".join(word_to_translate.split())  # adding spaces
user_agent = UserAgent()
headers = {"user-agent": user_agent.random}
req = requests.get(main_url, headers=headers)
soup = BeautifulSoup(req.text, 'html.parser')

translatePage_results = soup.find(class_="TranslatePage-results")
translatePage_articles = []
try:
    translatePage_articles = translatePage_results.find_all("article")
except AttributeError:
    print("RESULTS NOT FOUND")

result = {}
for article in translatePage_articles:
    title = article.find("h2").text
    if title in necessary_criteria and title not in ["Synonyma", "Antonyma"]:
        # print(title)
        result[title] = []
        list_items = article.find_all("li")
        for item in list_items:
            row_text = []
            row_elements = item.find_next()  # Only first row, without sub rows
            text_wraps = row_elements.find_all()
            for text_wrap in text_wraps:
                # Checking if tag is a
                if text_wrap.name == "a":
                    row_text.append({
                        "text": text_wrap.text,
                        "textType": TextTypes.BALD
                    })
                elif text_wrap.name == "svg":  # Looking for arrow picture
                    row_text.append({
                        "text": "->",
                        "textType": TextTypes.BALD
                    })
                # Else it can be only span
                else:
                    # Checking if span has not wrapped span
                    span = text_wrap.find()
                    if span is None:
                        text_to_add = text_wrap.text

                        # Without this checking happens bug where in row_text adds two element with the same text,
                        # but in first textType is description and in second textType is regular
                        if len(row_text) >= 1 \
                        and row_text[-1]["text"] != text_to_add:  # Check if text in previous is not the same as current
                            row_text.append({
                                "text": text_wrap.text,
                                "textType": TextTypes.REGULAR
                            })
                    # Else it exactly has wrapped span
                    else:
                        span_class = span.get("class")
                        if span_class:

                            if span_class[0] in ["c", "y", "g", "d", "v", "w", "note"]:
                                row_text.append({
                                    "text": span.text,
                                    "textType": TextTypes.DESCRIPTION
                                })
            result[title].append(row_text)
            # print(row_text)

    elif title in ["Synonyma", "Antonyma"]:
        # print(title)
        text_wraps = article.find_all("a")
        row_text = []
        result[title] = []
        for text_wrap in text_wraps:
            row_text.append({
                "text": text_wrap.text,
                "textType": TextTypes.BALD
            })
        result[title].append(row_text)
        # print(row_text)

# Final result
print(result)
