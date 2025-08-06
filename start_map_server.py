#!/usr/bin/env python3
import http.server
import socketserver
import os

# 切換到當前目錄
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 添加 CORS 標頭
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"伺服器已啟動於 http://localhost:{PORT}")
    print(f"請在瀏覽器中開啟 http://localhost:{PORT}/parking_map.html")
    print("按 Ctrl+C 停止伺服器")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n伺服器已停止")