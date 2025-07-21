# 使用官方 Python 基底映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 安裝必要套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# 指定 PORT（Cloud Run 預設為 8080）
ENV PORT=8080

# 啟動主程式（請依你使用的主程式為主）
CMD ["python", "main.py"]
