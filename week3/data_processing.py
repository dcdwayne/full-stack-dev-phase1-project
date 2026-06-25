import urllib.request
import json
import csv
from bs4 import BeautifulSoup

# ==========================================
# Task 1: 旅館與行政區資料處理
# ==========================================

url_ch = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-ch"
url_en = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-en"

def fetch_json(url):
    # 使用內建 urllib 發送請求
    with urllib.request.urlopen(url) as response:
        raw_data = response.read().decode('utf-8')
        return json.loads(raw_data) # 解析為 Python 資料結構

# 抓取中文與英文資料
print("正在抓取中文與英文旅館資料...")
data_ch = fetch_json(url_ch)
data_en = fetch_json(url_en)

# 1. 建立英文資料的對照字典 (用 _id 當作唯一的 Key)
en_lookup = {}
for en_item in data_en["list"]:
    hotel_id = en_item.get("_id")
    en_lookup[hotel_id] = en_item

# 2. 遍歷「中文資料」，利用 _id 去對照表撈出對應的英文資料並合併
merged_hotels = []
for ch_item in data_ch["list"]:
    hotel_key = ch_item.get("_id")
    
    # 去對照表找英文資料，萬一找不到就給個空字典 {} 避免程式噴錯
    en_item = en_lookup.get(hotel_key, {})
    
    # 3. 填入真實的欄位名稱 (Key)
    merged_item = {
        "_id": ch_item.get("_id", ""),
        "_importdate": ch_item.get("_importdate", ""),
        '旅館類別': ch_item.get("旅館類別", ""),
        'legal accommodation' : en_item.get("legal accommodation", ""),
        '旅宿名稱': ch_item.get("旅宿名稱", ""),
        "hotel name": en_item.get("hotel name", ""),
        '地址': ch_item.get("地址", ""),
        "address" : en_item.get("address", ""),
        '電話或手機號碼': ch_item.get("電話或手機號碼", ""),
        "tel": en_item.get("tel", ""),
        '傳真': ch_item.get("傳真", ""),
        "fax": en_item.get("fax", ""),
        '房間數': ch_item.get("房間數", ""),
        'the total number of rooms': en_item.get("the total number of rooms", ""),
    }
    
    merged_hotels.append(merged_item)

# 1. 定義作業要求的 CSV 標頭
hotels_headers = ["Chinese Name", "English Name", "ChineseAddress", "EnglishAddress", "Phone", "RoomCount"]

# 2. 開啟 (或建立) hotels.csv 檔案準備寫入
# newline="" 是為了避免在 Windows 系統下寫入 CSV 時產生多餘的空白行
# encoding="utf-8" 確保中文不會變成亂碼
with open("hotels.csv", mode="w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    
    # 3. 先寫入第一行的標頭
    writer.writerow(hotels_headers)
    
    # 4. 遍歷 merged_hotels，把每一筆資料轉成列表 (List) 寫入
    for hotel in merged_hotels:
        # 根據真實 Key 抓取這 6 個欄位的值
        row_data = [
            hotel.get("旅宿名稱", ""),
            hotel.get("hotel name", ""),
            hotel.get("地址", ""),
            hotel.get("address", ""),
            hotel.get("電話或手機號碼", ""),
            hotel.get("房間數", "")
        ]
        
        # 將這筆旅館資料寫入 CSV 成為新的一行
        writer.writerow(row_data)

print("hotels.csv 輸出完成！")

# 1. 準備一個空字典，用來當作各區的統計信箱
district_stats = {}

# 2. 開始遍歷我們合併好的旅館名單
for hotel in merged_hotels:
    address = hotel.get("地址", "")
    
    # 【關鍵步驟】從地址中切出「行政區」
    # 尋找 "區" 這個字的索引位置
    district_end_idx = address.find("區") 
    if district_end_idx != -1:
        # 往前推 2 個字，加上 "區" 本身，剛好會切出 3 個字 (例如 "萬華區")
        district = address[district_end_idx - 2 : district_end_idx + 1]
    else:
        # 如果地址裡沒有 "區"，就跳過這筆或歸類為 "其他"
        continue 
        
    # 安全地處理房間數 (萬一遇到空字串 "" 或非數字，就當作 0)
    room_str = hotel.get("房間數", 0)
    try:
        room_count = int(room_str)
    except ValueError:
        room_count = 0

    # 【分組邏輯】如果這個行政區還沒被記錄過，就幫它初始化
    if district not in district_stats:
        district_stats[district] = {
            "HotelCount": 0,
            "RoomCount": 0
        }
    
    # 3. 開始累加 (相當於 Pandas 的 .count() 和 .sum())
    district_stats[district]["HotelCount"] += 1
    district_stats[district]["RoomCount"] += room_count

# 4. 將統計結果輸出成 districts.csv
# 題目要求的標頭
districts_headers = ["DistrictName", "HotelCount", "RoomCount"]

with open("districts.csv", mode="w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(districts_headers)
    
    # 遍歷我們統計好的字典 (dict.items() 會同時抓出 Key 和 Value)
    for dist_name, stats in district_stats.items():
        row_data = [
            dist_name,
            stats["HotelCount"],
            stats["RoomCount"]
        ]
        writer.writerow(row_data)

print("districts.csv 輸出完成！")


# ==========================================
# Task 2: PTT Steam 看板文章爬蟲
# ==========================================

# 基礎設定
base_url = "https://www.ptt.cc"
current_url = base_url + "/bbs/Steam/index.html"
headers = {
    # 偽裝成一般的瀏覽器，避免被 PTT 伺服器拒絕
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# 準備要寫入的 CSV 檔案
with open("articles.csv", mode="w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    # 寫入標頭
    writer.writerow(["Article Title", "LikeCount", "Publish Time"])

    # 迴圈執行 3 次，代表抓取 3 頁 (目前最新頁 + 往前推 2 頁)
    for page in range(3):
        print(f"正在抓取第 {page + 1} 頁: {current_url}")
        
        # 1. 請求「列表頁」
        req = urllib.request.Request(current_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 找出該頁所有的文章區塊
        articles = soup.find_all("div", class_="r-ent")
        
        for article in articles:
            # 取得標題與 a 標籤
            title_div = article.find("div", class_="title")
            a_tag = title_div.find("a")
            
            # 【防呆機制】如果沒有 <a> 標籤，代表文章已經被刪除，題目規定要跳過
            if not a_tag:
                continue
                
            title = a_tag.text.strip()
            article_link = base_url + a_tag["href"] # 組裝出內頁的完整網址
            
            # 取得推文數
            nrec_div = article.find("div", class_="nrec")
            # 如果沒有推文數，預設給 0
            like_count = nrec_div.text.strip() if nrec_div and nrec_div.text.strip() else "0"
            
            # 2. 進入「文章內頁」抓取時間
            publish_time = ""
            try:
                inner_req = urllib.request.Request(article_link, headers=headers)
                with urllib.request.urlopen(inner_req) as inner_res:
                    inner_html = inner_res.read().decode('utf-8')
                    inner_soup = BeautifulSoup(inner_html, 'html.parser')
                    
                    # 尋找所有的 metadata 區塊
                    metalines = inner_soup.find_all("div", class_="article-metaline")
                    for meta in metalines:
                        tag = meta.find("span", class_="article-meta-tag")
                        # 確定這個標籤是標示「時間」的
                        if tag and tag.text.strip() == "時間":
                            value_span = meta.find("span", class_="article-meta-value")
                            if value_span:
                                raw_time = value_span.text.strip()
                                # 確保時間格式為 EEE MMM DD HH:MM:SS YYYY (例如 "Tue Jun  9 ..." 轉成 "Tue Jun 09 ...")
                                parts = raw_time.split()
                                if len(parts) == 5:
                                    parts[2] = parts[2].zfill(2)  # 將日（DD）補零至兩位數
                                    publish_time = " ".join(parts)
                                else:
                                    publish_time = raw_time
                            break # 找到了就不用繼續找其他 meta 了
            except Exception as e:
                print(f"抓取內頁 {article_link} 失敗: {e}")
            
            # 3. 將這篇文章的資訊寫入 CSV
            writer.writerow([title, like_count, publish_time])
            
        # 4. 尋找「‹ 上頁」的連結，準備進入下一次迴圈
        paging_div = soup.find("div", class_="btn-group btn-group-paging")
        # 找到包含所有分頁按鈕的 a 標籤，通常第 2 個 (索引值 1) 就是上一頁
        prev_link = paging_div.find_all("a")[1]
        
        if "href" in prev_link.attrs:
            # 更新 current_url 為上一頁的網址
            current_url = base_url + prev_link["href"]
        else:
            # 如果沒有 href (例如已經到了 PTT 最古早的第一頁)，就提早結束
            break

print("articles.csv 輸出完成！")
