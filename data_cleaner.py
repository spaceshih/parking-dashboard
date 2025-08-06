import pandas as pd
import numpy as np
from geopy.distance import geodesic
import json

def load_and_clean_data():
    """載入並清洗USpace和外部停車場資料"""
    
    # 載入USpace停車場資料
    print("載入USpace停車場資料...")
    uspace_df = pd.read_csv('../建物commit/input/建物費率上限整合_最終版拷貝.csv')
    
    # 載入外部停車場資料
    print("載入外部停車場資料...")
    external_df = pd.read_csv('../建物commit/input/外部停車場.csv')
    
    print(f"USpace停車場數量: {len(uspace_df)}")
    print(f"外部停車場數量: {len(external_df)}")
    
    # 清洗USpace資料
    uspace_cleaned = clean_uspace_data(uspace_df)
    
    # 清洗外部資料
    external_cleaned = clean_external_data(external_df)
    
    # 移除重複的USpace停車場（可能出現在外部資料中）
    external_deduped = remove_duplicates(uspace_cleaned, external_cleaned)
    
    # 統一資料格式
    uspace_standardized = standardize_uspace_data(uspace_cleaned)
    external_standardized = standardize_external_data(external_deduped)
    
    return uspace_standardized, external_standardized

def clean_uspace_data(df):
    """清洗USpace資料"""
    # 移除沒有經緯度的資料
    df_clean = df.dropna(subset=['lat', 'lon'])
    
    # 移除經緯度為0的資料
    df_clean = df_clean[(df_clean['lat'] != 0) & (df_clean['lon'] != 0)]
    
    # 確保經緯度在合理範圍內（台灣地區）
    df_clean = df_clean[
        (df_clean['lat'] >= 21.5) & (df_clean['lat'] <= 25.5) &
        (df_clean['lon'] >= 119.5) & (df_clean['lon'] <= 122.5)
    ]
    
    print(f"USpace清洗後數量: {len(df_clean)}")
    return df_clean

def clean_external_data(df):
    """清洗外部停車場資料"""
    # 移除沒有經緯度的資料
    df_clean = df.dropna(subset=['lat', 'lon'])
    
    # 移除經緯度為0的資料
    df_clean = df_clean[(df_clean['lat'] != 0) & (df_clean['lon'] != 0)]
    
    # 確保經緯度在合理範圍內（台灣地區）
    df_clean = df_clean[
        (df_clean['lat'] >= 21.5) & (df_clean['lat'] <= 25.5) &
        (df_clean['lon'] >= 119.5) & (df_clean['lon'] <= 122.5)
    ]
    
    print(f"外部停車場清洗後數量: {len(df_clean)}")
    return df_clean

def remove_duplicates(uspace_df, external_df, distance_threshold=50):
    """移除外部資料中與USpace停車場重複的停車場"""
    duplicates = []
    
    print("檢查重複停車場...")
    for idx, external_row in external_df.iterrows():
        external_lat, external_lon = external_row['lat'], external_row['lon']
        external_name = str(external_row['name']).lower()
        
        for _, uspace_row in uspace_df.iterrows():
            uspace_lat, uspace_lon = uspace_row['lat'], uspace_row['lon']
            uspace_name = str(uspace_row['name']).lower()
            
            # 計算距離
            distance = geodesic(
                (external_lat, external_lon), 
                (uspace_lat, uspace_lon)
            ).meters
            
            # 如果距離很近，檢查名稱相似性
            if distance < distance_threshold:
                # 簡單的名稱相似性檢查
                if (external_name in uspace_name or 
                    uspace_name in external_name or
                    any(word in external_name for word in uspace_name.split() if len(word) > 2)):
                    duplicates.append(idx)
                    print(f"發現重複: {external_row['name']} <-> {uspace_row['name']} (距離: {distance:.1f}m)")
                    break
    
    # 移除重複項目
    external_deduped = external_df.drop(duplicates)
    print(f"移除 {len(duplicates)} 個重複停車場")
    print(f"外部停車場去重後數量: {len(external_deduped)}")
    
    return external_deduped

def standardize_uspace_data(df):
    """統一USpace資料格式"""
    standardized = []
    
    for _, row in df.iterrows():
        # 計算平均日間費率
        day_rates = [
            row.get('星期一day_rate', 0) or 0,
            row.get('星期二day_rate', 0) or 0,
            row.get('星期三day_rate', 0) or 0,
            row.get('星期四day_rate', 0) or 0,
            row.get('星期五day_rate', 0) or 0,
            row.get('星期六day_rate', 0) or 0,
            row.get('星期日day_rate', 0) or 0
        ]
        avg_day_rate = np.mean([rate for rate in day_rates if rate > 0]) if any(rate > 0 for rate in day_rates) else 0
        
        standardized.append({
            'id': row['id'],
            'name': row['name'],
            'lat': row['lat'],
            'lon': row['lon'],
            'city': row['city'],
            'district': row.get('zone', ''),
            'address': row.get('address', ''),
            'space_number': row.get('space_number', 0),
            'day_rate': avg_day_rate,
            'night_rate': row.get('夜間費率', 0) or 0,
            'monthly_rate': 0,  # USpace資料中沒有月租費
            'source': 'uspace',
            'building_type': row.get('building_type', ''),
            'financial_class': row.get('financial_class', '')
        })
    
    return pd.DataFrame(standardized)

def standardize_external_data(df):
    """統一外部停車場資料格式"""
    standardized = []
    
    for _, row in df.iterrows():
        # 計算平均日間費率
        day_rates = [
            row.get('weekday_day', 0) or 0,
            row.get('weekend_day', 0) or 0
        ]
        avg_day_rate = np.mean([rate for rate in day_rates if rate > 0]) if any(rate > 0 for rate in day_rates) else 0
        
        # 計算平均夜間費率
        night_rates = [
            row.get('weekday_night', 0) or 0,
            row.get('weekend_night', 0) or 0
        ]
        avg_night_rate = np.mean([rate for rate in night_rates if rate > 0]) if any(rate > 0 for rate in night_rates) else 0
        
        standardized.append({
            'id': row['id'],
            'name': row['name'],
            'lat': row['lat'],
            'lon': row['lon'],
            'city': row['city'],
            'district': row.get('district', ''),
            'address': row.get('address_info', ''),
            'space_number': row.get('space_number', 0),
            'day_rate': avg_day_rate,
            'night_rate': avg_night_rate,
            'monthly_rate': row.get('monthly_rate', 0) or 0,
            'source': 'external',
            'building_type': '',
            'financial_class': ''
        })
    
    return pd.DataFrame(standardized)

def save_cleaned_data(uspace_df, external_df):
    """儲存清洗後的資料"""
    
    # 合併資料
    combined_df = pd.concat([uspace_df, external_df], ignore_index=True)
    
    # 儲存為CSV
    combined_df.to_csv('parking_combined_cleaned.csv', index=False, encoding='utf-8-sig')
    
    # 儲存為JSON格式供前端使用
    parking_data = {
        'uspace_parking': uspace_df.to_dict('records'),
        'external_parking': external_df.to_dict('records'),
        'combined': combined_df.to_dict('records')
    }
    
    with open('parking_data.json', 'w', encoding='utf-8') as f:
        json.dump(parking_data, f, ensure_ascii=False, indent=2)
    
    print(f"資料處理完成！")
    print(f"USpace停車場: {len(uspace_df)}")
    print(f"外部停車場: {len(external_df)}")
    print(f"總計: {len(combined_df)}")
    
    return combined_df

if __name__ == "__main__":
    # 執行資料清洗
    uspace_data, external_data = load_and_clean_data()
    combined_data = save_cleaned_data(uspace_data, external_data)
    
    print("\n資料統計:")
    print(f"城市分布:")
    print(combined_data['city'].value_counts())
    print(f"\n資料來源分布:")
    print(combined_data['source'].value_counts())