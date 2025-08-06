#!/usr/bin/env python3
import base64

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
        
        # Convert to string
        return decrypted_data.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error decrypting: {e}")
        return None

def search_in_file(file_path, search_term, key):
    """
    Search for a term in the encrypted file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            encrypted_content = f.read().strip()
        
        # Decrypt the content
        print("Decrypting file...")
        decrypted_content = xor_decrypt(encrypted_content, key)
        
        if decrypted_content is None:
            print("Failed to decrypt file")
            return
        
        print(f"File decrypted successfully. Length: {len(decrypted_content)} characters")
        
        # Search for the term
        lines = decrypted_content.split('\n')
        matches = []
        
        for line_num, line in enumerate(lines, 1):
            if search_term in line:
                matches.append((line_num, line.strip()))
        
        if matches:
            print(f"\nFound {len(matches)} matches for '{search_term}':")
            print("=" * 80)
            for line_num, line in matches:
                print(f"Line {line_num}: {line}")
                print("-" * 80)
        else:
            print(f"\nNo matches found for '{search_term}'")
            
        # Save decrypted content to file for inspection
        with open('decrypted_buildings.txt', 'w', encoding='utf-8') as f:
            f.write(decrypted_content)
        print("Decrypted content saved to 'decrypted_buildings.txt'")
        
        # Also check for partial matches or similar terms
        partial_matches = []
        songshan_matches = []
        wenchuang_matches = []
        
        for line_num, line in enumerate(lines, 1):
            if "松山" in line:
                songshan_matches.append((line_num, line.strip()))
            if "文創" in line:
                wenchuang_matches.append((line_num, line.strip()))
            if "松山" in line or "文創" in line or "創意" in line or "創造" in line:
                partial_matches.append((line_num, line.strip()))
        
        if songshan_matches:
            print(f"\nFound {len(songshan_matches)} matches containing '松山':")
            print("=" * 80)
            for line_num, line in songshan_matches[:5]:  # Show first 5 matches
                print(f"Line {line_num}: {line}")
                print("-" * 80)
                
        if wenchuang_matches:
            print(f"\nFound {len(wenchuang_matches)} matches containing '文創':")
            print("=" * 80)
            for line_num, line in wenchuang_matches[:5]:  # Show first 5 matches
                print(f"Line {line_num}: {line}")
                print("-" * 80)
                
        if partial_matches and not matches:
            print(f"\nTotal partial matches found: {len(partial_matches)}")
            
        # Look for parking-related terms
        parking_matches = []
        for line_num, line in enumerate(lines, 1):
            if "車位" in line or "停車" in line or "車格" in line:
                parking_matches.append((line_num, line.strip()))
        
        if parking_matches:
            print(f"\nFound {len(parking_matches)} parking-related entries")
            print("Sample parking entries:")
            print("=" * 80)
            for line_num, line in parking_matches[:3]:  # Show first 3 matches
                print(f"Line {line_num}: {line}")
                print("-" * 80)
                
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    encrypted_file = "/Users/space/test-claude-project/剩餘車格數/建物.encrypted"
    search_term = "松山文創"
    encryption_key = "PARKING_DASHBOARD_2024_SECURE_KEY_V1"
    
    search_in_file(encrypted_file, search_term, encryption_key)