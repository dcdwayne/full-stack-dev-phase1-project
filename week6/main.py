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
import json #因為需要解讀json的資料
from fastapi import FastAPI, Body, Request

# 準備資料庫連線(前製作業)
import os
from dotenv import load_dotenv
import mysql.connector

# 載入 .env 檔案中的環境變數
load_dotenv()

# 設定參數與資料庫連線，改用 os.getenv() 來抓取機密資料
con = mysql.connector.connect(
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD"),
    host = os.getenv("DB_HOST"),
    database = os.getenv("DB_NAME")
) 
print("Database Ready")

app = FastAPI()
# 掛載 SessionMiddleware，secret_key 是用來加密 Cookie 的鑰匙，隨便設一串字串即可
app.add_middleware(SessionMiddleware, secret_key="wehelp-secret-key")

# 設定 Jinja2 樣板引擎要去哪個資料夾找 HTML 檔案
# html 檔案都放在名為 "templates" 的資料夾中
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
# Task 1:會員頁面端點 (Member Page Endpoint)
# ==========================================
@app.get("/member")
def member_page(request: Request):
    # 1. 檢查 session 中是否有 member 的登入資訊
    if request.session.get("member") is None:
        # 如果沒有登入（未通過驗證），強制導向回首頁 
        return RedirectResponse(url="/", status_code=303)
    
    # 2. 如果有登入，把 session 裡面的名字取出來
    user_name = request.session["member"]["name"]
    
    # 3. 渲染 member.html，並把名字傳遞給前端的 {{ name }} 標籤
    return templates.TemplateResponse(
        request=request, 
        name="member.html", 
        context={"request": request, "name": user_name}
    )

# ==========================================
# Task 1: 失敗頁面 (Error Page)
# ==========================================
@app.get("/ohoh")
async def error_page(request: Request, msg: str = "自訂的錯誤訊息"):
    # 參數 `msg` 會自動去抓取網址上的 Query String (例如 ?msg=帳號、或密碼輸入錯誤)
    # 我們把抓到的 msg 放進 context 字典，傳給 Jinja2 渲染
    return templates.TemplateResponse(
        request=request, 
        name="ohoh.html", 
        context={"msg": msg}
    )

# ==========================================
# Task 2: 註冊端點 (​Signup Endpoint)
# ==========================================
# 註冊會員帳號的API
@app.post("/signup")
async def signup(body = Body(None)): 
    # body = json.loads(body) 
    name = body["name"]
    email = body["email"]
    password = body["password"]
    
    # 以下與資料庫互動
    # 首先檢查 email 是否重複
    cursor = con.cursor()
    cursor.execute("SELECT * FROM member WHERE email=%s", [email]) 
    result = cursor.fetchone() 
    
    if result == None: 
        # 代表 email 沒有重複，可以註冊
        cursor.execute("INSERT INTO member (name, email, password) VALUES(%s, %s, %s)", [name, email, password])
        con.commit()
        # 回傳 JSON 讓前端的 result.ok 變成 true
        return {"ok": True} 
    else: 
        # 回傳 JSON 讓前端的 result.ok 變成 undefined/false
        return {"ok": False}

# ==========================================
# Task 3: 登入端點 (Login Endpoint)
# ==========================================
#登入帳號的API
@app.post("/login")
def login(request:Request, body = Body(None)): # 這邊會用到使用者狀態管理
    # body = json.loads(body) 
    email = body["email"]
    password = body["password"]

    # 根據前端輸入的 email 和 password 從資料庫取得對應的帳戶資料
    cursor = con.cursor()
    cursor.execute("SELECT * FROM member WHERE email=%s AND password=%s", [email, password]) # SQL指令查詢
    result = cursor.fetchone() 

    if result == None: # 資料庫中沒有對應的資料，登入失敗
        request.session["member"] = None # session 紀錄 None 代表沒登入！
        return {"ok":False}
    else: # 資料庫中有對應的資料，登入成功
        request.session["member"] = {"id": result[0], "name": result[1], "email": result[2]} #這邊在把登入的身份紀錄到session內，讓系統知道當前使用者是否有登入。session 紀錄登入的身份 代表登入！
        return {"ok":True, "name":result[1], "email":result[2]} # 登入成功"}


# ==========================================
# Task 4: 登出端點 (Logout Endpoint)
# ==========================================
@app.get("/logout")
async def logout(request: Request):
    # 清除名為 "member" 的狀態
    request.session["member"] = None 
    # 或者更乾脆的 request.session.clear()
    return RedirectResponse(url="/")

# ==========================================
# Task 5: ​Create Message API
# ==========================================
# 新增留言的 API
@app.post("/api/message")
def create_message(request: Request, body=Body()):
    if request.session.get("member") is None:
        return {"error": True}
    # 預期前端透過 Resquest Body 傳遞 {"author":"姓名";"content":"內容"}
    # body = json.loads(body) # body的資料用json的模組解讀出來，變成字典。
    user_id = request.session["member"]["id"]
    content = body["content"]
    # 連線到資料庫，將資料新增資料表中
    cursor = con.cursor() # 建立cursor物件
    cursor.execute(f"INSERT INTO message (member_id, content) VALUES(%s, %s)", [request.session["member"]["id"], body["content"]])
    con.commit() # 執行！
    return {"ok":True} # 回報前端 運作順利！

# ==========================================
# Task 5: Get Messages API
# ==========================================
@app.get("/api/message")
def get_message(request: Request):
    if request.session.get("member") is None:
        return {"error": True}
    
    current_user_id = request.session["member"]["id"]
    cursor = con.cursor(dictionary=True)

    # 使用 JOIN 把兩張表接起來撈名字
    sql = """
        SELECT message.id, member.name, message.content, message.member_id 
        FROM message 
        INNER JOIN member ON message.member_id = member.id
    """
    cursor.execute(sql)
    messages = cursor.fetchall()

    data = []
    for msg in messages:
        # 判斷這則留言是不是當前登入者寫的
        is_self = True if msg["member_id"] == current_user_id else False
        data.append({
            "id": msg["id"],
            "name": msg["name"],
            "content": msg["content"],
            "self": is_self
        })

    return {"ok": True, "data": data}

# ==========================================
# Task 6: Delete Message API
# ==========================================
# 刪除留言的 API，刪除時，必須同時比對 id 與 member_id，確保只能刪除自己的留言。
@app.delete("/api/message/{id}")
def delete_message(request: Request, id: int):
    if request.session.get("member") is None:
        return {"error": True}

    member_id = request.session["member"]["id"]
    cursor = con.cursor()
    # 加上 AND member_id = %s，確保只有作者本人能刪除
    cursor.execute("DELETE FROM message WHERE id=%s AND member_id=%s", [id, member_id])
    con.commit()
    return {"ok": True}

# ==========================================
# 網站圖示 (Favicon)
# ==========================================
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # 直接回傳 static 資料夾裡面的圖片
    return FileResponse("static/favicon.ico")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

