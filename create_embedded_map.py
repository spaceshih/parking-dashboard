#!/usr/bin/env python3
import json

def create_embedded_map():
    # 讀取修正後的停車場資料
    with open('parking_data_fixed.json', 'r', encoding='utf-8') as f:
        parking_data = json.load(f)
    
    # 讀取HTML模板
    with open('parking_map.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 將資料嵌入HTML
    data_script = f"""
        // 嵌入的停車場資料
        const EMBEDDED_PARKING_DATA = {json.dumps(parking_data, ensure_ascii=False, indent=2)};
    """
    
    # 修改載入資料的函數
    new_load_function = """
        // 載入停車場資料（使用嵌入資料）
        async function loadParkingData() {
            try {
                console.log('載入嵌入的停車場資料...');
                
                parkingData = EMBEDDED_PARKING_DATA;
                console.log('解析後的資料結構:', Object.keys(parkingData));
                console.log('統計資訊:', parkingData.statistics);
                
                if (!parkingData.combined || parkingData.combined.length === 0) {
                    throw new Error('沒有找到合併的停車場資料');
                }
                
                filteredData = parkingData.combined;
                console.log('設定篩選資料，筆數:', filteredData.length);
                
                initializeFilters();
                displayMarkers();
                updateStatistics();
                
                document.getElementById('loading').style.display = 'none';
                
                console.log('資料載入完成！');
            } catch (error) {
                console.error('載入資料時發生錯誤:', error);
                document.getElementById('loading').innerHTML = 
                    `<p style="color: red;">載入資料失敗: ${error.message}</p>`;
            }
        }"""
    
    # 在JavaScript開始處插入資料
    html_content = html_content.replace(
        '<script>',
        f'<script>\n{data_script}'
    )
    
    # 替換載入函數
    old_function_start = '        // 載入停車場資料\n        async function loadParkingData() {'
    old_function_end = '        }'
    
    # 找到舊函數的位置
    start_pos = html_content.find(old_function_start)
    if start_pos != -1:
        # 找到對應的結束括號
        brace_count = 0
        pos = start_pos + len(old_function_start)
        while pos < len(html_content):
            if html_content[pos] == '{':
                brace_count += 1
            elif html_content[pos] == '}':
                if brace_count == 0:
                    end_pos = pos + 1
                    break
                brace_count -= 1
            pos += 1
        
        # 替換函數
        html_content = (html_content[:start_pos] + 
                       new_load_function + 
                       html_content[end_pos:])
    
    # 儲存新的HTML檔案
    with open('parking_map_embedded.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("已創建 parking_map_embedded.html")
    print("此版本將資料直接嵌入HTML，不需要額外載入JSON檔案")

if __name__ == "__main__":
    create_embedded_map()