from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

# import beautifulsoup4
import re
import requests
from bs4 import BeautifulSoup
import json


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

website_url_info_history_pb = ["https://en.wikipedia.org/wiki/Pittsburgh", "https://en.wikipedia.org/wiki/History_of_Pittsburgh",
                    "https://www.britannica.com/place/Pittsburgh", "https://www.visitpittsburgh.com/",
                    "https://www.pittsburghpa.gov/City-Government/Finances-Budget/Taxes/Tax-Forms"]
pdf_url_info_history_pb = ["https://apps.pittsburghpa.gov/redtail/images/23255_2024_Operating_Budget.pdf"]


special_website_url_event_pb = ["https://downtownpittsburgh.com/events/"]
website_url_event_pb = ["https://www.pghcitypaper.com/pittsburgh/EventSearch?v=d"]


website_url_music_pb = ["https://pittsburghopera.org/"]
website_url_museums_pb = ["https://carnegiemuseums.org/", "https://www.heinzhistorycenter.org/",
                          "https://www.thefrickpittsburgh.org/", "https://en.wikipedia.org/wiki/List_of_museums_in_Pittsburgh"]
website_url_food_pb = ["https://www.visitpittsburgh.com/events-festivals/food-festivals/", "https://www.picklesburgh.com/",
                       "https://www.pghtacofest.com/", "https://pittsburghrestaurantweek.com/", "https://littleitalydays.com/",
                       "https://bananasplitfest.com/"]


website_url_sports_pb = ["https://www.visitpittsburgh.com/things-to-do/pittsburgh-sports-teams/", "https://www.steelers.com/", "https://www.nhl.com/penguins/"]


website_url_info_history_cmu = ["https://www.cmu.edu/about/"]



def craw_text_data_normal(website_url):
    response = requests.get(website_url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    paragraphs = soup.find_all("p")
    text_list = [p.get_text(strip=True) for p in paragraphs]

    # Nối các đoạn văn bản, làm sạch khoảng trắng thừa
    text = " ".join(text_list)

    # các dấu ký tự như \t, \n bị lặp nhiều lần ở đầu mỗi chuỗi (\s+) sẽ được thay thế bằng 1 dấu cách (" ")
    text = re.sub(r"\s+", " ", text).strip()

    # các chuỗi có dạng "[số]" cũng cần được loại bỏ
    text = re.sub(r"\[\d+\]", "", text)
    
    return text

def craw_special_text_data(website_url):
    response = requests.get(website_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    event_paragraphs = []

    for h1 in soup.find_all("h1"):
        a_tag = h1.find("a", href=True)
        if not a_tag or "/events/event/" not in a_tag["href"]:
            continue

        title = a_tag.get_text(strip=True)
        link = a_tag["href"]

        parent_div = h1.find_parent("div", class_="copyContent")
        if not parent_div:
            continue

        date_div = parent_div.find("div", class_="eventdate")
        datetime = date_div.get_text(strip=True) if date_div else ""

        description = ""
        if date_div and date_div.next_sibling:
            sibling = date_div.next_sibling
            while sibling and isinstance(sibling, str) and sibling.strip() == "":
                sibling = sibling.next_sibling
            if sibling and isinstance(sibling, str):
                description = sibling.strip()

        read_more_link = ""
        read_more = parent_div.find("a", class_="button green right")
        if read_more:
            read_more_link = read_more["href"]

        start_date = ""
        location = ""
        event_url = ""
        json_script = parent_div.find_next("script", type="application/ld+json")
        if json_script:
            try:
                data = json.loads(json_script.string)
                start_date = data.get("startDate", "")
                location = data.get("location", {}).get("address", "")
                event_url = data.get("url", "")
            except json.JSONDecodeError:
                pass

        paragraph = f"""
Event: {title}
Time: {datetime or start_date}
Location: {location if location else 'Unknown'}
Description: {description}
More info: {event_url if event_url else link}
""".strip()
        paragraph = re.sub(r"\t+", " ", paragraph).strip()
        paragraph = re.sub(r"\n+", ";", paragraph).strip()
        event_paragraphs.append(paragraph)

        all_even = "\n\n".join(event_paragraphs)
    return all_even

def get_table_web(soup):
    # Tìm bảng đầu tiên có class wikitable
    table = soup.find("table", {"class": "wikitable sortable"})

    # Trích xuất hàng
    rows = table.find_all("tr")

    # Parse dữ liệu
    data = []
    for row in rows[1:]:  # Bỏ header
        cols = row.find_all("td")
        if len(cols) == 4:
            name = cols[0].get_text(strip=True)
            neighborhood = cols[1].get_text(strip=True)
            typ = cols[2].get_text(strip=True)
            summary = cols[3].get_text(strip=True)
            data.append(f"Name: {name}, Neighborhood: {neighborhood}, Type: {typ}, Summary: {summary}")
    text = ".".join(data)
    return text

def craw_table_text_data(website_url):
    response = requests.get(website_url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    paragraphs = soup.find_all("p")

    text_list = [p.get_text(strip=True) for p in paragraphs]

    # Nối các đoạn văn bản, làm sạch khoảng trắng thừa
    text = " ".join(text_list)

    # các dấu ký tự như \t, \n bị lặp nhiều lần ở đầu mỗi chuỗi (\s+) sẽ được thay thế bằng 1 dấu cách (" ")
    text = re.sub(r"\s+", " ", text).strip()

    # các chuỗi có dạng "[số]" cũng cần được loại bỏ
    text = re.sub(r"\[\d+\]", "", text)

    table_data = get_table_web(soup)

    text = [text, table_data]

    
    return "\n\n".join(text)

def craw_meta_content_data(website_url):
    response = requests.get(website_url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    ui_keywords = [
        "viewport", "robots", "theme-color", "charset", "generator",
        "referrer", "google", "apple", "facebook", "twitter","msapplication", "http-equiv",
        "format-detection", "image", "og:type"
    ]

    metas = soup.find_all("meta", attrs={"content": True})
    text_list = []

    for meta in metas:
        meta_name = (meta.get("name") or meta.get("property") or meta.get("http-equiv") or "").lower()

        if any(keyword in meta_name for keyword in ui_keywords):
            continue

        text_list.append(meta["content"])

    text = " ".join(text_list)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\[\d+\]", "", text)

    return text

def get_pdf_data_from_web(website_url):
    url = website_url
    filename = "2024_operating_budget.pdf"
    response = requests.get(url, verify=False)
    with open(filename, "wb") as f:
        f.write(response.content)

def craw_text_from_pdf(website_url, folder_data_dir):
    get_pdf_data_from_web(website_url)
    loader = DirectoryLoader(path = folder_data_dir, glob="*.pdf", loader_cls = PyPDFLoader)
    documents = loader.load()
    documents = [doc.model_dump()["page_content"] for doc in documents]
    return "\n".join(documents)


def general_info_history_synthesis(website_url_info_history_pb,
                               pdf_url_info_history_pb,
                               website_url_info_history_cmu, split_size_pdf = 50):
    general_info_history = []

    for url in website_url_info_history_pb:
        text = craw_text_data_normal(url) + "\n"
        dict_info =  {
            "content":text,
            "sumary": "general info and history",
            "name": "general info and history of Pittsburgh",
            "url": url,
            "created_on": "2025-05-13",
            "updated_at": "2025-05-13",
            "category": "general info and history",
            "_run_ml_inference": True,
            "rolePermissions": []
        }
        general_info_history.append(dict_info)
    
    for url in website_url_info_history_cmu:
        text = craw_text_data_normal(url) + "\n"
        dict_info =  {
            "content":text,
            "sumary": "general info and history",
            "name": "general info and history of CMU",
            "url": url,
            "created_on": "2025-05-13",
            "updated_at": "2025-05-13",
            "category": "general info and history",
            "_run_ml_inference": True,
            "rolePermissions": []
        }
        general_info_history.append(dict_info)
    
    for url in pdf_url_info_history_pb:
        text = craw_text_from_pdf(url, "") + "\n"
        text_per_split = len(text)//split_size_pdf
        for i in range(split_size_pdf):
            dict_info =  {
                "content":text[i*text_per_split:(i + 1)*text_per_split],
                "sumary": "general info and history",
                "name": "general info and history of Pittsburgh",
                "url": url,
                "created_on": "2025-05-13",
                "updated_at": "2025-05-13",
                "category": "general info and history",
                "_run_ml_inference": True,
                "rolePermissions": []
            }
            general_info_history.append(dict_info)
    
    return general_info_history

def event_synthesis(special_website_url_event_pb,
                    website_url_event_pb):
    events = []

    for url in special_website_url_event_pb:
        text = craw_special_text_data(url) + "\n"
        dict_info =  {
            "content":text,
            "sumary": "events of Pittsburgh",
            "name": "events of Pittsburgh",
            "url": url,
            "created_on": "2025-05-13",
            "updated_at": "2025-05-13",
            "category": "events",
            "_run_ml_inference": True,
            "rolePermissions": []
        }
        events.append(dict_info)
    
    for url in website_url_event_pb:
        text = craw_text_data_normal(url) + "\n"
        dict_info =  {
            "content":text,
            "sumary": "events of Pittsburgh",
            "name": "events of Pittsburgh",
            "url": url,
            "created_on": "2025-05-13",
            "updated_at": "2025-05-13",
            "category": "events",
            "_run_ml_inference": True,
            "rolePermissions": []
        }
        events.append(dict_info)
    
    return events

def music_culture_synthesis(website_url_music_pb,
                            website_url_museums_pb,
                            website_url_food_pb):
    music = []
    museums = []
    food = []

    for url in website_url_music_pb:
        text = craw_text_data_normal(url) + "\n"
        dict_info =  {
            "content":text,
            "sumary": "music",
            "name": "music",
            "url": url,
            "created_on": "2025-05-13",
            "updated_at": "2025-05-13",
            "category": "music",
            "_run_ml_inference": True,
            "rolePermissions": []
        }
        music.append(dict_info)

    for i in range(len(website_url_museums_pb)-1):
        text = craw_text_data_normal(website_url_museums_pb[i]) + "\n"
        dict_info =  {
            "content":text,
            "sumary": "museums",
            "name": "museums",
            "url": website_url_museums_pb[i],
            "created_on": "2025-05-13",
            "updated_at": "2025-05-13",
            "category": "museums",
            "_run_ml_inference": True,
            "rolePermissions": []
        }
        museums.append(dict_info)
    add = craw_table_text_data(website_url_museums_pb[-1]) + "\n"
    dict_info =  {
            "content":add,
            "sumary": "museums",
            "name": "museums",
            "url": website_url_museums_pb[-1],
            "created_on": "2025-05-13",
            "updated_at": "2025-05-13",
            "category": "museums",
            "_run_ml_inference": True,
            "rolePermissions": []
        }
    museums.append(dict_info)

    for i in range(len(website_url_food_pb)):
        if i == 1 or i == 2 or i == 3:
            text = craw_meta_content_data(website_url_food_pb[i]) + "\n"
            dict_info =  {
                "content":text,
                "sumary": "food",
                "name": "food",
                "url": website_url_food_pb[i],
                "created_on": "2025-05-13",
                "updated_at": "2025-05-13",
                "category": "food",
                "_run_ml_inference": True,
                "rolePermissions": []
            }
            food.append(dict_info)
        else:
            text = craw_text_data_normal(website_url_food_pb[i]) + "\n"
            dict_info =  {
                "content":text,
                "sumary": "food",
                "name": "food",
                "url": website_url_food_pb[i],
                "created_on": "2025-05-13",
                "updated_at": "2025-05-13",
                "category": "food",
                "_run_ml_inference": True,
                "rolePermissions": []
            }
            food.append(dict_info)
    return music + museums + food

def sport_synthesis(website_url_sports_pb):
    sport = []
    for url in website_url_sports_pb:
        text = craw_text_data_normal(url) + "\n"
        dict_info =  {
                "content":text,
                "sumary": "sport",
                "name": "sport",
                "url": url,
                "created_on": "2025-05-13",
                "updated_at": "2025-05-13",
                "category": "sport",
                "_run_ml_inference": True,
                "rolePermissions": []
        }
        sport.append(dict_info)
    return sport

def create_data(website_url_info_history_pb, pdf_url_info_history_pb,
              special_website_url_event_pb, website_url_event_pb, website_url_music_pb,
              website_url_museums_pb, website_url_food_pb, website_url_sports_pb, website_url_info_history_cmu):

    # general_info_history
    general_info_history_list = general_info_history_synthesis(website_url_info_history_pb,
                                                          pdf_url_info_history_pb,
                                                          website_url_info_history_cmu)
    # event in pb(Pittsburgh)
    event_pittsburgh = event_synthesis(special_website_url_event_pb, website_url_event_pb)

    music_culture = music_culture_synthesis(website_url_music_pb,
                                            website_url_museums_pb,
                                            website_url_food_pb)
    sport = sport_synthesis(website_url_sports_pb)

    data_list = general_info_history_list + event_pittsburgh + music_culture + sport
    # data_list = split_data(general_info_history_text, [], 50, [website_url_info_history_cmu,
    #                                                            website_url_info_history_pb,
    #                                                            pdf_url_info_history_pb])
    # data_list = split_data(event_pittsburgh, data_list, 3, [special_website_url_event_pb,
    #                                                         website_url_event_pb])
    # data_list = split_data(music_culture, data_list, 3, [website_url_music_pb,
    #                                                      website_url_museums_pb,
    #                                                      website_url_food_pb])
    # data_list = split_data(sport, data_list, 2, [website_url_sports_pb])

    file_path = "data.json"
    with open(file_path, "w") as f:
        json.dump(data_list,f, indent=4)

    return

def split_data(general_info_history_text, data_list, split_size, list_url):
    char_per_split = len(general_info_history_text)//split_size
    for i in range(split_size):
        split =  {
            "content":general_info_history_text[i*char_per_split: (i+1)*char_per_split],
            "sumary": "general info and history",
            "name": "general info and history",
            "url": list_url,
            "created_on": "2025-05-12",
            "updated_at": "2025-05-12",
            "category": "general info and history",
            "_run_ml_inference": True,
            "rolePermissions": []
        }
        data_list.append(split)
    return data_list

create_data(website_url_info_history_pb, pdf_url_info_history_pb,
            special_website_url_event_pb, website_url_event_pb,
            website_url_music_pb, website_url_museums_pb, website_url_food_pb,
            website_url_sports_pb, website_url_info_history_cmu)








