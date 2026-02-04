#!/usr/bin/env python3
"""
Test script to verify token generation and usage
"""

import json
import jwt
import sys

def decode_jwt_token(token):
    """Decode JWT token without verification"""
    try:
        # Split token into parts
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        # Decode payload (second part)
        import base64
        payload = parts[1]
        
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        # Decode base64
        decoded = base64.urlsafe_b64decode(payload)
        
        # Parse JSON
        data = json.loads(decoded)
        return data
    except Exception as e:
        print(f"❌ Error decoding token: {e}")
        return None

def test_token_file(filename="generated_tokens.json"):
    """Test tokens from generated file"""
    try:
        with open(filename, 'r') as f:
            tokens = json.load(f)
        
        if not isinstance(tokens, list):
            tokens = [tokens]
        
        print(f"\n{'='*60}")
        print(f"🧪 TESTING {len(tokens)} TOKEN(S)")
        print(f"{'='*60}\n")
        
        for i, token_data in enumerate(tokens, 1):
            print(f"Token {i}/{len(tokens)}")
            print("-" * 60)
            
            # Basic info
            print(f"📍 Region: {token_data.get('region', 'N/A')}")
            print(f"👤 UID: {token_data.get('bot_uid', 'N/A')}")
            print(f"⏰ Generated: {token_data.get('timestamp', 'N/A')}")
            
            # Decode JWT
            token = token_data.get('token')
            if token:
                print(f"\n🔍 Decoding JWT token...")
                payload = decode_jwt_token(token)
                
                if payload:
                    print(f"✅ Token is valid!")
                    print(f"\n📋 Token Contents:")
                    print(f"   Account ID: {payload.get('account_id', 'N/A')}")
                    print(f"   Nickname: {payload.get('nickname', 'N/A')}")
                    print(f"   Region: {payload.get('noti_region', 'N/A')}")
                    print(f"   External UID: {payload.get('external_uid', 'N/A')}")
                    print(f"   Platform: {payload.get('plat_id', 'N/A')} (1=Android)")
                    print(f"   Client Version: {payload.get('client_version', 'N/A')}")
                    print(f"   Is Emulator: {payload.get('is_emulator', 'N/A')}")
                    print(f"   Country: {payload.get('country_code', 'N/A')}")
                    
                    # Check expiration
                    exp = payload.get('exp')
                    if exp:
                        import time
                        from datetime import datetime
                        
                        exp_time = datetime.fromtimestamp(exp)
                        now = datetime.now()
                        
                        if now < exp_time:
                            remaining = exp_time - now
                            days = remaining.days
                            hours = remaining.seconds // 3600
                            print(f"\n⏳ Token Expiration:")
                            print(f"   Expires: {exp_time.strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"   Remaining: {days} days, {hours} hours")
                            print(f"   Status: ✅ VALID")
                        else:
                            print(f"\n⏳ Token Expiration:")
                            print(f"   Expired: {exp_time.strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"   Status: ❌ EXPIRED")
                else:
                    print(f"❌ Failed to decode token")
            else:
                print(f"❌ No token found in data")
            
            print("\n")
        
        print(f"{'='*60}")
        print(f"✅ Test complete!")
        print(f"{'='*60}\n")
        
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        print(f"💡 Generate tokens first using: python token_gen.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_single_token(token_string):
    """Test a single token string"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING SINGLE TOKEN")
    print(f"{'='*60}\n")
    
    print(f"🔍 Decoding JWT token...")
    payload = decode_jwt_token(token_string)
    
    if payload:
        print(f"✅ Token is valid!")
        print(f"\n📋 Token Contents:")
        for key, value in payload.items():
            print(f"   {key}: {value}")
    else:
        print(f"❌ Failed to decode token")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test single token from command line
        test_single_token(sys.argv[1])
    else:
        # Test tokens from file
        test_token_file()
