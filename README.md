# 🎯 Free Fire Token Generator

Ultra-clean standalone tool to generate Free Fire JWT tokens.

## 📁 Structure

```
.
├── README.md                # This file
│
├── Modules/                 # Required protobuf (2 files)
│   ├── MajoRLoGinrEq_pb2.py
│   └── MajoRLoGinrEs_pb2.py
│
└── token_generator/         # Main tool
    ├── token_gen.py         # Core generator
    ├── menu.py              # Auto batch mode
    ├── credentials.txt      # Your accounts
    ├── requirements.txt     # Dependencies
    ├── RUN_ME.bat          # Windows shortcut
    └── RUN_ME.sh           # Linux/Mac shortcut
```

## 🚀 Usage (3 Steps)

### 1. Install (First time only)
```bash
cd token_generator
pip install -r requirements.txt
```

### 2. Add Your Accounts
Edit `token_generator/credentials.txt`:
```
4437768628,JOBAYAR_CODX-IPP3PKDJB
4437769139,JOBAYAR_CODX-IYMKLOVER
```

### 3. Generate Tokens
```bash
cd token_generator
python menu.py
```

**Done!** Tokens saved in `generated_tokens.json`

## ✨ What menu.py Does

1. ✅ Reads all accounts from `credentials.txt`
2. 🗑️ Deletes old tokens
3. 🔄 Generates fresh tokens
4. 💾 Saves to `generated_tokens.json`

## 📦 Output Format

```json
[
  {"token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ..."},
  {"token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ..."}
]
```

## 🔧 Requirements

- Python 3.7+
- requests
- aiohttp  
- pycryptodome
- protobuf

## 💡 Alternative Methods

**Windows:** Double-click `RUN_ME.bat`

**Linux/Mac:** `./RUN_ME.sh`

**Single token:** `python token_gen.py <uid> <password>`

---

**That's it!** Simple and clean. 🎉
