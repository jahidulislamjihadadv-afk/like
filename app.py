from flask import Flask, request, jsonify, render_template
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import aiohttp
import requests
import json
import like_pb2
import like_count_pb2
import uid_generator_pb2
import threading
import urllib3
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import atexit
import os
import base64

# Configuration
TOKEN_BATCH_SIZE = 189
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global State for Batch Management
current_batch_indices = {}
batch_indices_lock = threading.Lock()

def get_next_batch_tokens(server_name, all_tokens):
    if not all_tokens:
        return []
    
    total_tokens = len(all_tokens)
    
    # If we have fewer tokens than batch size, use all available tokens
    if total_tokens <= TOKEN_BATCH_SIZE:
        return all_tokens
    
    with batch_indices_lock:
        if server_name not in current_batch_indices:
            current_batch_indices[server_name] = 0
        
        current_index = current_batch_indices[server_name]
        
        # Calculate the batch
        start_index = current_index
        end_index = start_index + TOKEN_BATCH_SIZE
        
        # If we reach or exceed the end, wrap around
        if end_index > total_tokens:
            remaining = end_index - total_tokens
            batch_tokens = all_tokens[start_index:total_tokens] + all_tokens[0:remaining]
        else:
            batch_tokens = all_tokens[start_index:end_index]
        
        # Update the index for next time
        next_index = (current_index + TOKEN_BATCH_SIZE) % total_tokens
        current_batch_indices[server_name] = next_index
        
        return batch_tokens

def get_random_batch_tokens(server_name, all_tokens):
    """Alternative method: use random sampling for better distribution"""
    if not all_tokens:
        return []
    
    total_tokens = len(all_tokens)
    
    # If we have fewer tokens than batch size, use all available tokens
    if total_tokens <= TOKEN_BATCH_SIZE:
        return all_tokens.copy()
    
    # Randomly select tokens without replacement
    return random.sample(all_tokens, TOKEN_BATCH_SIZE)

def get_token_health(token_str):
    """Check if token is valid and return expiry info"""
    try:
        parts = token_str.split('.')
        if len(parts) != 3:
            return None
        
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = base64.urlsafe_b64decode(payload)
        token_data = json.loads(decoded)
        
        exp_timestamp = token_data.get('exp')
        if not exp_timestamp:
            return None
        
        expiry_dt = datetime.fromtimestamp(exp_timestamp)
        now = datetime.now()
        days_left = (expiry_dt - now).days
        
        return {
            'is_valid': days_left > 0,
            'days_left': days_left,
            'expiry_datetime': expiry_dt,
            'account_id': token_data.get('account_id'),
            'nickname': token_data.get('nickname', 'N/A'),
            'region': token_data.get('noti_region') or token_data.get('lock_region')
        }
    except Exception as e:
        print(f"Error checking token health: {e}")
        return None

def cleanup_expired_tokens(filepath):
    """Remove expired tokens from a json file and save"""
    try:
        if not os.path.exists(filepath):
            return 0, 0
        
        with open(filepath, 'r') as f:
            tokens = json.load(f)
        
        if not isinstance(tokens, list):
            tokens = [tokens]
        
        valid_tokens = []
        expired_count = 0
        
        for token_dict in tokens:
            token_str = token_dict.get('token', '')
            health = get_token_health(token_str)
            
            if health and health['is_valid']:
                valid_tokens.append(token_dict)
            else:
                expired_count += 1
                if health:
                    print(f"  🗑️  Removing expired token: {health.get('nickname', 'N/A')} (expired {abs(health['days_left'])} days ago)")
        
        # Write back cleaned tokens
        if valid_tokens:
            with open(filepath, 'w') as f:
                json.dump(valid_tokens, f, indent=2)
        else:
            # If no valid tokens remaining, delete the file
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return len(valid_tokens), expired_count
    
    except Exception as e:
        print(f"Error cleaning up {filepath}: {e}")
        return 0, 0

def cleanup_all_expired_tokens():
    """Clean expired tokens from all token files"""
    token_files = [
        'token_bd.json', 'token_bd_visit.json',
        'token_ind.json', 'token_ind_visit.json',
        'token_br.json', 'token_br_visit.json'
    ]
    
    total_valid = 0
    total_expired = 0
    
    print("\n🧹 CLEANING EXPIRED TOKENS...")
    print("="*60)
    
    for filepath in token_files:
        if os.path.exists(filepath):
            valid, expired = cleanup_expired_tokens(filepath)
            if expired > 0 or valid > 0:
                print(f"📄 {filepath}: {valid} valid, {expired} expired removed")
                total_valid += valid
                total_expired += expired
    
    print("="*60)
    if total_expired > 0:
        print(f"✅ Cleanup complete: {total_expired} expired tokens removed, {total_valid} valid tokens kept")
    else:
        print("✅ All tokens are fresh!")
    print("="*60 + "\n")
    
    return total_valid, total_expired

def get_token_health_summary():
    """Get health status of all tokens"""
    token_files = {
        'token_bd.json': 'Regular (BD)',
        'token_bd_visit.json': 'Visit (BD)',
        'token_ind.json': 'Regular (IND)',
        'token_ind_visit.json': 'Visit (IND)',
        'token_br.json': 'Regular (BR)',
        'token_br_visit.json': 'Visit (BR)'
    }
    
    summary = {}
    
    for filepath, label in token_files.items():
        if not os.path.exists(filepath):
            continue
        
        try:
            with open(filepath, 'r') as f:
                tokens = json.load(f)
            
            if not isinstance(tokens, list):
                tokens = [tokens]
            
            valid = 0
            expired = 0
            min_days = float('inf')
            max_days = -float('inf')
            
            for token_dict in tokens:
                token_str = token_dict.get('token', '')
                health = get_token_health(token_str)
                
                if health:
                    if health['is_valid']:
                        valid += 1
                        min_days = min(min_days, health['days_left'])
                        max_days = max(max_days, health['days_left'])
                    else:
                        expired += 1
            
            summary[label] = {
                'total': len(tokens),
                'valid': valid,
                'expired': expired,
                'min_days': min_days if min_days != float('inf') else 0,
                'max_days': max_days if max_days != -float('inf') else 0,
                'health': '✅ GOOD' if expired == 0 else ('⚠️  NEEDS_REFRESH' if expired > 0 else '❌ EXPIRED')
            }
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    return summary

def load_tokens(server_name, for_visit=False):
    if for_visit:
        if server_name == "IND":
            path = "token_ind_visit.json"
        elif server_name in {"BR", "US", "SAC", "NA"}:
            path = "token_br_visit.json"
        else:
            path = "token_bd_visit.json"
    else:
        if server_name == "IND":
            path = "token_ind.json"
        elif server_name in {"BR", "US", "SAC", "NA"}:
            path = "token_br.json"
        else:
            path = "token_bd.json"

    try:
        with open(path, "r") as f:
            tokens = json.load(f)
            if isinstance(tokens, list) and all(isinstance(t, dict) and "token" in t for t in tokens):
                # Auto-cleanup: Remove expired tokens before using
                valid_tokens = []
                expired_count = 0
                
                for token_dict in tokens:
                    token_str = token_dict.get('token', '')
                    health = get_token_health(token_str)
                    
                    if health and health['is_valid']:
                        valid_tokens.append(token_dict)
                    else:
                        expired_count += 1
                
                # Save cleaned tokens back if any were removed
                if expired_count > 0:
                    if valid_tokens:
                        with open(path, 'w') as f:
                            json.dump(valid_tokens, f, indent=2)
                        print(f"🧹 {path}: Removed {expired_count} expired tokens, {len(valid_tokens)} valid remaining")
                    else:
                        os.remove(path)
                        print(f"🧹 {path}: All tokens expired, file deleted")
                
                print(f"Loaded {len(valid_tokens)} valid tokens from {path} for server {server_name}")
                return valid_tokens
            else:
                print(f"Warning: Token file {path} is not in the expected format. Returning empty list.")
                return []
    except FileNotFoundError:
        print(f"Warning: Token file {path} not found. Returning empty list for server {server_name}.")
        return []
    except json.JSONDecodeError:
        print(f"Warning: Token file {path} contains invalid JSON. Returning empty list.")
        return []

def encrypt_message(plaintext):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    encrypted_message = cipher.encrypt(padded_message)
    return binascii.hexlify(encrypted_message).decode('utf-8')

def create_protobuf_message(user_id, region):
    message = like_pb2.like()
    message.uid = int(user_id)
    message.region = region
    return message.SerializeToString()

def create_protobuf_for_profile_check(uid):
    message = uid_generator_pb2.uid_generator()
    message.krishna_ = int(uid)
    message.teamXdarks = 1
    return message.SerializeToString()

def enc_profile_check_payload(uid):
    protobuf_data = create_protobuf_for_profile_check(uid)
    encrypted_uid = encrypt_message(protobuf_data)
    return encrypted_uid

async def send_single_like_request(encrypted_like_payload, token_dict, url):
    edata = bytes.fromhex(encrypted_like_payload)
    token_value = token_dict.get("token", "")
    if not token_value:
        print("Warning: send_single_like_request received an empty or invalid token_dict.")
        return 999

    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Authorization': f"Bearer {token_value}",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB52"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=edata, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    print(f"Like request failed for token {token_value[:10]}... with status: {response.status}")
                return response.status
    except asyncio.TimeoutError:
        print(f"Like request timed out for token {token_value[:10]}...")
        return 998
    except Exception as e:
        print(f"Exception in send_single_like_request for token {token_value[:10]}...: {e}")
        return 997

async def send_likes_with_token_batch(uid, server_region_for_like_proto, like_api_url, token_batch_to_use):
    if not token_batch_to_use:
        print("No tokens provided in the batch to send_likes_with_token_batch.")
        return []

    like_protobuf_payload = create_protobuf_message(uid, server_region_for_like_proto)
    encrypted_like_payload = encrypt_message(like_protobuf_payload)
    
    tasks = []
    for token_dict_for_request in token_batch_to_use:
        tasks.append(send_single_like_request(encrypted_like_payload, token_dict_for_request, like_api_url))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful_sends = sum(1 for r in results if isinstance(r, int) and r == 200)
    failed_sends = len(token_batch_to_use) - successful_sends
    print(f"Attempted {len(token_batch_to_use)} like sends from batch. Successful: {successful_sends}, Failed/Error: {failed_sends}")
    return results

def make_profile_check_request(encrypted_profile_payload, server_name, token_dict):
    token_value = token_dict.get("token", "")
    if not token_value:
        print("Warning: make_profile_check_request received an empty token_dict.")
        return None

    if server_name == "IND":
        url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
    elif server_name in {"BR", "US", "SAC", "NA"}:
        url = "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
    else:
        url = "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"

    edata = bytes.fromhex(encrypted_profile_payload)
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Authorization': f"Bearer {token_value}",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB52"
    }
    try:
        response = requests.post(url, data=edata, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        binary_data = response.content
        decoded_info = decode_protobuf_profile_info(binary_data)
        return decoded_info
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error in make_profile_check_request for token {token_value[:10]}...: {e.response.status_code} - {e.response.text[:100]}")
    except requests.exceptions.RequestException as e:
        print(f"Request error in make_profile_check_request for token {token_value[:10]}...: {e}")
    except Exception as e:
        print(f"Unexpected error in make_profile_check_request for token {token_value[:10]}... processing response: {e}")
    return None

def decode_protobuf_profile_info(binary_data):
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary_data)
        return items
    except Exception as e:
        print(f"Error decoding Protobuf profile data: {e}")
        return None

def refresh_tokens_logic():
    """Core logic for token refresh (used by both endpoint and scheduler)"""
    try:
        import sys
        import os
        
        # Add token_generator to path
        token_gen_path = os.path.join(os.path.dirname(__file__), 'token_generator')
        if token_gen_path not in sys.path:
            sys.path.insert(0, token_gen_path)
        
        # Import token generation functions
        from token_generator.token_gen import load_credentials_from_file, generate_token
        
        # Check credential files
        credentials_file = os.path.join(token_gen_path, 'credentials.txt')
        visit_file_creds = os.path.join(token_gen_path, 'visit.txt')
        
        has_credentials = os.path.exists(credentials_file)
        has_visit = os.path.exists(visit_file_creds)
        
        if not has_credentials and not has_visit:
            return {
                "status": "error",
                "message": "No credential files found. Create credentials.txt or visit.txt in token_generator folder",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        print("\n" + "="*60)
        print("🔄 TOKEN REFRESH TRIGGERED")
        print("="*60)
        
        # Define output file paths
        output_file = "token_bd.json"
        visit_file = "token_bd_visit.json"
        
        total_success = 0
        total_failed = 0
        all_failed_accounts = []
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # ========== PROCESS REGULAR TOKENS ==========
            if has_credentials:
                print("\n📋 Processing credentials.txt...")
                credentials = loop.run_until_complete(load_credentials_from_file(credentials_file))
                
                if credentials:
                    print(f"Found {len(credentials)} accounts in credentials.txt")
                    
                    # Delete old file
                    if os.path.exists(output_file):
                        os.remove(output_file)
                        print(f"Deleted old {output_file}")
                    
                    success_count = 0
                    failed_accounts = []
                    
                    for i, (uid, password) in enumerate(credentials, 1):
                        print(f"[{i}/{len(credentials)}] Processing UID: {uid}")
                        
                        try:
                            token_obj = loop.run_until_complete(generate_token(uid, password))
                            
                            if token_obj:
                                existing_tokens = []
                                try:
                                    with open(output_file, 'r') as f:
                                        existing_tokens = json.load(f)
                                        if not isinstance(existing_tokens, list):
                                            existing_tokens = [existing_tokens]
                                except FileNotFoundError:
                                    pass
                                
                                existing_tokens.append(token_obj)
                                
                                with open(output_file, 'w') as f:
                                    json.dump(existing_tokens, f, indent=2)
                                
                                success_count += 1
                                print(f"✅ Token saved ({success_count}/{len(credentials)})")
                            else:
                                failed_accounts.append((uid, "Generation failed"))
                        
                        except Exception as e:
                            print(f"❌ Error: {str(e)[:100]}")
                            failed_accounts.append((uid, str(e)[:50]))
                        
                        if i < len(credentials):
                            loop.run_until_complete(asyncio.sleep(2))
                    
                    total_success += success_count
                    total_failed += len(failed_accounts)
                    all_failed_accounts.extend([{"uid": uid, "reason": reason, "file": "credentials.txt"} for uid, reason in failed_accounts])
                    
                    print(f"✅ Regular tokens: {success_count}/{len(credentials)} successful")
            
            # ========== PROCESS VISIT TOKENS ==========
            if has_visit:
                print("\n📋 Processing visit.txt...")
                visit_credentials = loop.run_until_complete(load_credentials_from_file(visit_file_creds))
                
                if visit_credentials:
                    print(f"Found {len(visit_credentials)} accounts in visit.txt")
                    
                    # Delete old file
                    if os.path.exists(visit_file):
                        os.remove(visit_file)
                        print(f"Deleted old {visit_file}")
                    
                    visit_success_count = 0
                    visit_failed_accounts = []
                    
                    for i, (uid, password) in enumerate(visit_credentials, 1):
                        print(f"[{i}/{len(visit_credentials)}] Processing UID: {uid}")
                        
                        try:
                            token_obj = loop.run_until_complete(generate_token(uid, password))
                            
                            if token_obj:
                                existing_tokens = []
                                try:
                                    with open(visit_file, 'r') as f:
                                        existing_tokens = json.load(f)
                                        if not isinstance(existing_tokens, list):
                                            existing_tokens = [existing_tokens]
                                except FileNotFoundError:
                                    pass
                                
                                existing_tokens.append(token_obj)
                                
                                with open(visit_file, 'w') as f:
                                    json.dump(existing_tokens, f, indent=2)
                                
                                visit_success_count += 1
                                print(f"✅ Visit token saved ({visit_success_count}/{len(visit_credentials)})")
                            else:
                                visit_failed_accounts.append((uid, "Generation failed"))
                        
                        except Exception as e:
                            print(f"❌ Error: {str(e)[:100]}")
                            visit_failed_accounts.append((uid, str(e)[:50]))
                        
                        if i < len(visit_credentials):
                            loop.run_until_complete(asyncio.sleep(2))
                    
                    total_success += visit_success_count
                    total_failed += len(visit_failed_accounts)
                    all_failed_accounts.extend([{"uid": uid, "reason": reason, "file": "visit.txt"} for uid, reason in visit_failed_accounts])
                    
                    print(f"✅ Visit tokens: {visit_success_count}/{len(visit_credentials)} successful")
        
        finally:
            loop.close()
        
        print("\n" + "="*60)
        print("✅ TOKEN REFRESH COMPLETE")
        print("="*60)
        
        return {
            "status": "success",
            "message": "Tokens refreshed successfully",
            "total_successful": total_success,
            "total_failed": total_failed,
            "failed_accounts": all_failed_accounts,
            "files_processed": {
                "credentials.txt": has_credentials,
                "visit.txt": has_visit
            },
            "output_files": {
                "regular_tokens": output_file if has_credentials else None,
                "visit_tokens": visit_file if has_visit else None
            },
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except Exception as e:
        print(f"\n❌ Token refresh error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def get_token_expiry_info(token_file):
    """Extract expiry time from first token in token file"""
    try:
        if not os.path.exists(token_file):
            return None
        
        with open(token_file, 'r') as f:
            tokens = json.load(f)
            if not tokens or len(tokens) == 0:
                return None
            
            token_str = tokens[0].get('token', '')
            if not token_str:
                return None
            
            # Decode JWT payload
            parts = token_str.split('.')
            if len(parts) != 3:
                return None
            
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            try:
                decoded = binascii.a2b_base64(payload)
                token_data = json.loads(decoded)
                exp_timestamp = token_data.get('exp')
                
                if exp_timestamp:
                    expiry_dt = datetime.fromtimestamp(exp_timestamp)
                    return {
                        'expiry_timestamp': exp_timestamp,
                        'expiry_datetime': expiry_dt,
                        'days_remaining': (expiry_dt - datetime.now()).days,
                        'account_id': token_data.get('account_id', 'N/A'),
                        'nickname': token_data.get('nickname', 'N/A')
                    }
            except Exception as e:
                print(f"Error decoding token payload: {e}")
                return None
    
    except Exception as e:
        print(f"Error reading token file {token_file}: {e}")
        return None

def calculate_next_refresh_time():
    """Calculate when to refresh based on token expiry (1 day before expiry)"""
    import os
    
    token_files = [
        'token_bd.json', 'token_bd_visit.json',
        'token_ind.json', 'token_ind_visit.json', 
        'token_br.json', 'token_br_visit.json'
    ]
    
    earliest_expiry = None
    
    for token_file in token_files:
        info = get_token_expiry_info(token_file)
        if info:
            if earliest_expiry is None or info['expiry_timestamp'] < earliest_expiry['expiry_timestamp']:
                earliest_expiry = info
    
    if earliest_expiry:
        # Schedule refresh 1 day before expiry
        refresh_time = datetime.fromtimestamp(earliest_expiry['expiry_timestamp']) - timedelta(days=1)
        return refresh_time, earliest_expiry
    
    return None, None

def refresh_visit_first_task():
    """Background task: Refresh VISIT tokens first, then regular tokens"""
    print(f"\n🕐 SMART REFRESH TRIGGERED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📋 Refreshing VISIT tokens first...")
    
    # First, cleanup expired tokens
    cleanup_all_expired_tokens()
    
    try:
        import sys
        import os
        
        # Add token_generator to path
        token_gen_path = os.path.join(os.path.dirname(__file__), 'token_generator')
        if token_gen_path not in sys.path:
            sys.path.insert(0, token_gen_path)
        
        from token_generator.token_gen import load_credentials_from_file, generate_token
        
        visit_file_creds = os.path.join(token_gen_path, 'visit.txt')
        credentials_file = os.path.join(token_gen_path, 'credentials.txt')
        
        total_success = 0
        total_failed = 0
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # ========== STEP 1: REFRESH VISIT TOKENS FIRST ==========
            if os.path.exists(visit_file_creds):
                print("\n✅ STEP 1: Processing visit.txt (FIRST)")
                visit_credentials = loop.run_until_complete(load_credentials_from_file(visit_file_creds))
                
                if visit_credentials:
                    visit_file = "token_bd_visit.json"
                    
                    # Delete old file
                    if os.path.exists(visit_file):
                        os.remove(visit_file)
                    
                    success_count = 0
                    for i, (uid, password) in enumerate(visit_credentials, 1):
                        try:
                            token_obj = loop.run_until_complete(generate_token(uid, password))
                            
                            if token_obj:
                                existing = []
                                try:
                                    with open(visit_file, 'r') as f:
                                        existing = json.load(f)
                                        if not isinstance(existing, list):
                                            existing = [existing]
                                except FileNotFoundError:
                                    pass
                                
                                existing.append(token_obj)
                                with open(visit_file, 'w') as f:
                                    json.dump(existing, f, indent=2)
                                
                                success_count += 1
                                print(f"  ✅ Visit token {i}/{len(visit_credentials)}")
                        except Exception as e:
                            print(f"  ❌ Visit token {i} failed: {str(e)[:50]}")
                        
                        if i < len(visit_credentials):
                            loop.run_until_complete(asyncio.sleep(2))
                    
                    total_success += success_count
                    print(f"✅ Visit tokens: {success_count}/{len(visit_credentials)} refreshed")
            
            # ========== STEP 2: REFRESH REGULAR TOKENS SECOND ==========
            if os.path.exists(credentials_file):
                print("\n📋 STEP 2: Processing credentials.txt (SECOND)")
                credentials = loop.run_until_complete(load_credentials_from_file(credentials_file))
                
                if credentials:
                    output_file = "token_bd.json"
                    
                    if os.path.exists(output_file):
                        os.remove(output_file)
                    
                    success_count = 0
                    for i, (uid, password) in enumerate(credentials, 1):
                        try:
                            token_obj = loop.run_until_complete(generate_token(uid, password))
                            
                            if token_obj:
                                existing = []
                                try:
                                    with open(output_file, 'r') as f:
                                        existing = json.load(f)
                                        if not isinstance(existing, list):
                                            existing = [existing]
                                except FileNotFoundError:
                                    pass
                                
                                existing.append(token_obj)
                                with open(output_file, 'w') as f:
                                    json.dump(existing, f, indent=2)
                                
                                success_count += 1
                                print(f"  ✅ Regular token {i}/{len(credentials)}")
                        except Exception as e:
                            print(f"  ❌ Regular token {i} failed: {str(e)[:50]}")
                        
                        if i < len(credentials):
                            loop.run_until_complete(asyncio.sleep(2))
                    
                    total_success += success_count
                    print(f"✅ Regular tokens: {success_count}/{len(credentials)} refreshed")
            
            # Get next refresh time
            next_refresh, expiry_info = calculate_next_refresh_time()
            
            print("\n" + "="*60)
            print("✅ REFRESH COMPLETE")
            print("="*60)
            if expiry_info:
                print(f"Next token expiry: {expiry_info['expiry_datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Days remaining: {expiry_info['days_remaining']}")
                if next_refresh:
                    print(f"Next refresh scheduled: {next_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return total_success
        
        finally:
            loop.close()
    
    except Exception as e:
        print(f"❌ Smart refresh failed: {e}")
        return 0

def refresh_tokens_task():
    """Background task to refresh tokens automatically"""
    print(f"\n🕐 AUTO REFRESH TRIGGERED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Call the refresh endpoint logic
        result = refresh_tokens_logic()
        print(f"✅ Auto refresh completed: {result.get('total_successful', 0)} successful")
        return result
    except Exception as e:
        print(f"❌ Auto refresh failed: {e}")
        return None

app = Flask(__name__)

# Initialize scheduler for automatic token refresh
scheduler = BackgroundScheduler()
scheduler.start()

# Get initial refresh time based on token expiry
next_refresh_time, expiry_info = calculate_next_refresh_time()

if next_refresh_time:
    print(f"\n🕐 Token expiry detected: {expiry_info['expiry_datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Scheduled refresh at: {next_refresh_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Schedule based on token expiry time
    scheduler.add_job(
        func=refresh_visit_first_task,
        trigger="date",
        run_date=next_refresh_time,
        id='expiry_based_refresh',
        name='Expiry-Based Token Refresh',
        replace_existing=True
    )
else:
    # Fallback: refresh every 24 hours if no tokens found
    print("⚠️  No tokens found. Scheduling fallback refresh every 24 hours...")
    scheduler.add_job(
        func=refresh_visit_first_task,
        trigger="interval",
        hours=24,
        id='fallback_refresh',
        name='Fallback Token Refresh',
        replace_existing=True
    )

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def home():
    """Serve the dashboard"""
    return render_template('index.html')

@app.route('/like', methods=['GET'])
def handle_requests():
    uid_param = request.args.get("uid")
    server_name_param = request.args.get("server_name", "").upper()
    use_random = request.args.get("random", "false").lower() == "true"

    if not uid_param or not server_name_param:
        return jsonify({"error": "UID and server_name are required"}), 400

    # Load visit token for profile checking
    visit_tokens = load_tokens(server_name_param, for_visit=True)
    if not visit_tokens:
        return jsonify({"error": f"No visit tokens loaded for server {server_name_param}."}), 500
    
    # Use the first visit token for profile check
    visit_token = visit_tokens[0] if visit_tokens else None
    
    # Load regular tokens for like sending
    all_available_tokens = load_tokens(server_name_param, for_visit=False)
    if not all_available_tokens:
        return jsonify({"error": f"No tokens loaded or token file invalid for server {server_name_param}."}), 500

    print(f"Total tokens available for {server_name_param}: {len(all_available_tokens)}")

    # Get the batch of tokens for like sending
    if use_random:
        tokens_for_like_sending = get_random_batch_tokens(server_name_param, all_available_tokens)
        print(f"Using RANDOM batch selection for {server_name_param}")
    else:
        tokens_for_like_sending = get_next_batch_tokens(server_name_param, all_available_tokens)
        print(f"Using ROTATING batch selection for {server_name_param}")
    
    encrypted_player_uid_for_profile = enc_profile_check_payload(uid_param)
    
    # Get likes BEFORE using visit token
    before_info = make_profile_check_request(encrypted_player_uid_for_profile, server_name_param, visit_token)
    before_like_count = 0
    
    if before_info and hasattr(before_info, 'AccountInfo'):
        before_like_count = int(before_info.AccountInfo.Likes)
    else:
        print(f"Could not reliably fetch 'before' profile info for UID {uid_param} on {server_name_param}.")

    print(f"UID {uid_param} ({server_name_param}): Likes before = {before_like_count}")

    # Determine the URL for sending likes
    if server_name_param == "IND":
        like_api_url = "https://client.ind.freefiremobile.com/LikeProfile"
    elif server_name_param in {"BR", "US", "SAC", "NA"}:
        like_api_url = "https://client.us.freefiremobile.com/LikeProfile"
    else:
        like_api_url = "https://clientbp.ggblueshark.com/LikeProfile"

    if tokens_for_like_sending:
        print(f"Using token batch for {server_name_param} (size {len(tokens_for_like_sending)}) to send likes.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(send_likes_with_token_batch(uid_param, server_name_param, like_api_url, tokens_for_like_sending))
        finally:
            loop.close()
    else:
        print(f"Skipping like sending for UID {uid_param} as no tokens available for like sending.")
        
    # Get likes AFTER using visit token
    after_info = make_profile_check_request(encrypted_player_uid_for_profile, server_name_param, visit_token)
    after_like_count = before_like_count
    actual_player_uid_from_profile = int(uid_param)
    player_nickname_from_profile = "N/A"

    if after_info and hasattr(after_info, 'AccountInfo'):
        after_like_count = int(after_info.AccountInfo.Likes)
        actual_player_uid_from_profile = int(after_info.AccountInfo.UID)
        if after_info.AccountInfo.PlayerNickname:
            player_nickname_from_profile = str(after_info.AccountInfo.PlayerNickname)
        else:
            player_nickname_from_profile = "N/A"
    else:
        print(f"Could not reliably fetch 'after' profile info for UID {uid_param} on {server_name_param}.")

    print(f"UID {uid_param} ({server_name_param}): Likes after = {after_like_count}")

    likes_increment = after_like_count - before_like_count
    request_status = 1 if likes_increment > 0 else (2 if likes_increment == 0 else 3)

    response_data = {
        "LikesGivenByAPI": likes_increment,
        "LikesafterCommand": after_like_count,
        "LikesbeforeCommand": before_like_count,
        "PlayerNickname": player_nickname_from_profile,
        "UID": actual_player_uid_from_profile,
        "status": request_status,
        "Note": f"Used visit token for profile check and {'random' if use_random else 'rotating'} batch of {len(tokens_for_like_sending)} tokens for like sending."
    }
    return jsonify(response_data)

@app.route('/token_info', methods=['GET'])
def token_info():
    """Endpoint to check token counts for each server"""
    servers = ["IND", "BD", "BR", "US", "SAC", "NA"]
    info = {}
    
    for server in servers:
        regular_tokens = load_tokens(server, for_visit=False)
        visit_tokens = load_tokens(server, for_visit=True)
        info[server] = {
            "regular_tokens": len(regular_tokens),
            "visit_tokens": len(visit_tokens)
        }
    
    return jsonify(info)

@app.route('/scheduler_status', methods=['GET'])
def scheduler_status():
    """Check scheduler status and next run time"""
    from datetime import datetime, timezone
    
    jobs = scheduler.get_jobs()
    job_info = []
    
    for job in jobs:
        next_run = None
        time_remaining = None
        
        if job.next_run_time:
            # Convert to local time and format nicely
            next_run_dt = job.next_run_time
            if next_run_dt.tzinfo is not None:
                next_run_dt = next_run_dt.replace(tzinfo=None)
            
            next_run = next_run_dt.strftime('%B %d, %Y at %I:%M:%S %p')
            
            # Calculate time remaining
            now = datetime.now()
            time_diff = next_run_dt - now
            
            if time_diff.total_seconds() > 0:
                hours = int(time_diff.total_seconds() // 3600)
                minutes = int((time_diff.total_seconds() % 3600) // 60)
                seconds = int(time_diff.total_seconds() % 60)
                
                if hours > 0:
                    time_remaining = f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    time_remaining = f"{minutes}m {seconds}s"
                else:
                    time_remaining = f"{seconds}s"
            else:
                time_remaining = "Running now..."
        
        job_info.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": next_run if next_run else "Not scheduled",
            "time_remaining": time_remaining if time_remaining else "N/A"
        })
    
    return jsonify({
        "status": "🟢 Running" if scheduler.running else "🔴 Stopped",
        "current_time": datetime.now().strftime('%B %d, %Y at %I:%M:%S %p'),
        "total_jobs": len(jobs),
        "jobs": job_info
    })

@app.route('/token_details', methods=['GET'])
def token_details():
    """Endpoint to get detailed token information"""
    try:
        import base64
        from datetime import datetime
        
        server_name = request.args.get("server", "BD").upper()
        
        # Load tokens
        regular_tokens = load_tokens(server_name, for_visit=False)
        visit_tokens = load_tokens(server_name, for_visit=True)
        
        def decode_jwt_payload(token_str):
            """Decode JWT token payload without verification"""
            try:
                parts = token_str.split('.')
                if len(parts) != 3:
                    return None
                
                # Decode payload (second part)
                payload = parts[1]
                # Add padding if needed
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                
                decoded = base64.urlsafe_b64decode(payload)
                return json.loads(decoded)
            except Exception as e:
                print(f"Error decoding token: {e}")
                return None
        
        def parse_token_info(token_dict):
            """Extract information from token"""
            token_str = token_dict.get("token", "")
            payload = decode_jwt_payload(token_str)
            
            if not payload:
                return {
                    "token": token_str,
                    "account_id": None,
                    "nickname": None,
                    "region": None,
                    "external_uid": None,
                    "expiry_date": None,
                    "is_expired": None,
                    "days_until_expiry": None
                }
            
            # Extract info
            account_id = payload.get("account_id")
            nickname = payload.get("nickname")
            region = payload.get("noti_region") or payload.get("lock_region")
            external_uid = payload.get("external_uid")
            exp_timestamp = payload.get("exp")
            
            # Calculate expiry
            is_expired = False
            expiry_date = None
            days_until_expiry = None
            
            if exp_timestamp:
                expiry_dt = datetime.fromtimestamp(exp_timestamp)
                expiry_date = expiry_dt.strftime("%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                is_expired = now > expiry_dt
                
                if not is_expired:
                    days_until_expiry = (expiry_dt - now).days
            
            return {
                "token": token_str,
                "account_id": account_id,
                "nickname": nickname,
                "region": region,
                "external_uid": external_uid,
                "expiry_date": expiry_date,
                "is_expired": is_expired,
                "days_until_expiry": days_until_expiry
            }
        
        # Parse all tokens
        parsed_regular = [parse_token_info(t) for t in regular_tokens]
        parsed_visit = [parse_token_info(t) for t in visit_tokens]
        
        return jsonify({
            "status": "success",
            "server": server_name,
            "total_tokens": len(regular_tokens),
            "total_visit_tokens": len(visit_tokens),
            "tokens": parsed_regular,
            "visit_tokens": parsed_visit
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def refresh_tokens_task():
    """Background task to refresh tokens automatically"""
    print(f"\n🕐 AUTO REFRESH TRIGGERED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Call the refresh endpoint logic
        result = refresh_tokens_logic()
        print(f"✅ Auto refresh completed: {result.get('total_successful', 0)} successful")
        return result
    except Exception as e:
        print(f"❌ Auto refresh failed: {e}")
        return None

def refresh_tokens_logic():
    """Core logic for token refresh (used by both endpoint and scheduler)"""
    try:
        import sys
        import os
        
        # Add token_generator to path
        token_gen_path = os.path.join(os.path.dirname(__file__), 'token_generator')
        if token_gen_path not in sys.path:
            sys.path.insert(0, token_gen_path)
        
        # Import token generation functions
        from token_generator.token_gen import load_credentials_from_file, generate_token
        
        # Check credential files
        credentials_file = os.path.join(token_gen_path, 'credentials.txt')
        visit_file_creds = os.path.join(token_gen_path, 'visit.txt')
        
        has_credentials = os.path.exists(credentials_file)
        has_visit = os.path.exists(visit_file_creds)
        
        if not has_credentials and not has_visit:
            return jsonify({
                "status": "error",
                "message": "No credential files found. Create credentials.txt or visit.txt in token_generator folder"
            }), 404
        
        print("\n" + "="*60)
        print("🔄 TOKEN REFRESH API TRIGGERED")
        print("="*60)
        
        # Define output file paths
        output_file = "token_bd.json"
        visit_file = "token_bd_visit.json"
        
        total_success = 0
        total_failed = 0
        all_failed_accounts = []
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # ========== PROCESS REGULAR TOKENS ==========
            if has_credentials:
                print("\n📋 Processing credentials.txt...")
                credentials = loop.run_until_complete(load_credentials_from_file(credentials_file))
                
                if credentials:
                    print(f"Found {len(credentials)} accounts in credentials.txt")
                    
                    # Delete old file
                    if os.path.exists(output_file):
                        os.remove(output_file)
                        print(f"Deleted old {output_file}")
                    
                    success_count = 0
                    failed_accounts = []
                    
                    for i, (uid, password) in enumerate(credentials, 1):
                        print(f"[{i}/{len(credentials)}] Processing UID: {uid}")
                        
                        try:
                            token_obj = loop.run_until_complete(generate_token(uid, password))
                            
                            if token_obj:
                                existing_tokens = []
                                try:
                                    with open(output_file, 'r') as f:
                                        existing_tokens = json.load(f)
                                        if not isinstance(existing_tokens, list):
                                            existing_tokens = [existing_tokens]
                                except FileNotFoundError:
                                    pass
                                
                                existing_tokens.append(token_obj)
                                
                                with open(output_file, 'w') as f:
                                    json.dump(existing_tokens, f, indent=2)
                                
                                success_count += 1
                                print(f"✅ Token saved ({success_count}/{len(credentials)})")
                            else:
                                failed_accounts.append((uid, "Generation failed"))
                        
                        except Exception as e:
                            print(f"❌ Error: {str(e)[:100]}")
                            failed_accounts.append((uid, str(e)[:50]))
                        
                        if i < len(credentials):
                            loop.run_until_complete(asyncio.sleep(2))
                    
                    total_success += success_count
                    total_failed += len(failed_accounts)
                    all_failed_accounts.extend([{"uid": uid, "reason": reason, "file": "credentials.txt"} for uid, reason in failed_accounts])
                    
                    print(f"✅ Regular tokens: {success_count}/{len(credentials)} successful")
            
            # ========== PROCESS VISIT TOKENS ==========
            if has_visit:
                print("\n📋 Processing visit.txt...")
                visit_credentials = loop.run_until_complete(load_credentials_from_file(visit_file_creds))
                
                if visit_credentials:
                    print(f"Found {len(visit_credentials)} accounts in visit.txt")
                    
                    # Delete old file
                    if os.path.exists(visit_file):
                        os.remove(visit_file)
                        print(f"Deleted old {visit_file}")
                    
                    visit_success_count = 0
                    visit_failed_accounts = []
                    
                    for i, (uid, password) in enumerate(visit_credentials, 1):
                        print(f"[{i}/{len(visit_credentials)}] Processing UID: {uid}")
                        
                        try:
                            token_obj = loop.run_until_complete(generate_token(uid, password))
                            
                            if token_obj:
                                existing_tokens = []
                                try:
                                    with open(visit_file, 'r') as f:
                                        existing_tokens = json.load(f)
                                        if not isinstance(existing_tokens, list):
                                            existing_tokens = [existing_tokens]
                                except FileNotFoundError:
                                    pass
                                
                                existing_tokens.append(token_obj)
                                
                                with open(visit_file, 'w') as f:
                                    json.dump(existing_tokens, f, indent=2)
                                
                                visit_success_count += 1
                                print(f"✅ Visit token saved ({visit_success_count}/{len(visit_credentials)})")
                            else:
                                visit_failed_accounts.append((uid, "Generation failed"))
                        
                        except Exception as e:
                            print(f"❌ Error: {str(e)[:100]}")
                            visit_failed_accounts.append((uid, str(e)[:50]))
                        
                        if i < len(visit_credentials):
                            loop.run_until_complete(asyncio.sleep(2))
                    
                    total_success += visit_success_count
                    total_failed += len(visit_failed_accounts)
                    all_failed_accounts.extend([{"uid": uid, "reason": reason, "file": "visit.txt"} for uid, reason in visit_failed_accounts])
                    
                    print(f"✅ Visit tokens: {visit_success_count}/{len(visit_credentials)} successful")
        
        finally:
            loop.close()
        
        print("\n" + "="*60)
        print("✅ TOKEN REFRESH COMPLETE")
        print("="*60)
        
        return {
            "status": "success",
            "message": "Tokens refreshed successfully",
            "total_successful": total_success,
            "total_failed": total_failed,
            "failed_accounts": all_failed_accounts,
            "files_processed": {
                "credentials.txt": has_credentials,
                "visit.txt": has_visit
            },
            "output_files": {
                "regular_tokens": output_file if has_credentials else None,
                "visit_tokens": visit_file if has_visit else None
            },
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except Exception as e:
        print(f"\n❌ Token refresh error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

@app.route('/refresh_tokens', methods=['POST', 'GET'])
def refresh_tokens():
    """Endpoint to refresh tokens - VISIT first, then REGULAR"""
    print("\n📡 API: /refresh_tokens triggered")
    success = refresh_visit_first_task()
    
    return jsonify({
        "status": "success" if success > 0 else "completed",
        "message": f"Refreshed {success} tokens (visit first, then regular)",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/next_refresh_info', methods=['GET'])
def next_refresh_info():
    """Get info about next scheduled token refresh"""
    next_refresh_time, expiry_info = calculate_next_refresh_time()
    
    if not expiry_info:
        return jsonify({
            "status": "no_tokens",
            "message": "No tokens found in system",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        "status": "scheduled",
        "token_expiry": expiry_info['expiry_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
        "days_remaining": expiry_info['days_remaining'],
        "account_id": str(expiry_info['account_id']),
        "nickname": expiry_info['nickname'],
        "next_refresh_time": next_refresh_time.strftime('%Y-%m-%d %H:%M:%S') if next_refresh_time else None,
        "refresh_strategy": "Visit tokens first, then regular tokens",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/token_health', methods=['GET'])
def token_health():
    """Get health status of all tokens"""
    summary = get_token_health_summary()
    
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "tokens": summary
    })

@app.route('/cleanup_tokens', methods=['POST', 'GET'])
def cleanup_tokens():
    """Manually cleanup expired tokens"""
    print("\n📡 API: /cleanup_tokens triggered")
    valid, expired = cleanup_all_expired_tokens()
    
    return jsonify({
        "status": "success",
        "message": f"Cleanup complete: {expired} expired removed, {valid} valid kept",
        "valid_tokens": valid,
        "expired_tokens_removed": expired,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
