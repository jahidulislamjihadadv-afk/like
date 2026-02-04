#!/usr/bin/env python3
"""
Example: How to use generated tokens for Free Fire API requests
"""

import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# =================== HELPER FUNCTIONS ===================

def encrypt_api(plain_text):
    """Encrypt data for Free Fire API"""
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(bytes.fromhex(plain_text), AES.block_size))
    return cipher_text.hex()

def encrypt_uid(uid):
    """Encrypt UID for API requests"""
    uid = int(uid)
    encoded_bytes = []
    
    while True:
        byte = uid & 0x7F
        uid >>= 7
        if uid:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not uid:
            break
    
    return bytes(encoded_bytes).hex()

def load_token(filename="generated_tokens.json", index=0):
    """Load token from file"""
    try:
        with open(filename, 'r') as f:
            tokens = json.load(f)
        
        if not isinstance(tokens, list):
            tokens = [tokens]
        
        if index < len(tokens):
            return tokens[index]
        else:
            print(f"❌ Token index {index} not found (only {len(tokens)} tokens)")
            return None
    except Exception as e:
        print(f"❌ Error loading token: {e}")
        return None

# =================== API EXAMPLES ===================

def example_get_player_info(token, target_uid, region="IND"):
    """
    Example 1: Get player information
    """
    print("\n" + "="*60)
    print("📋 EXAMPLE 1: Get Player Info")
    print("="*60)
    
    # Encrypt target UID
    encrypted_uid = encrypt_uid(target_uid)
    payload = f"08{encrypted_uid}1007"
    encrypted_payload = encrypt_api(payload)
    
    # Determine URL based on region
    if region.upper() == "IND":
        url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
    elif region.upper() == "BD":
        url = "https://client.bd.freefiremobile.com/GetPlayerPersonalShow"
    else:
        url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB52",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive"
    }
    
    print(f"🎯 Target UID: {target_uid}")
    print(f"📍 Region: {region}")
    print(f"🔗 URL: {url}")
    print(f"📤 Sending request...")
    
    try:
        response = requests.post(
            url,
            data=bytes.fromhex(encrypted_payload),
            headers=headers,
            verify=False,
            timeout=10
        )
        
        print(f"📥 Response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Success! Player info retrieved")
            print(f"📦 Response size: {len(response.content)} bytes")
            # Note: Response is encrypted protobuf, needs decoding
        else:
            print(f"❌ Failed: {response.text[:100]}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def example_send_friend_request(token, target_uid, region="IND"):
    """
    Example 2: Send friend request
    """
    print("\n" + "="*60)
    print("👥 EXAMPLE 2: Send Friend Request")
    print("="*60)
    
    # Encrypt target UID
    encrypted_uid = encrypt_uid(target_uid)
    payload = f"08a7c4839f1e10{encrypted_uid}1801"
    encrypted_payload = encrypt_api(payload)
    
    # Determine URL based on region
    if region.upper() == "IND":
        url = "https://client.ind.freefiremobile.com/RequestAddingFriend"
    elif region.upper() == "BD":
        url = "https://client.bd.freefiremobile.com/RequestAddingFriend"
    else:
        url = "https://client.ind.freefiremobile.com/RequestAddingFriend"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB52",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0"
    }
    
    print(f"🎯 Target UID: {target_uid}")
    print(f"📍 Region: {region}")
    print(f"🔗 URL: {url}")
    print(f"📤 Sending friend request...")
    
    try:
        response = requests.post(
            url,
            data=bytes.fromhex(encrypted_payload),
            headers=headers,
            verify=False,
            timeout=10
        )
        
        print(f"📥 Response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Success! Friend request sent")
        else:
            print(f"❌ Failed: {response.text[:100]}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def example_choose_emote(token, emote_id, region="IND"):
    """
    Example 3: Choose/equip emote
    """
    print("\n" + "="*60)
    print("🎭 EXAMPLE 3: Choose Emote")
    print("="*60)
    
    # Hardcoded encrypted payload for choosing emote
    # This is a simplified example
    encrypted_payload = "CA F6 83 22 2A 25 C7 BE FE B5 1F 59 54 4D B3 13"
    encrypted_payload = encrypted_payload.replace(" ", "")
    
    # Determine URL based on region
    if region.upper() == "IND":
        url = "https://client.ind.freefiremobile.com/ChooseEmote"
    elif region.upper() == "BD":
        url = "https://client.bd.freefiremobile.com/ChooseEmote"
    else:
        url = "https://client.ind.freefiremobile.com/ChooseEmote"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB52",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
        "Expect": "100-continue"
    }
    
    print(f"🎭 Emote ID: {emote_id}")
    print(f"📍 Region: {region}")
    print(f"🔗 URL: {url}")
    print(f"📤 Sending request...")
    
    try:
        response = requests.post(
            url,
            data=bytes.fromhex(encrypted_payload),
            headers=headers,
            verify=False,
            timeout=10
        )
        
        print(f"📥 Response: HTTP {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Success! Emote equipped")
        else:
            print(f"❌ Failed: {response.text[:100]}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# =================== MAIN ===================

def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("🎯 FREE FIRE TOKEN USAGE EXAMPLES")
    print("="*60)
    
    # Load token
    print("\n📂 Loading token from generated_tokens.json...")
    token_data = load_token()
    
    if not token_data:
        print("❌ No token found!")
        print("💡 Generate a token first: python token_gen.py <uid> <password>")
        return
    
    token = token_data['token']
    region = token_data.get('region', 'IND')
    bot_uid = token_data.get('bot_uid', 'Unknown')
    
    print(f"✅ Token loaded")
    print(f"👤 Bot UID: {bot_uid}")
    print(f"📍 Region: {region}")
    print(f"🎫 Token: {token[:50]}...")
    
    # Example 1: Get player info
    target_uid = input("\n🎯 Enter target UID for player info (or press Enter to skip): ").strip()
    if target_uid:
        example_get_player_info(token, target_uid, region)
    
    # Example 2: Send friend request
    target_uid = input("\n👥 Enter target UID for friend request (or press Enter to skip): ").strip()
    if target_uid:
        example_send_friend_request(token, target_uid, region)
    
    # Example 3: Choose emote
    emote_choice = input("\n🎭 Choose emote? (y/n): ").strip().lower()
    if emote_choice == 'y':
        emote_id = input("Enter emote ID (e.g., 909000063): ").strip()
        if emote_id:
            example_choose_emote(token, emote_id, region)
    
    print("\n" + "="*60)
    print("✅ Examples complete!")
    print("="*60)
    print("\n💡 Tips:")
    print("   - All API responses are encrypted protobuf")
    print("   - You need to decrypt and parse them")
    print("   - See main.py for full decryption examples")
    print("   - Token expires after some time")
    print("\n")

if __name__ == "__main__":
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()
