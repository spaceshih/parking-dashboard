import csv
import json
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """計算兩點間的距離（米）"""
    R = 6371000  # 地球半径（米）
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon/2) * math.sin(delta_lon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def load_csv_data(filename):
    """載入CSV資料"""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"找不到檔案: {filename}")
        return []
    return data

def clean_coordinate_data(data, lat_field='lat', lon_field='lon'):
    """清洗座標資料"""
    cleaned = []
    for row in data:
        try:
            lat = float(row.get(lat_field, 0))
            lon = float(row.get(lon_field, 0))
            
            # 檢查座標是否在台灣範圍內
            if 21.5 <= lat <= 25.5 and 119.5 <= lon <= 122.5:
                row[lat_field] = lat
                row[lon_field] = lon
                cleaned.append(row)
        except (ValueError, TypeError):
            continue
    
    return cleaned

def standardize_uspace_data(data):
    """標準化USpace資料"""
    standardized = []
    
    for row in data:
        try:
            # 計算平均日間費率
            day_rates = []
            for day in ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']:
                rate_field = f"{day}day_rate"
                if rate_field in row and row[rate_field]:
                    try:
                        rate = float(row[rate_field])
                        if rate > 0:
                            day_rates.append(rate)
                    except ValueError:
                        continue
            
            avg_day_rate = sum(day_rates) / len(day_rates) if day_rates else 0
            
            # 夜間費率
            night_rate = 0
            if '夜間費率' in row and row['夜間費率']:
                try:
                    night_rate = float(row['夜間費率'])
                except ValueError:
                    night_rate = 0
            
            # 車位數
            space_number = 0
            if 'space_number' in row and row['space_number']:
                try:
                    space_number = int(float(row['space_number']))
                except ValueError:
                    space_number = 0
            
            standardized.append({
                'id': row.get('id', ''),
                'name': row.get('name', ''),
                'lat': row['lat'],
                'lon': row['lon'],
                'city': row.get('city', ''),
                'district': row.get('zone', ''),
                'address': row.get('address', ''),
                'space_number': space_number,
                'day_rate': avg_day_rate,
                'night_rate': night_rate,
                'monthly_rate': 0,
                'source': 'uspace',
                'building_type': row.get('building_type', ''),
                'financial_class': row.get('financial_class', '')
            })
        except Exception as e:
            print(f"處理USpace資料時發生錯誤: {e}")
            continue
    
    return standardized

def standardize_external_data(data):
    """標準化外部停車場資料"""
    standardized = []
    
    for row in data:
        try:
            # 計算平均日間費率
            day_rates = []
            for field in ['weekday_day', 'weekend_day']:
                if field in row and row[field]:
                    try:
                        rate = float(row[field])
                        if rate > 0:
                            day_rates.append(rate)
                    except ValueError:
                        continue
            
            avg_day_rate = sum(day_rates) / len(day_rates) if day_rates else 0
            
            # 計算平均夜間費率
            night_rates = []
            for field in ['weekday_night', 'weekend_night']:
                if field in row and row[field]:
                    try:
                        rate = float(row[field])
                        if rate > 0:
                            night_rates.append(rate)
                    except ValueError:
                        continue
            
            avg_night_rate = sum(night_rates) / len(night_rates) if night_rates else 0
            
            # 月租費
            monthly_rate = 0
            if 'monthly_rate' in row and row['monthly_rate']:
                try:
                    monthly_rate = float(row['monthly_rate'])
                except ValueError:
                    monthly_rate = 0
            
            # 車位數
            space_number = 0
            if 'space_number' in row and row['space_number']:
                try:
                    space_number = int(float(row['space_number']))
                except ValueError:
                    space_number = 0
            
            standardized.append({
                'id': row.get('id', ''),
                'name': row.get('name', ''),
                'lat': row['lat'],
                'lon': row['lon'],
                'city': row.get('city', ''),
                'district': row.get('district', ''),
                'address': row.get('address_info', ''),
                'space_number': space_number,
                'day_rate': avg_day_rate,
                'night_rate': avg_night_rate,
                'monthly_rate': monthly_rate,
                'source': 'external',
                'building_type': '',
                'financial_class': ''
            })
        except Exception as e:
            print(f"處理外部資料時發生錯誤: {e}")
            continue
    
    return standardized

def remove_duplicates(uspace_data, external_data, distance_threshold=50):
    """移除重複的停車場"""
    duplicates = []
    
    print("檢查重複停車場...")
    for i, external in enumerate(external_data):
        external_lat, external_lon = external['lat'], external['lon']
        external_name = external['name'].lower()
        
        for uspace in uspace_data:
            uspace_lat, uspace_lon = uspace['lat'], uspace['lon']
            uspace_name = uspace['name'].lower()
            
            # 計算距離
            distance = calculate_distance(external_lat, external_lon, uspace_lat, uspace_lon)
            
            # 如果距離很近，檢查名稱相似性
            if distance < distance_threshold:
                # 簡單的名稱相似性檢查
                if (external_name in uspace_name or 
                    uspace_name in external_name or
                    any(word in external_name for word in uspace_name.split() if len(word) > 2)):
                    duplicates.append(i)
                    print(f"發現重複: {external['name']} <-> {uspace['name']} (距離: {distance:.1f}m)")
                    break
    
    # 移除重複項目
    external_deduped = [external_data[i] for i in range(len(external_data)) if i not in duplicates]
    
    print(f"移除 {len(duplicates)} 個重複停車場")
    print(f"外部停車場去重後數量: {len(external_deduped)}")
    
    return external_deduped

def main():
    print("開始處理停車場資料...")
    
    # 載入資料
    print("載入USpace停車場資料...")
    uspace_raw = load_csv_data('../建物commit/input/建物費率上限整合_最終版拷貝.csv')
    
    print("載入外部停車場資料...")
    external_raw = load_csv_data('../建物commit/input/外部停車場.csv')
    
    if not uspace_raw:
        print("無法載入USpace資料！")
        return
    
    if not external_raw:
        print("無法載入外部資料！")
        return
    
    print(f"USpace原始資料: {len(uspace_raw)} 筆")
    print(f"外部原始資料: {len(external_raw)} 筆")
    
    # 清洗座標資料
    uspace_clean = clean_coordinate_data(uspace_raw)
    external_clean = clean_coordinate_data(external_raw)
    
    print(f"USpace清洗後: {len(uspace_clean)} 筆")
    print(f"外部清洗後: {len(external_clean)} 筆")
    
    # 標準化資料
    uspace_std = standardize_uspace_data(uspace_clean)
    external_std = standardize_external_data(external_clean)
    
    # 移除重複
    external_deduped = remove_duplicates(uspace_std, external_std)
    
    # 合併資料
    combined_data = uspace_std + external_deduped
    
    # 儲存為JSON
    output_data = {
        'uspace_parking': uspace_std,
        'external_parking': external_deduped,
        'combined': combined_data,
        'statistics': {
            'uspace_count': len(uspace_std),
            'external_count': len(external_deduped),
            'total_count': len(combined_data)
        }
    }
    
    with open('parking_data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n資料處理完成！")
    print(f"USpace停車場: {len(uspace_std)} 筆")
    print(f"外部停車場: {len(external_deduped)} 筆")
    print(f"總計: {len(combined_data)} 筆")
    
    # 統計城市分布
    city_count = {}
    for item in combined_data:
        city = item['city']
        city_count[city] = city_count.get(city, 0) + 1
    
    print(f"\n城市分布:")
    for city, count in sorted(city_count.items()):
        print(f"  {city}: {count}")

if __name__ == "__main__":
    main()