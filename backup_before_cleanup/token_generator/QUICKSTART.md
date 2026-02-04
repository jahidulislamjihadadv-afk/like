# Quick Start Guide - Token Generator

## 🚀 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd token_generator
pip install -r requirements.txt
```

### Step 2: Single Token Generation

```bash
python token_gen.py 4343348452 2336099414_W0363_BY_XANAF_GAMING_WBYMF
```

**Output:**
```
============================================================
🎯 FREE FIRE TOKEN GENERATOR
============================================================
📝 UID: 4343348452
🔑 Password: 2336099414_W0363_BY...
============================================================

📡 Requesting access token for UID: 4343348452...
✅ Access token obtained
🔐 Performing MajorLogin...
✅ MajorLogin successful
✅ JWT Token extracted
📍 Region: IND
👤 Account UID: 4343348452

============================================================
✅ TOKEN GENERATED SUCCESSFULLY!
============================================================
🎫 Token: eyJhbGciOiJIUzI1NiIsInN2ciI6IjMiLCJ0eXAiOiJKV1Qi...
📍 Region: IND
👤 UID: 4343348452
⏰ Generated: 2026-01-30 15:30:45
============================================================

💾 Token saved to generated_tokens.json
📊 Total tokens in file: 1
```

### Step 3: View Your Token

```bash
cat generated_tokens.json
```

**Output:**
```json
[
  {
    "token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjMiLCJ0eXAiOiJKV1QifQ.eyJhY2NvdW50X2lkIjoxNDEyOTQ0NjI1Miwibmlja25hbWUiOiJHT0xPUllfMyIsIm5vdGlfcmVnaW9uIjoiSU5EIiwibG9ja19yZWdpb24iOiJJTkQiLCJleHRlcm5hbF9pZCI6ImE5MzMxZTI0ZjYyOGUyNmRlNjAwNzc0ODM3NTBkYTYxIiwiZXh0ZXJuYWxfdHlwZSI6NCwicGxhdF9pZCI6MSwiY2xpZW50X3ZlcnNpb24iOiIxLjEyMC4yIiwiZW11bGF0b3Jfc2NvcmUiOjEwMCwiaXNfZW11bGF0b3IiOnRydWUsImNvdW50cnlfY29kZSI6IklOIiwiZXh0ZXJuYWxfdWlkIjo0MzQzMzQ4NDUyLCJyZWdfYXZhdGFyIjoxMDIwMDAwMDcsInNvdXJjZSI6MCwibG9ja19yZWdpb25fdGltZSI6MTc2NTg1MTA2OSwiY2xpZW50X3R5cGUiOjIsInNpZ25hdHVyZV9tZDUiOiI3NDI4YjI1M2RlZmMxNjQwMThjNjA0YTFlYmJmZWJkZiIsInVzaW5nX3ZlcnNpb24iOjEsInJlbGVhc2VfY2hhbm5lbCI6ImFuZHJvaWQiLCJyZWxlYXNlX3ZlcnNpb24iOiJPQjUyIiwiZXhwIjoxNzY4NzQzNzgyfQ.f00udPT2qrORr7_uPG6dYM2c2CF63W3nNAVOgMqegZg",
    "region": "IND",
    "account_uid": "4343348452",
    "saved_at": 1738247445.123456,
    "timestamp": "2026-01-30 15:30:45",
    "bot_uid": "4343348452",
    "source": "token_generator"
  }
]
```

## 📦 Batch Generation

### Step 1: Create credentials.txt

```bash
nano credentials.txt
```

Add your accounts:
```
4343348452,2336099414_W0363_BY_XANAF_GAMING_WBYMF
1234567890,YOUR_PASSWORD_HERE
9876543210,ANOTHER_PASSWORD
```

### Step 2: Run Batch Generation

```bash
python token_gen.py --batch
```

**Output:**
```
============================================================
🎯 FREE FIRE TOKEN GENERATOR
============================================================
📝 No emotes or bundles required - just tokens!
============================================================

📂 Batch mode: Loading credentials from credentials.txt
📋 Found 3 accounts

============================================================
Processing account 1/3
============================================================
[... token generation for account 1 ...]

============================================================
Processing account 2/3
============================================================
[... token generation for account 2 ...]

============================================================
Processing account 3/3
============================================================
[... token generation for account 3 ...]

============================================================
✅ Batch complete: 3/3 tokens generated
============================================================
```

## 🔧 Using Your Token

### Python Example

```python
import requests
import json

# Load token
with open('generated_tokens.json', 'r') as f:
    tokens = json.load(f)
    token = tokens[0]['token']

# Use token in API request
headers = {
    "Authorization": f"Bearer {token}",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA": "v1 1",
    "ReleaseVersion": "OB52",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Dalvik/2.1.0"
}

# Example: Send friend request
response = requests.post(
    "https://client.ind.freefiremobile.com/RequestAddingFriend",
    headers=headers,
    data=encrypted_data
)

print(response.status_code)
```

### cURL Example

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInN2ciI6IjMiLCJ0eXAiOiJKV1QifQ..."

curl -X POST \
  https://client.ind.freefiremobile.com/GetPlayerPersonalShow \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Unity-Version: 2018.4.11f1" \
  -H "X-GA: v1 1" \
  -H "ReleaseVersion: OB52" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: Dalvik/2.1.0" \
  --data-binary @encrypted_uid.bin
```

## ❓ Common Issues

### Issue: "Cannot import MajoRLoGinrEq_pb2"

**Solution:** Run from the main project directory:
```bash
cd /path/to/your/project
python token_generator/token_gen.py <uid> <password>
```

### Issue: "Failed at Step 1: Could not get access token"

**Solution:** 
- Check UID and password are correct
- Verify internet connection
- Wait a few minutes and try again

### Issue: "Failed at Step 3: MajorLogin request failed"

**Solution:**
- Account might be banned
- Password might be incorrect
- Try a different account

## 📊 Token Information

Your token contains:

| Field | Description | Example |
|-------|-------------|---------|
| `account_id` | Your FF account ID | 14129446252 |
| `nickname` | Your in-game name | "GLORY_3" |
| `region` | Your region | "IND" |
| `external_uid` | External account ID | 4343348452 |
| `exp` | Token expiration | 1768743782 |

## 🔒 Security Tips

1. **Never share your token** - It's like your password
2. **Don't commit to git** - Add `generated_tokens.json` to `.gitignore`
3. **Check expiration** - Tokens expire after some time
4. **Use HTTPS only** - Never send tokens over HTTP

## 🎯 Next Steps

1. ✅ Generate your first token
2. ✅ Save it to `generated_tokens.json`
3. ✅ Use it in your API requests
4. ✅ Generate more tokens as needed

## 📚 Full Documentation

For complete documentation, see [README.md](README.md)

---

**Need Help?** Check the main project README or contact the developer.
