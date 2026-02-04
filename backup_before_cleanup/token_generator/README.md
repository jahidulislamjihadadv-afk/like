# Free Fire Token Generator

A standalone tool to generate JWT authentication tokens for Free Fire accounts. No emotes or bundles required - just pure token generation!

## Features

✅ Generate JWT tokens from UID and password  
✅ Single token generation  
✅ Batch token generation from file  
✅ Save tokens to JSON file  
✅ No dependencies on emotes or bundles  
✅ Clean, minimal code  

## Requirements

```bash
pip install requests aiohttp pycryptodome
```

You also need the protobuf modules from the main project:
- `Modules/MajoRLoGinrEq_pb2.py`
- `Modules/MajoRLoGinrEs_pb2.py`

## Usage

### 1. Single Token Generation (Command Line)

```bash
python token_gen.py <uid> <password>
```

Example:
```bash
python token_gen.py 4343348452 2336099414_W0363_BY_XANAF_GAMING_WBYMF
```

### 2. Single Token Generation (Interactive)

```bash
python token_gen.py
```

Then enter UID and password when prompted.

### 3. Batch Token Generation

Create a `credentials.txt` file with your accounts:

```
# Format: uid,password (one per line)
4343348452,2336099414_W0363_BY_XANAF_GAMING_WBYMF
1234567890,YOUR_PASSWORD_HERE
9876543210,ANOTHER_PASSWORD
```

Then run:

```bash
python token_gen.py --batch
```

## Output

Tokens are saved to `generated_tokens.json` in the following format:

```json
[
  {
    "token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjMiLCJ0eXAiOiJKV1QifQ...",
    "region": "IND",
    "account_uid": "4343348452",
    "saved_at": 1768714982.2221375,
    "timestamp": "2026-01-18 11:13:02",
    "bot_uid": "4343348452",
    "source": "token_generator"
  }
]
```

## Token Format

The generated token is a JWT (JSON Web Token) that contains:

- `account_id`: Your Free Fire account ID
- `nickname`: Your in-game name
- `noti_region`: Notification region (e.g., "IND")
- `lock_region`: Locked region
- `external_id`: External account ID
- `external_type`: Account type (4 = guest)
- `plat_id`: Platform ID (1 = Android)
- `client_version`: Game version
- `emulator_score`: Emulator detection score
- `is_emulator`: Whether running on emulator
- `country_code`: Country code
- `exp`: Token expiration timestamp

## How It Works

The token generation process follows these steps:

1. **Get Access Token**: Request OAuth token from Garena servers
   - Endpoint: `https://100067.connect.garena.com/oauth/guest/token/grant`
   - Requires: UID, password, client credentials

2. **Create MajorLogin Payload**: Build protobuf message with device info
   - Uses `MajoRLoGinrEq_pb2.MajorLogin` protobuf
   - Includes device specs, Android version, etc.
   - Encrypted with AES-CBC

3. **Perform MajorLogin**: Send login request to Free Fire
   - Endpoint: `https://loginbp.ggblueshark.com/MajorLogin`
   - Returns encrypted response

4. **Extract JWT Token**: Parse response and extract token
   - Uses `MajoRLoGinrEs_pb2.MajorLoginRes` protobuf
   - Extracts token, region, account UID

## Token Usage

You can use the generated token for API requests:

```python
import requests

token = "YOUR_GENERATED_TOKEN"

headers = {
    "Authorization": f"Bearer {token}",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA": "v1 1",
    "ReleaseVersion": "OB52",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Dalvik/2.1.0"
}

# Example: Get player info
response = requests.post(
    "https://client.ind.freefiremobile.com/GetPlayerPersonalShow",
    headers=headers,
    data=encrypted_uid_data
)
```

## Security Notes

⚠️ **Important Security Information:**

1. **Never share your tokens** - They provide full access to your account
2. **Tokens expire** - Check the `exp` field in the JWT
3. **Store securely** - Don't commit `generated_tokens.json` to git
4. **Use at your own risk** - This tool is for educational purposes

## Troubleshooting

### "Failed at Step 1: Could not get access token"
- Check your UID and password are correct
- Verify internet connection
- Try again after a few minutes

### "Failed at Step 3: MajorLogin request failed"
- Account might be banned
- Password might be incorrect
- Server might be down

### "Cannot import MajoRLoGinrEq_pb2"
- Make sure you run from the project directory
- Verify `Modules/` folder exists with protobuf files

## File Structure

```
token_generator/
├── token_gen.py           # Main token generator script
├── README.md              # This file
├── credentials.txt        # Your account credentials (create this)
└── generated_tokens.json  # Output file (auto-created)
```

## Comparison with Main Bot

| Feature | Main Bot (main.py) | Token Generator |
|---------|-------------------|-----------------|
| Token Generation | ✅ | ✅ |
| Emote System | ✅ | ❌ |
| Bundle System | ✅ | ❌ |
| Squad Management | ✅ | ❌ |
| Message Sending | ✅ | ❌ |
| TCP Connection | ✅ | ❌ |
| Standalone | ❌ | ✅ |
| Minimal Code | ❌ | ✅ |

## License

This tool is for educational purposes only. Use at your own risk.

## Credits

Based on the Free Fire bot project by BLACK_APIs and XANAF_GAMING.

---

**Last Updated**: January 30, 2026  
**Version**: 1.0.0
