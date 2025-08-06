#!/usr/bin/env python3
import base64
import csv
import io

def xor_decrypt(encrypted_b64, key):
    """
    Decrypt XOR encrypted Base64 data
    """
    try:
        # Decode from Base64
        encrypted_data = base64.b64decode(encrypted_b64)
        
        # XOR decrypt with key
        decrypted_data = bytearray()
        key_len = len(key)
        
        for i, byte in enumerate(encrypted_data):
            key_byte = ord(key[i % key_len])
            decrypted_data.append(byte ^ key_byte)
        
        # Try different encodings
        for encoding in ['utf-8', 'gbk', 'big5', 'utf-16', 'iso-8859-1']:
            try:
                return decrypted_data.decode(encoding)
            except:
                continue
                
        return decrypted_data.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error decrypting: {e}")
        return None

def advanced_search(file_path, key):
    """
    Advanced search with multiple approaches
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            encrypted_content = f.read().strip()
        
        print("Attempting decryption...")
        decrypted_content = xor_decrypt(encrypted_content, key)
        
        if decrypted_content is None:
            print("Failed to decrypt file")
            return
        
        print(f"File decrypted successfully. Length: {len(decrypted_content)} characters")
        
        # Try to parse as CSV
        try:
            csv_reader = csv.DictReader(io.StringIO(decrypted_content))
            rows = list(csv_reader)
            print(f"Successfully parsed as CSV with {len(rows)} rows")
            
            # Print column names
            if rows:
                print("Column names:", list(rows[0].keys()))
                
                # Search for Songshan Creative Park related terms
                search_terms = [
                    '松山文創', '松山', '文創', 'Songshan', 'Creative', 'SONGSHAN', 'CREATIVE',
                    '創意', '創作', '文化創意', '松山文創園區', '車位', '停車', '車格'
                ]
                
                matches = []
                for i, row in enumerate(rows):
                    for field_name, field_value in row.items():
                        if field_value:
                            field_str = str(field_value)
                            for term in search_terms:
                                if term in field_str:
                                    matches.append({
                                        'row': i + 1,
                                        'field': field_name,
                                        'value': field_str,
                                        'term_found': term
                                    })
                
                if matches:
                    print(f"\nFound {len(matches)} matches:")
                    for match in matches[:10]:  # Show first 10 matches
                        print(f"Row {match['row']}, Field '{match['field']}': {match['value'][:100]}...")
                        print(f"  -> Found term: {match['term_found']}")
                        print("-" * 80)
                else:
                    print("\nNo matches found for search terms")
                    
                    # Show sample data
                    print("\nSample data (first 3 rows):")
                    for i, row in enumerate(rows[:3]):
                        print(f"Row {i+1}:")
                        for field, value in row.items():
                            if value and len(str(value)) > 5:  # Only show non-empty, meaningful fields
                                print(f"  {field}: {str(value)[:100]}...")
                        print("-" * 40)
                        
        except Exception as csv_error:
            print(f"Could not parse as CSV: {csv_error}")
            
            # Fall back to line-by-line search
            lines = decrypted_content.split('\n')
            print(f"Searching {len(lines)} lines for terms...")
            
            search_terms = ['松山文創', '松山', '文創', 'Songshan', 'Creative']
            matches = []
            
            for line_num, line in enumerate(lines, 1):
                for term in search_terms:
                    if term in line:
                        matches.append((line_num, line.strip()[:200], term))
            
            if matches:
                print(f"\nFound {len(matches)} line matches:")
                for line_num, line, term in matches[:5]:
                    print(f"Line {line_num} (term: {term}): {line}")
                    print("-" * 80)
            else:
                print("\nNo matches found in line search")
                
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    encrypted_file = "/Users/space/test-claude-project/剩餘車格數/建物.encrypted"
    encryption_key = "PARKING_DASHBOARD_2024_SECURE_KEY_V1"
    
    advanced_search(encrypted_file, encryption_key)