#!/usr/bin/env python3
import json

def normalize_city_name(city):
    """統一城市名稱"""
    city_mapping = {
        '臺北市': '台北市',
        '臺中市': '台中市', 
        '臺南市': '台南市',
        '臺東縣': '台東縣'
    }
    return city_mapping.get(city, city)

def fix_city_names():
    """修正城市名稱不一致問題"""
    print("載入停車場資料...")
    with open('parking_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("修正城市名稱...")
    
    # 修正所有資料的城市名稱
    for dataset_key in ['uspace_parking', 'external_parking', 'combined']:
        if dataset_key in data:
            for item in data[dataset_key]:
                original_city = item.get('city', '')
                normalized_city = normalize_city_name(original_city)
                if original_city != normalized_city:
                    print(f"修正: {original_city} -> {normalized_city}")
                    item['city'] = normalized_city
    
    # 重新計算統計資訊
    uspace_count = len(data['uspace_parking'])
    external_count = len(data['external_parking'])
    total_count = len(data['combined'])
    
    data['statistics'] = {
        'uspace_count': uspace_count,
        'external_count': external_count,
        'total_count': total_count
    }
    
    # 儲存修正後的資料
    with open('parking_data_fixed.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("修正完成！已儲存為 parking_data_fixed.json")
    
    # 顯示修正後的統計
    city_count = {}
    source_city_count = {'uspace': {}, 'external': {}}
    
    for item in data['combined']:
        city = item['city']
        source = item['source']
        
        city_count[city] = city_count.get(city, 0) + 1
        source_city_count[source][city] = source_city_count[source].get(city, 0) + 1
    
    print('\n修正後的城市統計:')
    for city, count in sorted(city_count.items()):
        uspace_cnt = source_city_count['uspace'].get(city, 0)
        external_cnt = source_city_count['external'].get(city, 0)
        print(f'  {city}: 總計{count} (USpace: {uspace_cnt}, 外部: {external_cnt})')

if __name__ == "__main__":
    fix_city_names()