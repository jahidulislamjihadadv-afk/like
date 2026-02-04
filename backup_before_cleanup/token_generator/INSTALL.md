# Installation & Setup Guide

## 🎯 Quick Install (5 Minutes)

### Windows

```cmd
cd token_generator
pip install -r requirements.txt
python token_gen.py 4437768628 JOBAYAR_CODX-IPP3PKDJB
```

### Linux/Mac

```bash
cd token_generator
pip3 install -r requirements.txt
python3 token_gen.py 4437768628 JOBAYAR_CODX-IPP3PKDJB
```

## 📋 Prerequisites

### 1. Python 3.7+

**Check if installed:**
```bash
python --version
# or
python3 --version
```

**Install if needed:**
- Windows: https://python.org/downloads
- Linux: `sudo apt install python3 python3-pip`
- Mac: `brew install python3`

### 2. pip (Python Package Manager)

Usually comes with Python. Check:
```bash
pip --version
# or
pip3 --version
```

## 📦 Install Dependencies

### Method 1: Automatic (Recommended)

```bash
cd token_generator
pip install -r requirements.txt
```

### Method 2: Manual

```bash
pip install requests
pip install aiohttp
pip install pycryptodome
pip install protobuf
pip install urllib3
```

### Verify Installation

```bash
python -c "import requests, aiohttp; print('✅ All dependencies installed')"
```

## 🚀 First Run

### Test with Single Account

```bash
# Windows
python token_gen.py 4437768628 JOBAYAR_CODX-IPP3PKDJB

# Linux/Mac
python3 token_gen.py 4437768628 JOBAYAR_CODX-IPP3PKDJB
```

**Expected output:**
```
============================================================
🎯 FREE FIRE TOKEN GENERATOR
============================================================
📝 UID: 4437768628
🔑 Password: JOBAYAR_CODX-IPP3PKDJB
============================================================

📡 Requesting access token for UID: 4437768628...
✅ Access token obtained
🔐 Performing MajorLogin...
✅ MajorLogin successful
✅ JWT Token extracted
📍 Region: BD
👤 Account UID: 4437768628

============================================================
✅ TOKEN GENERATED SUCCESSFULLY!
============================================================
```

## 🔧 Batch Setup

### Step 1: Prepare Credentials File

Edit `credentials.txt`:
```
4437768628,JOBAYAR_CODX-IPP3PKDJB
4437769139,JOBAYAR_CODX-IYMKLOVER
4437769273,JOBAYAR_CODX-2AJDB0KJC
4437769404,JOBAYAR_CODX-NSE70CLK3
4437769524,JOBAYAR_CODX-PBXLQEZIK
```

### Step 2: Run Batch Generation

**Windows:**
```cmd
generate_all.bat
```

**Linux/Mac:**
```bash
chmod +x generate_all.sh
./generate_all.sh
```

**Or manually:**
```bash
python token_gen.py --batch
```

## 📊 Verify Tokens

### Test Generated Tokens

```bash
python test_token.py
```

**Expected output:**
```
============================================================
🧪 TESTING 5 TOKEN(S)
============================================================

Token 1/5
------------------------------------------------------------
📍 Region: BD
👤 UID: 4437768628
⏰ Generated: 2026-01-30 16:45:23

🔍 Decoding JWT token...
✅ Token is valid!

📋 Token Contents:
   Account ID: 14129446252
   Nickname: GHOST_MOD2UN
   Region: BD
   External UID: 4437768628
   Platform: 1 (1=Android)
   Client Version: 1.120.2
   Is Emulator: True
   Country: BD

⏳ Token Expiration:
   Expires: 2026-02-28 16:45:23
   Remaining: 29 days, 0 hours
   Status: ✅ VALID
```

## 🎯 Usage Examples

### Load Token in Python

```python
import json

# Load first token
with open('generated_tokens.json', 'r') as f:
    tokens = json.load(f)
    token = tokens[0]['token']
    region = tokens[0]['region']

print(f"Token: {token[:50]}...")
print(f"Region: {region}")
```

### Use Token in API Request

```python
import requests

headers = {
    "Authorization": f"Bearer {token}",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA": "v1 1",
    "ReleaseVersion": "OB52",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Dalvik/2.1.0"
}

response = requests.post(
    "https://client.bd.freefiremobile.com/GetPlayerPersonalShow",
    headers=headers,
    data=encrypted_data
)
```

## 🐛 Troubleshooting

### Issue: "Cannot import MajoRLoGinrEq_pb2"

**Solution:** Run from project root directory:
```bash
cd /path/to/your/project
python token_generator/token_gen.py <uid> <password>
```

### Issue: "ModuleNotFoundError: No module named 'requests'"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "Failed at Step 1: Could not get access token"

**Possible causes:**
1. Wrong UID or password
2. No internet connection
3. Garena servers down

**Solution:**
- Verify credentials are correct
- Check internet connection
- Try again in a few minutes

### Issue: "Failed at Step 3: MajorLogin request failed"

**Possible causes:**
1. Account is banned
2. Invalid password
3. Server maintenance

**Solution:**
- Try a different account
- Verify password is correct
- Check Free Fire server status

### Issue: Token expired

**Solution:** Generate new token:
```bash
python token_gen.py <uid> <password>
```

## 📁 File Structure After Installation

```
token_generator/
├── token_gen.py              ✅ Main script
├── test_token.py             ✅ Testing tool
├── example_usage.py          ✅ Usage examples
├── requirements.txt          ✅ Dependencies
├── credentials.txt           📝 Your accounts
├── test_credentials.txt      📝 Test accounts
├── generated_tokens.json     📦 Generated tokens (auto-created)
├── README.md                 📖 Full documentation
├── QUICKSTART.md             📖 Quick guide
├── SUMMARY.md                📖 Project summary
├── INSTALL.md                📖 This file
├── generate_all.bat          🚀 Windows batch script
└── generate_all.sh           🚀 Linux/Mac script
```

## ✅ Verification Checklist

After installation, verify:

- [ ] Python 3.7+ installed
- [ ] pip installed
- [ ] Dependencies installed (`pip list | grep requests`)
- [ ] Can run `python token_gen.py --help`
- [ ] Generated at least one token
- [ ] `generated_tokens.json` exists
- [ ] Token test passes (`python test_token.py`)
- [ ] Token is not expired

## 🎓 Next Steps

1. ✅ Generate tokens for all your accounts
2. ✅ Test tokens with `test_token.py`
3. ✅ Try example usage with `example_usage.py`
4. ✅ Integrate tokens into your project
5. ✅ Set up automated token refresh (optional)

## 📞 Support

If you still have issues:

1. Check `README.md` for detailed documentation
2. Check `QUICKSTART.md` for quick examples
3. Check `SUMMARY.md` for project overview
4. Verify all prerequisites are met
5. Try with a fresh Python environment

## 🔒 Security Reminder

- ✅ Never share your tokens
- ✅ Don't commit `generated_tokens.json` to git
- ✅ Don't commit `credentials.txt` to git
- ✅ Tokens expire - regenerate as needed
- ✅ Use HTTPS only for API requests

## 📊 Performance

- Single token: ~2-3 seconds
- Batch (5 tokens): ~15-20 seconds
- Network dependent
- No rate limiting on token generation

---

**Installation Complete!** 🎉

You're ready to generate Free Fire tokens without emotes or bundles!
