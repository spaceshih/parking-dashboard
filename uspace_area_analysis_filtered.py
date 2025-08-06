#!/usr/bin/env python3
import json
import csv
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """計算兩點間的距離（公里）"""
    R = 6371  # 地球半径（公里）
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon/2) * math.sin(delta_lon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def analyze_uspace_areas():
    """分析每個USpace停車場周邊3公里內的外部停車場（僅包含有臨停服務的）"""
    
    print("載入停車場資料...")
    with open('parking_data_fixed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    uspace_parking = data['uspace_parking']
    external_parking = data['external_parking']
    
    # 過濾掉純月租制停車場（日間費率為0的）
    external_with_hourly = []
    for parking in external_parking:
        day_rate = parking.get('day_rate', 0)
        night_rate = parking.get('night_rate', 0)
        
        # 只保留有日間或夜間臨停費率的停車場
        if day_rate > 0 or night_rate > 0:
            # 計算日間最高金額（日間和夜間取較高者）
            max_rate = max(day_rate or 0, night_rate or 0)
            parking['max_hourly_rate'] = max_rate
            external_with_hourly.append(parking)
    
    print(f"USpace停車場數量: {len(uspace_parking)}")
    print(f"原始外部停車場數量: {len(external_parking)}")
    print(f"有臨停服務的外部停車場數量: {len(external_with_hourly)}")
    print(f"過濾掉純月租制停車場: {len(external_parking) - len(external_with_hourly)}個")
    
    results = []
    
    for i, uspace in enumerate(uspace_parking):
        if i % 50 == 0:
            print(f"處理進度: {i}/{len(uspace_parking)}")
        
        uspace_lat = uspace['lat']
        uspace_lon = uspace['lon']
        uspace_name = uspace['name']
        uspace_city = uspace['city']
        uspace_district = uspace['district']
        uspace_address = uspace['address']
        uspace_day_rate = uspace['day_rate']
        uspace_night_rate = uspace['night_rate']
        uspace_space_number = uspace['space_number']
        uspace_max_rate = max(uspace_day_rate or 0, uspace_night_rate or 0)
        
        # 找出3公里內的外部停車場（僅限有臨停服務的）
        nearby_external = []
        
        for external in external_with_hourly:
            try:
                external_lat = external['lat']
                external_lon = external['lon']
                
                # 計算距離
                distance = calculate_distance(uspace_lat, uspace_lon, external_lat, external_lon)
                
                if distance <= 3.0:  # 3公里內
                    nearby_external.append({
                        'name': external['name'],
                        'distance': distance,
                        'day_rate': external['day_rate'],
                        'night_rate': external['night_rate'],
                        'max_hourly_rate': external['max_hourly_rate'],
                        'monthly_rate': external['monthly_rate'],
                        'space_number': external['space_number']
                    })
            except (ValueError, TypeError):
                continue
        
        # 計算統計資料
        total_external_count = len(nearby_external)
        
        if total_external_count > 0:
            # 總車格數
            total_spaces = sum(ext['space_number'] for ext in nearby_external if ext['space_number'] and ext['space_number'] > 0)
            
            # 平均日間最高費率
            max_rates = [ext['max_hourly_rate'] for ext in nearby_external if ext['max_hourly_rate'] and ext['max_hourly_rate'] > 0]
            avg_max_rate = sum(max_rates) / len(max_rates) if max_rates else 0
            
            # 平均日間費率
            day_rates = [ext['day_rate'] for ext in nearby_external if ext['day_rate'] and ext['day_rate'] > 0]
            avg_day_rate = sum(day_rates) / len(day_rates) if day_rates else 0
            
            # 平均夜間費率
            night_rates = [ext['night_rate'] for ext in nearby_external if ext['night_rate'] and ext['night_rate'] > 0]
            avg_night_rate = sum(night_rates) / len(night_rates) if night_rates else 0
            
            # 平均月租金額
            monthly_rates = [ext['monthly_rate'] for ext in nearby_external if ext['monthly_rate'] and ext['monthly_rate'] > 0]
            avg_monthly_rate = sum(monthly_rates) / len(monthly_rates) if monthly_rates else 0
            
            # 最近距離
            min_distance = min(ext['distance'] for ext in nearby_external)
            
            # 最遠距離
            max_distance = max(ext['distance'] for ext in nearby_external)
            
        else:
            total_spaces = 0
            avg_max_rate = 0
            avg_day_rate = 0
            avg_night_rate = 0
            avg_monthly_rate = 0
            min_distance = 0
            max_distance = 0
        
        # 價格比較（使用最高費率比較）
        uspace_vs_external_max = 0
        uspace_vs_external_day = 0
        
        if avg_max_rate > 0 and uspace_max_rate > 0:
            uspace_vs_external_max = ((uspace_max_rate - avg_max_rate) / avg_max_rate) * 100
        
        if avg_day_rate > 0 and uspace_day_rate > 0:
            uspace_vs_external_day = ((uspace_day_rate - avg_day_rate) / avg_day_rate) * 100
        
        # 計算周邊停車場價格區間分布（使用最高費率）
        price_ranges = {
            '0-30元': 0,
            '31-50元': 0,
            '51-80元': 0,
            '81-120元': 0,
            '121-200元': 0,
            '200元以上': 0
        }
        
        for ext in nearby_external:
            max_rate = ext['max_hourly_rate']
            if max_rate <= 30:
                price_ranges['0-30元'] += 1
            elif max_rate <= 50:
                price_ranges['31-50元'] += 1
            elif max_rate <= 80:
                price_ranges['51-80元'] += 1
            elif max_rate <= 120:
                price_ranges['81-120元'] += 1
            elif max_rate <= 200:
                price_ranges['121-200元'] += 1
            else:
                price_ranges['200元以上'] += 1
        
        # 格式化價格區間字串
        price_range_summary = []
        for range_name, count in price_ranges.items():
            if count > 0:
                price_range_summary.append(f"{range_name}:{count}場")
        
        price_range_text = '; '.join(price_range_summary) if price_range_summary else '無資料'
        
        # 添加結果
        results.append({
            'uspace_id': uspace['id'],
            'uspace_name': uspace_name,
            'uspace_city': uspace_city,
            'uspace_district': uspace_district,
            'uspace_address': uspace_address,
            'uspace_lat': uspace_lat,
            'uspace_lon': uspace_lon,
            'uspace_space_number': uspace_space_number,
            'uspace_day_rate': uspace_day_rate,
            'uspace_night_rate': uspace_night_rate,
            'uspace_max_rate': uspace_max_rate,
            '周邊3km內有臨停服務停車場數量': total_external_count,
            '周邊外部停車場總車格數': total_spaces,
            '周邊平均日間最高費率': round(avg_max_rate, 2) if avg_max_rate > 0 else 0,
            '周邊平均日間臨停費率': round(avg_day_rate, 2) if avg_day_rate > 0 else 0,
            '周邊平均夜間臨停費率': round(avg_night_rate, 2) if avg_night_rate > 0 else 0,
            '周邊平均月租金額': round(avg_monthly_rate, 2) if avg_monthly_rate > 0 else 0,
            '周邊停車場價格區間分布_按最高費率': price_range_text,
            '最近外部停車場距離km': round(min_distance, 2) if min_distance > 0 else 0,
            '最遠外部停車場距離km': round(max_distance, 2) if max_distance > 0 else 0,
            'USpace最高費率vs周邊差異百分比': round(uspace_vs_external_max, 2),
            'USpace日間費率vs周邊差異百分比': round(uspace_vs_external_day, 2),
            '競爭密度_每平方公里外部停車場數': round(total_external_count / (3.14 * 3 * 3), 2),
            '周邊停車場詳細清單': '; '.join([f"{ext['name']}({ext['distance']:.2f}km,最高:{ext['max_hourly_rate']},日:{ext['day_rate']},夜:{ext['night_rate']},月:{ext['monthly_rate']})" for ext in nearby_external[:5]])
        })
    
    return results

def save_to_csv(results):
    """儲存結果到CSV檔案"""
    filename = 'uspace_area_analysis_filtered.csv'
    
    fieldnames = [
        'uspace_id', 'uspace_name', 'uspace_city', 'uspace_district', 'uspace_address',
        'uspace_lat', 'uspace_lon', 'uspace_space_number', 'uspace_day_rate', 'uspace_night_rate', 'uspace_max_rate',
        '周邊3km內有臨停服務停車場數量', '周邊外部停車場總車格數', 
        '周邊平均日間最高費率', '周邊平均日間臨停費率', '周邊平均夜間臨停費率', '周邊平均月租金額',
        '周邊停車場價格區間分布_按最高費率',
        '最近外部停車場距離km', '最遠外部停車場距離km',
        'USpace最高費率vs周邊差異百分比', 'USpace日間費率vs周邊差異百分比',
        '競爭密度_每平方公里外部停車場數', '周邊停車場詳細清單'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"過濾後的分析結果已儲存到 {filename}")
    return filename

def generate_summary_stats(results):
    """生成統計摘要"""
    total_uspace = len(results)
    has_nearby_external = sum(1 for r in results if r['周邊3km內有臨停服務停車場數量'] > 0)
    no_nearby_external = total_uspace - has_nearby_external
    
    # 平均競爭密度
    avg_competition = sum(r['競爭密度_每平方公里外部停車場數'] for r in results) / total_uspace
    
    # 價格比較統計（基於最高費率）
    higher_max_rate = sum(1 for r in results if r['USpace最高費率vs周邊差異百分比'] > 0)
    lower_max_rate = sum(1 for r in results if r['USpace最高費率vs周邊差異百分比'] < 0)
    
    print(f"\n=== 過濾後分析摘要 ===")
    print(f"總USpace停車場數: {total_uspace}")
    print(f"周邊3km內有臨停服務停車場: {has_nearby_external} ({has_nearby_external/total_uspace*100:.1f}%)")
    print(f"周邊3km內無臨停服務停車場: {no_nearby_external} ({no_nearby_external/total_uspace*100:.1f}%)")
    print(f"平均競爭密度: {avg_competition:.2f} 停車場/平方公里")
    print(f"最高費率高於周邊: {higher_max_rate} ({higher_max_rate/total_uspace*100:.1f}%)")
    print(f"最高費率低於周邊: {lower_max_rate} ({lower_max_rate/total_uspace*100:.1f}%)")

def main():
    print("開始USpace停車場周邊分析（過濾純月租制停車場）...")
    
    # 執行分析
    results = analyze_uspace_areas()
    
    # 儲存CSV
    csv_filename = save_to_csv(results)
    
    # 生成統計摘要
    generate_summary_stats(results)
    
    print(f"\n過濾後分析完成！請查看 {csv_filename}")

if __name__ == "__main__":
    main()