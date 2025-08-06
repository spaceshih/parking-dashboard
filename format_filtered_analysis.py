#!/usr/bin/env python3
import csv

def create_readable_filtered_format():
    """創建易讀格式的過濾分析（僅臨停服務）"""
    
    results = []
    
    # 讀取過濾後的CSV檔案
    with open('uspace_area_analysis_filtered.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 解析價格區間分布
            price_dist = row['周邊停車場價格區間分布_按最高費率']
            
            # 初始化價格區間計數
            price_counts = {
                '0-30元': 0,
                '31-50元': 0,
                '51-80元': 0,
                '81-120元': 0,
                '121-200元': 0,
                '200元以上': 0
            }
            
            # 解析價格分布字串
            if price_dist and price_dist != '無資料':
                segments = price_dist.split('; ')
                for segment in segments:
                    if ':' in segment:
                        range_name, count_str = segment.split(':')
                        count = int(count_str.replace('場', ''))
                        if range_name in price_counts:
                            price_counts[range_name] = count
            
            # 計算主要價格區間
            max_count = max(price_counts.values())
            dominant_ranges = [k for k, v in price_counts.items() if v == max_count and v > 0]
            dominant_range = dominant_ranges[0] if dominant_ranges else '無資料'
            
            # 計算低價競爭者比例 (50元以下)
            total_competitors = sum(price_counts.values())
            low_price_count = price_counts['0-30元'] + price_counts['31-50元']
            low_price_ratio = (low_price_count / total_competitors * 100) if total_competitors > 0 else 0
            
            # 計算高價競爭者比例 (120元以上)
            high_price_count = price_counts['121-200元'] + price_counts['200元以上']
            high_price_ratio = (high_price_count / total_competitors * 100) if total_competitors > 0 else 0
            
            # USpace價格定位（基於最高費率）
            uspace_max_rate = float(row['uspace_max_rate']) if row['uspace_max_rate'] else 0
            if uspace_max_rate <= 30:
                uspace_position = '低價位'
            elif uspace_max_rate <= 50:
                uspace_position = '中低價位'
            elif uspace_max_rate <= 80:
                uspace_position = '中價位'
            elif uspace_max_rate <= 120:
                uspace_position = '中高價位'
            elif uspace_max_rate <= 200:
                uspace_position = '高價位'
            else:
                uspace_position = '超高價位'
            
            # 競爭優勢分析
            if low_price_ratio >= 60:
                competition_level = '低價競爭激烈'
            elif high_price_ratio >= 40:
                competition_level = '高價市場'
            elif total_competitors <= 5:
                competition_level = '競爭者少'
            else:
                competition_level = '競爭適中'
            
            # 價格競爭優勢
            max_rate_diff = float(row['USpace最高費率vs周邊差異百分比']) if row['USpace最高費率vs周邊差異百分比'] else 0
            if max_rate_diff < -20:
                price_advantage = '明顯較便宜'
            elif max_rate_diff < -5:
                price_advantage = '稍微便宜'
            elif max_rate_diff <= 5:
                price_advantage = '價格相當'
            elif max_rate_diff <= 20:
                price_advantage = '稍微較貴'
            else:
                price_advantage = '明顯較貴'
            
            results.append({
                'USpace停車場名稱': row['uspace_name'],
                'USpace城市': row['uspace_city'],
                'USpace區域': row['uspace_district'],
                'USpace日間費率': row['uspace_day_rate'],
                'USpace夜間費率': row['uspace_night_rate'],
                'USpace最高費率': row['uspace_max_rate'],
                'USpace價格定位': uspace_position,
                '周邊臨停服務停車場總數': row['周邊3km內有臨停服務停車場數量'],
                '周邊總車格數': row['周邊外部停車場總車格數'],
                '0-30元停車場數': price_counts['0-30元'],
                '31-50元停車場數': price_counts['31-50元'],
                '51-80元停車場數': price_counts['51-80元'],
                '81-120元停車場數': price_counts['81-120元'],
                '121-200元停車場數': price_counts['121-200元'],
                '200元以上停車場數': price_counts['200元以上'],
                '主要價格區間': dominant_range,
                '低價競爭者比例': f"{low_price_ratio:.1f}%",
                '高價競爭者比例': f"{high_price_ratio:.1f}%",
                '競爭狀況': competition_level,
                '周邊平均最高費率': row['周邊平均日間最高費率'],
                '周邊平均日間費率': row['周邊平均日間臨停費率'],
                '周邊平均夜間費率': row['周邊平均夜間臨停費率'] if row['周邊平均夜間臨停費率'] != '0' else '-',
                'USpace最高費率相對差異%': row['USpace最高費率vs周邊差異百分比'],
                'USpace日間費率相對差異%': row['USpace日間費率vs周邊差異百分比'],
                '價格競爭優勢': price_advantage,
                '競爭密度每平方公里': row['競爭密度_每平方公里外部停車場數'],
                '最近競爭者距離km': row['最近外部停車場距離km'],
                '周邊平均月租': row['周邊平均月租金額'] if row['周邊平均月租金額'] != '0' else '-'
            })
    
    return results

def save_formatted_csv(results):
    """儲存格式化的CSV"""
    filename = 'uspace_filtered_price_analysis.csv'
    
    fieldnames = [
        'USpace停車場名稱', 'USpace城市', 'USpace區域', 
        'USpace日間費率', 'USpace夜間費率', 'USpace最高費率', 'USpace價格定位',
        '周邊臨停服務停車場總數', '周邊總車格數',
        '0-30元停車場數', '31-50元停車場數', '51-80元停車場數', 
        '81-120元停車場數', '121-200元停車場數', '200元以上停車場數',
        '主要價格區間', '低價競爭者比例', '高價競爭者比例', '競爭狀況',
        '周邊平均最高費率', '周邊平均日間費率', '周邊平均夜間費率', '周邊平均月租',
        'USpace最高費率相對差異%', 'USpace日間費率相對差異%', '價格競爭優勢',
        '競爭密度每平方公里', '最近競爭者距離km'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"格式化的過濾分析已儲存到 {filename}")
    return filename

def generate_filtered_summary(results):
    """生成過濾後統計摘要"""
    total_uspace = len(results)
    
    # 統計USpace價格定位
    price_positions = {}
    competition_levels = {}
    price_advantages = {}
    
    for result in results:
        position = result['USpace價格定位']
        competition = result['競爭狀況']
        advantage = result['價格競爭優勢']
        
        price_positions[position] = price_positions.get(position, 0) + 1
        competition_levels[competition] = competition_levels.get(competition, 0) + 1
        price_advantages[advantage] = price_advantages.get(advantage, 0) + 1
    
    print(f"\n=== 過濾後價格分析摘要（僅包含臨停服務停車場）===")
    print(f"總USpace停車場數: {total_uspace}")
    
    print(f"\nUSpace價格定位分布（基於最高費率）:")
    for position, count in sorted(price_positions.items()):
        print(f"  {position}: {count}場 ({count/total_uspace*100:.1f}%)")
    
    print(f"\n市場競爭狀況分布:")
    for competition, count in sorted(competition_levels.items()):
        print(f"  {competition}: {count}場 ({count/total_uspace*100:.1f}%)")
    
    print(f"\n價格競爭優勢分布:")
    for advantage, count in sorted(price_advantages.items()):
        print(f"  {advantage}: {count}場 ({count/total_uspace*100:.1f}%)")
    
    # 計算平均價格區間分布
    avg_ranges = {
        '0-30元': 0, '31-50元': 0, '51-80元': 0, 
        '81-120元': 0, '121-200元': 0, '200元以上': 0
    }
    
    for result in results:
        for range_name in avg_ranges.keys():
            field_name = f"{range_name}停車場數"
            avg_ranges[range_name] += int(result[field_name])
    
    total_competitors = sum(avg_ranges.values())
    print(f"\n周邊臨停服務停車場價格分布 (總計{total_competitors}場):")
    for range_name, count in avg_ranges.items():
        if total_competitors > 0:
            percentage = count / total_competitors * 100
            print(f"  {range_name}: {count}場 ({percentage:.1f}%)")

def main():
    print("開始創建過濾後的易讀格式價格分析...")
    
    # 處理資料
    results = create_readable_filtered_format()
    
    # 儲存格式化CSV
    csv_filename = save_formatted_csv(results)
    
    # 生成統計摘要
    generate_filtered_summary(results)
    
    print(f"\n過濾分析完成！請查看 {csv_filename}")

if __name__ == "__main__":
    main()