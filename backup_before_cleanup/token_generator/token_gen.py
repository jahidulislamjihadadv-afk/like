#!/usr/bin/env python3
"""
Free Fire Token Generator
Standalone tool to generate JWT tokens from UID and password
No emotes or bundles required - just token generation
"""

import requests
import json
import time
import random
import ssl
import aiohttp
import asyncio
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =================== CONFIGURATION ======================
OUTPUT_FILE = "generated_tokens.json"

# =================== HELPER FUNCTIONS ===================

async def generate_user_agent():
    """Generate random user agent for Garena SDK"""
    versions = [
        '4.0.18P6', '4.0.19P7', '4.0.20P1', '4.1.0P3', '4.1.5P2', '4.2.1P8',
        '4.2.3P1', '5.0.1B2', '5.0.2P4', '5.1.0P1', '5.2.0B1', '5.2.5P3',
        '5.3.0B1', '5.3.2P2', '5.4.0P1', '5.4.3B2', '5.5.0P1', '5.5.2P3'
    ]
    models = [
        'SM-A125F', 'SM-A225F', 'SM-A325M', 'SM-A515F', 'SM-A725F', 'SM-M215F', 'SM-M325FV',
        'Redmi 9A', 'Redmi 9C', 'POCO M3', 'POCO M4 Pro', 'RMX2185', 'RMX3085',
        'moto g(9) play', 'CPH2239', 'V2027', 'OnePlus Nord', 'ASUS_Z01QD',
    ]
    android_versions = ['9', '10', '11', '12', '13', '14']
    languages = ['en-US', 'es-MX', 'pt-BR', 'id-ID', 'ru-RU', 'hi-IN']
    countries = ['USA', 'MEX', 'BRA', 'IDN', 'RUS', 'IND']
    
    version = random.choice(versions)
    model = random.choice(models)
    android = random.choice(android_versions)
    lang = random.choice(languages)
    country = random.choice(countries)
    
    return f"GarenaMSDK/{version}({model};Android {android};{lang};{country};)"

async def encrypt_proto(encoded_hex):
    """Encrypt protobuf data using AES CBC"""
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload

# =================== TOKEN GENERATION ===================

async def get_access_token(uid, password):
    """
    Step 1: Get access token from Garena OAuth
    """
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": await generate_user_agent(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    
    print(f"📡 Requesting access token for UID: {uid}...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status != 200:
                print(f"❌ Failed to get access token: HTTP {response.status}")
                return None, None
            
            data = await response.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            
            if open_id and access_token:
                print(f"✅ Access token obtained")
                return open_id, access_token
            else:
                print(f"❌ Invalid response from Garena OAuth")
                return None, None

async def create_major_login_payload(open_id, access_token):
    """
    Step 2: Create MajorLogin protobuf payload
    """
    # Import protobuf module
    try:
        import sys
        import os
        # Add parent directory to path to import Modules
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from Modules import MajoRLoGinrEq_pb2
    except ImportError:
        print("❌ Error: Cannot import MajoRLoGinrEq_pb2")
        print("💡 Make sure you run this from the project directory")
        return None
    
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.120.2"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    
    string = major_login.SerializeToString()
    return await encrypt_proto(string)

async def perform_major_login(payload):
    """
    Step 3: Send MajorLogin request to Free Fire server
    """
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB52"
    }
    
    print(f"🔐 Performing MajorLogin...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as response:
            if response.status == 200:
                print(f"✅ MajorLogin successful")
                return await response.read()
            else:
                print(f"❌ MajorLogin failed: HTTP {response.status}")
                return None

async def parse_major_login_response(response_data):
    """
    Step 4: Parse MajorLogin response to extract JWT token
    """
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from Modules import MajoRLoGinrEs_pb2
    except ImportError:
        print("❌ Error: Cannot import MajoRLoGinrEs_pb2")
        return None
    
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(response_data)
    
    token = proto.token
    region = getattr(proto, 'region', 'IND')
    account_uid = proto.account_uid
    
    if token:
        print(f"✅ JWT Token extracted")
        print(f"📍 Region: {region}")
        print(f"👤 Account UID: {account_uid}")
        return {
            "token": token,
            "region": region,
            "account_uid": str(account_uid)
        }
    else:
        print(f"❌ No token in response")
        return None

# =================== MAIN FUNCTION ===================

async def generate_token(uid, password):
    """
    Complete token generation flow
    """
    print("\n" + "="*60)
    print("🎯 FREE FIRE TOKEN GENERATOR")
    print("="*60)
    print(f"📝 UID: {uid}")
    print(f"🔑 Password: {password[:20]}...")
    print("="*60 + "\n")
    
    # Step 1: Get access token
    open_id, access_token = await get_access_token(uid, password)
    if not open_id or not access_token:
        print("\n❌ Failed at Step 1: Could not get access token")
        print("💡 Check your UID and password")
        return None
    
    # Step 2: Create MajorLogin payload
    payload = await create_major_login_payload(open_id, access_token)
    if not payload:
        print("\n❌ Failed at Step 2: Could not create login payload")
        return None
    
    # Step 3: Perform MajorLogin
    response = await perform_major_login(payload)
    if not response:
        print("\n❌ Failed at Step 3: MajorLogin request failed")
        print("💡 Account might be banned or invalid")
        return None
    
    # Step 4: Parse response
    token_data = await parse_major_login_response(response)
    if not token_data:
        print("\n❌ Failed at Step 4: Could not extract token")
        return None
    
    # Extract only the token string and wrap in object
    token_string = token_data["token"]
    
    print("\n" + "="*60)
    print("✅ TOKEN GENERATED SUCCESSFULLY!")
    print("="*60)
    print(f"🎫 Token: {token_string[:50]}...")
    print(f"📍 Region: {token_data['region']}")
    print(f"👤 UID: {uid}")
    print("="*60 + "\n")
    
    # Return token in object format
    return {"token": token_string}

async def save_token(token_obj, filename=OUTPUT_FILE):
    """Save token to JSON file - {"token": "..."} format"""
    try:
        # Load existing tokens
        existing_tokens = []
        try:
            with open(filename, 'r') as f:
                existing_tokens = json.load(f)
                if not isinstance(existing_tokens, list):
                    existing_tokens = [existing_tokens]
        except FileNotFoundError:
            pass
        
        # Add new token object
        existing_tokens.append(token_obj)
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(existing_tokens, f, indent=2)
        
        print(f"💾 Token saved to {filename}")
        print(f"📊 Total tokens in file: {len(existing_tokens)}")
        return True
    except Exception as e:
        print(f"❌ Error saving token: {e}")
        return False

async def load_credentials_from_file(filename="credentials.txt"):
    """Load UID and password from file"""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        credentials = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Format: uid,password or uid=xxx,password=xxx
            if ',' in line:
                parts = line.split(',')
                uid = parts[0].split('=')[-1].strip()
                password = parts[1].split('=')[-1].strip()
                credentials.append((uid, password))
        
        return credentials
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []

# =================== CLI INTERFACE ===================

async def main():
    """Main entry point"""
    import sys
    
    print("\n" + "="*60)
    print("🎯 FREE FIRE TOKEN GENERATOR")
    print("="*60)
    print("📝 No emotes or bundles required - just tokens!")
    print("="*60 + "\n")
    
    # Check command line arguments
    if len(sys.argv) >= 3:
        # Single token generation from command line
        uid = sys.argv[1]
        password = sys.argv[2]
        
        token_obj = await generate_token(uid, password)
        if token_obj:
            await save_token(token_obj)
    
    elif len(sys.argv) == 2 and sys.argv[1] == "--batch":
        # Batch generation from credentials.txt
        print("📂 Batch mode: Loading credentials from credentials.txt")
        credentials = await load_credentials_from_file("credentials.txt")
        
        if not credentials:
            print("❌ No credentials found in credentials.txt")
            print("💡 Format: uid,password (one per line)")
            return
        
        print(f"📋 Found {len(credentials)} accounts\n")
        
        success_count = 0
        for i, (uid, password) in enumerate(credentials, 1):
            print(f"\n{'='*60}")
            print(f"Processing account {i}/{len(credentials)}")
            print(f"{'='*60}")
            
            token_obj = await generate_token(uid, password)
            if token_obj:
                await save_token(token_obj)
                success_count += 1
            
            # Small delay between requests
            if i < len(credentials):
                await asyncio.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"✅ Batch complete: {success_count}/{len(credentials)} tokens generated")
        print(f"{'='*60}\n")
    
    else:
        # Interactive mode
        print("Usage:")
        print("  1. Single token:  python token_gen.py <uid> <password>")
        print("  2. Batch mode:    python token_gen.py --batch")
        print("                    (reads from credentials.txt)")
        print("\nInteractive mode:")
        
        uid = input("Enter UID: ").strip()
        password = input("Enter Password: ").strip()
        
        if uid and password:
            token_obj = await generate_token(uid, password)
            if token_obj:
                await save_token(token_obj)
        else:
            print("❌ UID and password are required")

if __name__ == "__main__":
    asyncio.run(main())
