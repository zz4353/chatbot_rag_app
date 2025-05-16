from bs4 import BeautifulSoup
import requests
import json
from fake_useragent import UserAgent
ua = UserAgent()

def get_table_web(table):
    # Trích xuất hàng
    rows = table.find_all("tr")
    # Parse dữ liệu
    data = []
    if len(rows) == 0:
        return ""
    first_cols = rows[0].find_all("td")
    number_of_col = len(first_cols)
    name_of_col = []
    # lấy tên các cột từ dòng đầu tiên của bảng
    for i in range(number_of_col):
        text = first_cols[i].get_text(strip=True)
        if len(text) > 0:
            name_of_col.append(text)
        else:
            name_of_col.append("---")
    # lấy các dòng tiếp theo
    for row in rows[1:]:  # Bỏ qua dòng đầu tiên
        cols = row.find_all("td")
        if len(cols) != len(name_of_col):
            continue
        if len(cols) == 0:
            continue
        data_row = ""
        for i in range(number_of_col):
            data_row += str(name_of_col[i]) + ": " + str(cols[i].get_text(strip=True)) + ", "
        data_row = data_row[:-2] # Dữ liệu của 1 dòng trong bảng, bỏ 2 ký tự khoảng trắng và dấu `.` cuối đi
        data.append(data_row)

    text = ". ".join(data)
    return text

def craw_text_data(website_url):
    headers = {
        "User-Agent": ua.random
    }
    try:
        response = requests.get(website_url, headers=headers, verify=False)
    except:
        return "", []
    if response.status_code != 200:
        return "", []
    html_content = response.content
    soup = BeautifulSoup(html_content.decode('utf-8','ignore'))
    paragraphs = soup.find_all("p")
    text_list = [p.get_text(strip=True) for p in paragraphs]
    text = ".".join(text_list)
    all_table = soup.find_all("table")
    text_tables = []
    for table in all_table:
        text_tables.append(get_table_web(table))
    text_tables = ". ".join(text_tables)
            
    if "?" in website_url:
        return text + text_tables[:-1] + "\n", []
    urls_ref = soup.find_all("a", href=True)
    infomation_ref = []
    for url in urls_ref:
        sub_url = url["href"]
        if len(sub_url) == 0:
            continue
        if sub_url[:4] != "http":
            if sub_url[0] == "/":
                sub_url = sub_url[6:]
            sub_url = website_url + sub_url
        
        infomation_ref.append((url.get_text(strip=True), sub_url))
    return text + text_tables[:-1] + "\n", infomation_ref

def crawl_data(main_website, queue_url, history_pair_url, save_folder = "data_json/"):
    set_url = set([pair[1] for pair in queue_url])
    history_pair_url.append(queue_url.pop(0))
    text_init, infomation_ref = craw_text_data(main_website)
    init_info =  {
        "content":text_init,
        "sumary": "ĐẠI HỌC QUỐC GIA HÀ NỘI - VIETNAM NATIONAL UNIVERSITY, HANOI",
        "name": "ĐẠI HỌC QUỐC GIA HÀ NỘI - VIETNAM NATIONAL UNIVERSITY, HANOI",
        "url": main_website,
        "created_on": "2025-05-15",
        "updated_at": "2025-05-15",
        "category": "ĐẠI HỌC QUỐC GIA HÀ NỘI - VIETNAM NATIONAL UNIVERSITY, HANOI",
        "_run_ml_inference": True,
        "rolePermissions": []
    }

    file_path = save_folder+"data0.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(init_info, f, indent=4, ensure_ascii=False)
    queue_url = []
    for pair in infomation_ref:
        if pair[1] in set_url:
            continue
        queue_url.append(pair)
        set_url.add(pair[1])
    index = 53
    while(len(queue_url) > 0): 
        pair_url = queue_url.pop(0)
        history_pair_url.append(pair_url)
        text, infomation_ref = craw_text_data(pair_url[1])
        if text == "":
            continue
        index += 1
        init_info =  {
            "content":text,
            "sumary": pair_url[0],
            "name": pair_url[0],
            "url": pair_url[1],
            "created_on": "2025-05-15",
            "updated_at": "2025-05-15",
            "category": pair_url[0],
            "_run_ml_inference": True,
            "rolePermissions": []
        }
        file_path = save_folder+f"data{index}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(init_info, f, indent=4, ensure_ascii=False)
        for pair in infomation_ref:
            if pair[1] in set_url:
                continue
            queue_url.append(pair)
            set_url.add(pair[1])


queue_url = [("ĐẠI HỌC QUỐC GIA HÀ NỘI - VIETNAM NATIONAL UNIVERSITY, HANOI", "https://vnu.edu.vn/home/")]
history_pair_url = []
main_website = "https://vnu.edu.vn/home/"