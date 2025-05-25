import requests
import json
import glob
import os

api_gemini_key = os.getenv("API_KEY_GEMINI")

API_KEY_GEMINI = "AIzaSyCN9MfrGIcJfAMgPpn2RRTnP8AZcqA4Za0"
response = ""


url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY_GEMINI}"

headers = {
    "Content-Type": "application/json"
}
folder_json = "data_json/"
new_folder_json = "data_json/"
count = 0
for file_path in glob.glob(folder_json+"*.json"):
    with open(file_path, 'r', encoding="utf-8") as f:
        dict_data = json.load(f)
    infomation = dict_data.get("content")
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Làm sạch đoạn text sau, tuyệt đối không thêm hay bớt thông tin, chỉ trả về thông tin đã được làm sạch:\n\n" + infomation
                    }
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        clean_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        dict_data["content"] = clean_text
        with open(new_folder_json+ "data" + str(count) + ".json", 'w', encoding="utf-8") as f:
            json.dump(dict_data, f, indent=4, ensure_ascii=False)
    count += 1
