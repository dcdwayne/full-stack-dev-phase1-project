from fastmcp import FastMCP
"""
fastmcp 就是 mcp 伺服器的開發套件，所以可以用來開發mcp伺服器 部屬上線與調用
ai agent 除了是LLM之外 還可以調用外部工具。所謂的調用，就是利用MCP通訊協定來跟外部MCP Server做互動
例子：使用者要定房 > ai agent 了解意念 > 調用定房網站的伺服器，開發的商業邏輯去定房 > 然後把定房結果傳給AI agent > AI agent 在用人話告訴使用者！
建立MCP server步驟：利用FastMCP套件開發 > 佈署到FastMCP Cloud > 利用MCP客戶端，測試
"""
app = FastMCP("My MCP Server")

# 在設計開發MCP伺服器時，腦袋應該思考的是我要提供怎樣的工具，給AI Agent調用

# 步驟一、MCP開發範例:提供一個加法工具給AI Agent調用
@app.tool
def add(n1: int, n2: int) -> int:  # 吃整數，回傳整數
    """加法運算(add two numbers)""" # 給AI Agent看的說明文件
    return n1 + n2

# 本地端測試指令：
# fastmcp run app.py:app --transport http --port 8000
# --transport http 透過網路的http協定來提供服務

# --如果沒有佈署上限，那就只能自己用--

# 步驟二、佈署上線，利用 FastMCP Cloud 部屬

# 1. 專案與雲端同步。在github上建立一個新的repo，並且把程式碼推上去
# 2. github專案與FastMCP Cloud連結，並建制雲端伺服器(MCP Server)。在 FastMCP Cloud 上建立一個新的專案，並且連結到你的github repo
# 3. 建立AI Agent與MCP Server的連結。首先設定 AI Agent的 MCP 伺服器管理 (Manage MCP servers)，加入設定 json 檔，設定完成後AI Agent即可認到MCP伺服器，並且可以調用你的加法工具。
# 4. 測試階段，利用 AI Agent 調用你的MCP伺服器，測試加法工具是否可以正常運作
