#!/usr/bin/env python3
"""
Interactive menu for token generator
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
    print("🎯 FREE FIRE TOKEN GENERATOR - INTERACTIVE MENU")
    print("="*60)

def print_menu():
    """Print main menu"""
    print("\n📋 MAIN MENU:")
    print("  1. Generate single token")
    print("  2. Generate batch tokens (from credentials.txt)")
    print("  3. Test generated tokens")
    print("  4. View token info")
    print("  5. Example API usage")
    print("  6. Help & Documentation")
    print("  0. Exit")
    print("\n" + "="*60)

async def option_single_token():
    """Option 1: Generate single token"""
    clear_screen()
    print_header()
    print("\n📝 SINGLE TOKEN GENERATION\n")
    
    uid = input("Enter UID: ").strip()
    password = input("Enter Password: ").strip()
    
    if not uid or not password:
        print("\n❌ UID and password are required!")
        input("\nPress Enter to continue...")
        return
    
    print("\n🔄 Generating token...")
    
    # Import and run token generator
    from token_gen import generate_token, save_token
    
    token_data = await generate_token(uid, password)
    if token_data:
        await save_token(token_data)
        print("\n✅ Token generated and saved!")
    else:
        print("\n❌ Token generation failed!")
    
    input("\nPress Enter to continue...")

async def option_batch_tokens():
    """Option 2: Generate batch tokens"""
    clear_screen()
    print_header()
    print("\n📦 BATCH TOKEN GENERATION\n")
    
    # Check if credentials.txt exists
    if not os.path.exists("credentials.txt"):
        print("❌ credentials.txt not found!")
        print("\n💡 Create credentials.txt with format:")
        print("   uid,password")
        print("   one per line")
        input("\nPress Enter to continue...")
        return
    
    # Count lines
    with open("credentials.txt", 'r') as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    
    print(f"📋 Found {len(lines)} accounts in credentials.txt")
    confirm = input("\nGenerate tokens for all accounts? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Cancelled")
        input("\nPress Enter to continue...")
        return
    
    print("\n🔄 Generating tokens...\n")
    
    # Run batch generation
    os.system(f"{sys.executable} token_gen.py --batch")
    
    input("\nPress Enter to continue...")

def option_test_tokens():
    """Option 3: Test generated tokens"""
    clear_screen()
    print_header()
    print("\n🧪 TEST GENERATED TOKENS\n")
    
    if not os.path.exists("generated_tokens.json"):
        print("❌ No tokens found!")
        print("💡 Generate tokens first (option 1 or 2)")
        input("\nPress Enter to continue...")
        return
    
    print("🔄 Testing tokens...\n")
    os.system(f"{sys.executable} test_token.py")
    
    input("\nPress Enter to continue...")

def option_view_tokens():
    """Option 4: View token info"""
    clear_screen()
    print_header()
    print("\n📊 TOKEN INFORMATION\n")
    
    try:
        with open("generated_tokens.json", 'r') as f:
            tokens = json.load(f)
        
        if not isinstance(tokens, list):
            tokens = [tokens]
        
        print(f"📦 Total tokens: {len(tokens)}\n")
        
        for i, token_data in enumerate(tokens, 1):
            print(f"Token {i}:")
            print(f"  👤 UID: {token_data.get('bot_uid', 'N/A')}")
            print(f"  📍 Region: {token_data.get('region', 'N/A')}")
            print(f"  ⏰ Generated: {token_data.get('timestamp', 'N/A')}")
            print(f"  🎫 Token: {token_data.get('token', '')[:50]}...")
            print()
        
    except FileNotFoundError:
        print("❌ No tokens found!")
        print("💡 Generate tokens first (option 1 or 2)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    input("\nPress Enter to continue...")

def option_example_usage():
    """Option 5: Example API usage"""
    clear_screen()
    print_header()
    print("\n🎯 EXAMPLE API USAGE\n")
    
    if not os.path.exists("generated_tokens.json"):
        print("❌ No tokens found!")
        print("💡 Generate tokens first (option 1 or 2)")
        input("\nPress Enter to continue...")
        return
    
    print("🔄 Running examples...\n")
    os.system(f"{sys.executable} example_usage.py")
    
    input("\nPress Enter to continue...")

def option_help():
    """Option 6: Help & Documentation"""
    clear_screen()
    print_header()
    print("\n📚 HELP & DOCUMENTATION\n")
    
    print("📖 Available Documentation:")
    print("  1. README.md - Full documentation")
    print("  2. QUICKSTART.md - Quick start guide")
    print("  3. INSTALL.md - Installation guide")
    print("  4. SUMMARY.md - Project summary")
    print()
    
    print("🔗 Quick Links:")
    print("  • Single token: python token_gen.py <uid> <password>")
    print("  • Batch tokens: python token_gen.py --batch")
    print("  • Test tokens:  python test_token.py")
    print("  • Examples:     python example_usage.py")
    print()
    
    print("💡 Tips:")
    print("  • Tokens expire after some time")
    print("  • Never share your tokens")
    print("  • Store tokens securely")
    print("  • Use HTTPS for API requests")
    print()
    
    choice = input("Open README.md? (y/n): ").strip().lower()
    if choice == 'y':
        if os.name == 'nt':
            os.system("type README.md | more")
        else:
            os.system("less README.md")
    
    input("\nPress Enter to continue...")

async def main():
    """Main menu loop"""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("Select option (0-6): ").strip()
        
        if choice == '0':
            clear_screen()
            print("\n👋 Goodbye!\n")
            break
        elif choice == '1':
            await option_single_token()
        elif choice == '2':
            await option_batch_tokens()
        elif choice == '3':
            option_test_tokens()
        elif choice == '4':
            option_view_tokens()
        elif choice == '5':
            option_example_usage()
        elif choice == '6':
            option_help()
        else:
            print("\n❌ Invalid option!")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
