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
# 因為需要解讀json的資料
import json
from fastapi import FastAPI, Body, Request

# fastMCP
from fastmcp import FastMCP, Context

# 用來跨執行緒/非同步上下文傳遞 Token 的標準庫
from contextvars import ContextVar

# create token
import time
import uuid
import hashlib

# 資料庫連線設定
import os
from dotenv import load_dotenv
import mysql.connector

# 載入 .env 檔案中的環境變數
load_dotenv()

# 設定參數與資料庫連線，用 os.getenv() 來抓取機密資料
con = mysql.connector.connect(
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD"),
    host = os.getenv("DB_HOST"),
    database = os.getenv("DB_NAME")
) 
print("Database Ready")


# 宣告一個 ContextVar 用來在請求期間暫存 Token
auth_token_var: ContextVar[str | None] = ContextVar("auth_token", default=None)

# ==========================================
# MCP Task 2: 建立 FastMCP 伺服器 及 提供留言工具給 AI Agent 調用
# ==========================================

# 建立 MCP 伺服器
mcp = FastMCP("Testing Message Website")

# 這裡工具參數只要收 content，Token 透過 ContextVar 安全取得
@mcp.tool(name="Create_Message", description="Create a new message in Testing Message Website.")
def mcp_create_message(content: str) -> dict:
    
    # --- A. 從 ContextVar 取得 Token ---
    token = auth_token_var.get()
    
    if not token:
        return {"error": True}
    
    # --- B. 查詢資料庫 ---
    cursor = con.cursor()
    cursor.execute("SELECT id FROM member WHERE mcp_token=%s", [token])
    result = cursor.fetchone()
    if result is None: 
        return {"error": True} 
    member_id = result[0] 
    
    # --- C. 寫入留言 ---
    cursor.execute("INSERT INTO message (member_id, content) VALUES (%s, %s)", [member_id, content])
    con.commit()

    # --- D. 成功回傳 ---
    return {"ok": True}

# 產生 MCP ASGI 應用程式
mcp_app = mcp.http_app(path="/")

# ==========================================
# 建立主程式 FastAPI，並綁定 lifespan
# ==========================================
app = FastAPI(lifespan=mcp_app.lifespan)

# 攔截所有進來的請求，把 Authorization Header 抓出來存進 ContextVar
@app.middleware("http")
async def capture_auth_header(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    token_reset_token = auth_token_var.set(token)
    try:
        response = await call_next(request)
        return response
    finally:
        auth_token_var.reset(token_reset_token)

# 將 MCP 掛載到 /mcp 路徑
app.mount("/mcp", mcp_app)

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
# MCP Task 1: 產生金鑰 (​Create Token API)
# ==========================================
@app.put("/api/token")
def create_token(request: Request):
    # 1. 驗證登入狀態
    if request.session.get("member") is None:
        return {"error": True}      
    
    user_email = request.session["member"]["email"]

    # 2. 準備組合字串：信箱 + 當下時間戳記 + 隨機 UUID
    current_time = str(time.time())
    random_str = str(uuid.uuid4())
    raw_data = user_email + current_time + random_str

    # 3. 進行 SHA256 加密
    # 必須先將字串 encode() 轉成 byte 格式才能進行 hash
    # hexdigest() 是將加密後的二進位結果轉換成你看得懂的 16 進位字串 (也就是 64 個字元)
    token = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()

    # 4. 將 token 存入資料庫，並與使用者綁定    
    cursor = con.cursor()
    cursor.execute("UPDATE member SET mcp_token=%s WHERE email=%s", [token, user_email])
    con.commit()

    return {"ok": True, "token": token}
    
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
    cursor.execute(f"INSERT INTO message (member_id, content) VALUES(%s, %s)", [user_id, content])
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