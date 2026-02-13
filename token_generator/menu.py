#!/usr/bin/env python3
"""
Automatic batch token generator
Generates tokens for all accounts in credentials.txt
"""

import os
import sys
import asyncio
import json

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print menu header"""
    print("\n" + "="*60)
    print("🎯 FREE FIRE TOKEN GENERATOR - AUTO BATCH MODE")
    print("="*60)

async def auto_batch_generate():
    """Automatically generate tokens for all credentials"""
    clear_screen()
    print_header()
    print("\n🚀 AUTOMATIC BATCH TOKEN GENERATION\n")
    
    # Check if credentials files exist
    visit_file_creds = "visit.txt"
    credentials_file = "credentials.txt"
    
    
    has_credentials = os.path.exists(credentials_file)
    has_visit = os.path.exists(visit_file_creds)
    
    if not has_credentials and not has_visit:
        print("❌ No credential files found!")
        print("\n💡 Create at least one of these files:")
        print("   - credentials.txt (for regular tokens)")
        print("   - visit.txt (for visit tokens)")
        print("   Format: uid,password (one per line)")
        input("\nPress Enter to exit...")
        return
    
    # Load credentials
    from token_gen import load_credentials_from_file, generate_token
    
    # Define output file paths (parent directory)
    visit_file = os.path.join("..", "token_bd_visit.json")
    output_file = os.path.join("..", "token_bd.json")
    
        # ========== PROCESS VISIT TOKENS (visit.txt) ==========
    if has_visit:
        print("\n\n" + "="*60)
        print("📋 PROCESSING VISIT TOKENS (visit.txt)")
        print("="*60)
        
        visit_credentials = await load_credentials_from_file(visit_file_creds)
        
        if visit_credentials:
            print(f"📋 Found {len(visit_credentials)} accounts in visit.txt")
            
            # Delete old visit tokens file
            if os.path.exists(visit_file):
                print(f"\n🗑️  Deleting old visit tokens from {visit_file}...")
                os.remove(visit_file)
                print("✅ Old visit tokens deleted")
            
            print("\n🔄 Generating visit tokens...\n")
            print("="*60)
            
            visit_success_count = 0
            visit_failed_accounts = []
            
            for i, (uid, password) in enumerate(visit_credentials, 1):
                print(f"\n[{i}/{len(visit_credentials)}] Processing UID: {uid}")
                print("-"*60)
                
                try:
                    token_obj = await generate_token(uid, password)
                    
                    if token_obj:
                        try:
                            # Load existing visit tokens
                            existing_tokens = []
                            try:
                                with open(visit_file, 'r') as f:
                                    existing_tokens = json.load(f)
                                    if not isinstance(existing_tokens, list):
                                        existing_tokens = [existing_tokens]
                            except FileNotFoundError:
                                pass
                            
                            # Add new token
                            existing_tokens.append(token_obj)
                            
                            # Save to file
                            with open(visit_file, 'w') as f:
                                json.dump(existing_tokens, f, indent=2)
                            
                            visit_success_count += 1
                            print(f"✅ Visit token saved to {visit_file}")
                            print(f"📊 Progress: {visit_success_count}/{len(visit_credentials)} tokens")
                            
                        except Exception as e:
                            print(f"❌ Error saving token: {e}")
                            visit_failed_accounts.append((uid, "Save error"))
                    else:
                        print(f"❌ Token generation failed")
                        visit_failed_accounts.append((uid, "Generation failed"))
                
                except Exception as e:
                    print(f"❌ Error: {str(e)[:100]}")
                    visit_failed_accounts.append((uid, str(e)[:50]))
                
                # Small delay between requests
                if i < len(visit_credentials):
                    await asyncio.sleep(2)
            
            # Summary for visit tokens
            print("\n" + "="*60)
            print("📊 VISIT TOKENS GENERATION COMPLETE")
            print("="*60)
            print(f"✅ Success: {visit_success_count}/{len(visit_credentials)} tokens")
            print(f"❌ Failed: {len(visit_failed_accounts)}/{len(visit_credentials)} accounts")
            
            if visit_failed_accounts:
                print("\n⚠️  Failed Accounts:")
                for uid, reason in visit_failed_accounts:
                    print(f"  • {uid}: {reason}")
            
            print(f"\n💾 Visit tokens saved to: {visit_file}")
        else:
            print("⚠️  No valid credentials found in visit.txt")
    else:
        print("\n⚠️  visit.txt not found, skipping visit tokens")
    
    
    # ========== PROCESS REGULAR TOKENS (credentials.txt) ==========
    if has_credentials:
        print("="*60)
        print("📋 PROCESSING REGULAR TOKENS (credentials.txt)")
        print("="*60)
        
        credentials = await load_credentials_from_file(credentials_file)
        
        if credentials:
            print(f"📋 Found {len(credentials)} accounts in credentials.txt")
            
            # Delete old regular tokens file
            if os.path.exists(output_file):
                print(f"\n🗑️  Deleting old tokens from {output_file}...")
                os.remove(output_file)
                print("✅ Old tokens deleted")
            
            print("\n🔄 Generating regular tokens...\n")
            print("="*60)
            
            success_count = 0
            failed_accounts = []
            
            for i, (uid, password) in enumerate(credentials, 1):
                print(f"\n[{i}/{len(credentials)}] Processing UID: {uid}")
                print("-"*60)
                
                try:
                    token_obj = await generate_token(uid, password)
                    
                    if token_obj:
                        try:
                            # Load existing tokens
                            existing_tokens = []
                            try:
                                with open(output_file, 'r') as f:
                                    existing_tokens = json.load(f)
                                    if not isinstance(existing_tokens, list):
                                        existing_tokens = [existing_tokens]
                            except FileNotFoundError:
                                pass
                            
                            # Add new token
                            existing_tokens.append(token_obj)
                            
                            # Save to file
                            with open(output_file, 'w') as f:
                                json.dump(existing_tokens, f, indent=2)
                            
                            success_count += 1
                            print(f"✅ Token saved to {output_file}")
                            print(f"📊 Progress: {success_count}/{len(credentials)} tokens")
                            
                        except Exception as e:
                            print(f"❌ Error saving token: {e}")
                            failed_accounts.append((uid, "Save error"))
                    else:
                        print(f"❌ Token generation failed")
                        failed_accounts.append((uid, "Generation failed"))
                
                except Exception as e:
                    print(f"❌ Error: {str(e)[:100]}")
                    failed_accounts.append((uid, str(e)[:50]))
                
                # Small delay between requests
                if i < len(credentials):
                    await asyncio.sleep(2)
            
            # Summary for regular tokens
            print("\n" + "="*60)
            print("📊 REGULAR TOKENS GENERATION COMPLETE")
            print("="*60)
            print(f"✅ Success: {success_count}/{len(credentials)} tokens")
            print(f"❌ Failed: {len(failed_accounts)}/{len(credentials)} accounts")
            
            if failed_accounts:
                print("\n⚠️  Failed Accounts:")
                for uid, reason in failed_accounts:
                    print(f"  • {uid}: {reason}")
            
            print(f"\n💾 Regular tokens saved to: {output_file}")
        else:
            print("⚠️  No valid credentials found in credentials.txt")
    else:
        print("⚠️  credentials.txt not found, skipping regular tokens")
    

    # Final summary
    print("\n\n" + "="*60)
    print("🎉 ALL TOKEN GENERATION COMPLETE!")
    print("="*60)
    
    input("\nPress Enter to exit...")

async def main():
    """Main entry point - auto batch mode"""
    try:
        await auto_batch_generate()
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted!")
        print("👋 Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
    
