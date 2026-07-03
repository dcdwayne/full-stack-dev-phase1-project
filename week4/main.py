import csv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# Form 用來接收表單資料
from fastapi import Form
# RedirectResponse 用來把使用者踢到別的網址
from fastapi.responses import RedirectResponse
from starlette.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
# 掛載 SessionMiddleware，secret_key 是用來加密 Cookie 的鑰匙，隨便設一串字串即可
app.add_middleware(SessionMiddleware, secret_key="wehelp-secret-key")


# 設定 Jinja2 樣板引擎要去哪個資料夾找 HTML 檔案
# 記得要在 week4 資料夾下建立一個名為 templates 的資料夾
templates = Jinja2Templates(directory="templates")

# ==========================================
# Task 1: 首頁 (Home Page)
# ==========================================
@app.get("/")
async def home_page(request: Request):
    # 統一使用 Jinja2 去 templates 資料夾裡面抓 index.html
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={}
    )

# ==========================================
# Task 2: 驗證端點 (Verification Endpoint)
# ==========================================
@app.post("/login")
async def login_verify(
    request: Request,
    email: str = Form(default=""), 
    password: str = Form(default="")
):
    # 檢查 1：如果信箱或密碼是空的
    # (因為前端送出空表單時，接收到的是空字串 "")
    if not email or not password:
        # 導向失敗頁面，並帶上 msg 參數 (記得用 303 轉為 GET 請求)
        return RedirectResponse(url="/ohoh?msg=請輸入信箱和密碼", status_code=303)
    
    # 檢查 2：比對指定的帳號與密碼
    if email == "abc@abc.com" and password == "abc":
        # ⭐ 新增這行：將使用者的狀態標記為已登入 (對應作業要求的 LOGGED-IN state)
        request.session["LOGGED_IN"] = True
        # 成功，導向會員頁
        return RedirectResponse(url="/member", status_code=303)
    
    # 檢查 3：如果不符合上述條件，就是帳號或密碼錯誤
    return RedirectResponse(url="/ohoh?msg=帳號或密碼輸入錯誤", status_code=303)


# ==========================================
# Task 2: 成功頁面 (Success Page)
# ==========================================
@app.get("/member")
async def member_page(request: Request):
    # ⭐ 檢查 Session 裡面有沒有 LOGGED_IN 的紀錄，並且值是不是 True
    if not request.session.get("LOGGED_IN", False):
        # 如果沒登入過，強制踢回首頁 (因為是 GET 到 GET，不用加 303 沒關係)
        return RedirectResponse(url="/")
    
    # 單純渲染 member.html 畫面
    return templates.TemplateResponse(
        request=request, 
        name="member.html", 
        context={}
    )


# ==========================================
# Task 2: 失敗頁面 (Error Page)
# ==========================================
@app.get("/ohoh")
async def error_page(request: Request, msg: str = "發生未知的錯誤"):
    # 參數 `msg` 會自動去抓取網址上的 Query String (例如 ?msg=帳號或密碼輸入錯誤)
    # 我們把抓到的 msg 放進 context 字典，傳給 Jinja2 渲染
    return templates.TemplateResponse(
        request=request, 
        name="ohoh.html", 
        context={"msg": msg}
    )


# ==========================================
# Task 3: 登出端點 (Logout Endpoint)
# ==========================================
@app.get("/logout")
async def logout(request: Request):
    # 將登入狀態設為 False (銷毀通行證)
    request.session["LOGGED_IN"] = False
    
    # 導向回首頁
    return RedirectResponse(url="/")


# ==========================================
# 資料載入區：啟動時將 CSV 讀入記憶體
# ==========================================
hotel_data = {}

# 假設你的 csv 欄位名稱是: id, name, en_name, phone
# 這裡使用 utf-8-sig 是為了避免 Windows Excel 產生的 BOM 亂碼
with open("hotels.csv", mode="r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    # 使用 enumerate 從 1 開始自動編號
    for index, row in enumerate(reader, start=1):
        hotel_id = str(index)
        # 順便把產生的 id 放進 row 裡面，方便前端畫面的渲染
        row["id"] = hotel_id 
        hotel_data[hotel_id] = row

# ==========================================
# Task 4: 取得旅館資訊 Endpoint
# ==========================================
@app.get("/hotels/{hotel_id}", response_class=HTMLResponse)
async def get_hotel_info(request: Request, hotel_id: str):
    # 從我們剛剛建立的字典中尋找對應的旅館
    hotel = hotel_data.get(hotel_id)
    
    # 準備要傳給 Jinja2 樣板的資料
    # 將 request 物件傳進去是 Jinja2 的硬性規定
    context = {
        "request": request,
        "hotel": hotel  # 如果找不到，hotel 的值會是 None
    }
    
    # 渲染 hotel.html 並回傳
    return templates.TemplateResponse(request, "hotel.html", context)

# ==========================================
# 網站圖示 (Favicon)
# ==========================================
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # 直接回傳 static 資料夾裡面的圖片
    return FileResponse("static/favicon.ico")

"""
# 最後掛載靜態資料夾 (注意這行要放最後，避免攔截了 API 路由)
app.mount("/", 
          StaticFiles(directory="static", html=True), name="static")
"""
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)