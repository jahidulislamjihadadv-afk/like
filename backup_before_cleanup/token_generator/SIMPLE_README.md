# 🎯 Simple Token Generator

শুধু token generate করে, কোনো extra metadata নেই।

## 🚀 Quick Use

### একটা token generate করো:
```bash
python token_gen.py 4437769524 JOBAYAR_CODX-PBXLQEZIK
```

### অনেকগুলো token generate করো:
```bash
# credentials.txt এ তোমার accounts লিখো
python token_gen.py --batch
```

## 📦 Output Format

**generated_tokens.json:**
```json
[
  {
    "token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ.eyJhY2NvdW50X2lkIjoxNDI2OTcwMDAwMCwibmlja25hbWUiOiJKT1lfQk9ZLkVYRSIsIm5vdGlfcmVnaW9uIjoiQkQiLCJsb2NrX3JlZ2lvbiI6IkJEIiwiZXh0ZXJuYWxfaWQiOiIyZTdhOGRjZjhhODcyNmIwZWEzMjk3NzQ2Y2NhZTY0YiIsImV4dGVybmFsX3R5cGUiOjQsInBsYXRfaWQiOjEsImNsaWVudF92ZXJzaW9uIjoiMS4xMjAuMiIsImVtdWxhdG9yX3Njb3JlIjoxMDAsImlzX2VtdWxhdG9yIjp0cnVlLCJjb3VudHJ5X2NvZGUiOiJNWSIsImV4dGVybmFsX3VpZCI6NDM3MjM4NzkzMCwicmVnX2F2YXRhciI6MTAyMDAwMDA3LCJzb3VyY2UiOjAsImxvY2tfcmVnaW9uX3RpbWUiOjE3NjcwNjkyOTMsImNsaWVudF90eXBlIjoyLCJzaWduYXR1cmVfbWQ1IjoiNzQyOGIyNTNkZWZjMTY0MDE4YzYwNGExZWJiZmViZGYiLCJ1c2luZ192ZXJzaW9uIjoxLCJyZWxlYXNlX2NoYW5uZWwiOiJhbmRyb2lkIiwicmVsZWFzZV92ZXJzaW9uIjoiT0I1MiIsImV4cCI6MTc2OTc0NTk2MH0.AkwDrO-2OWEUaqKFACGNMmu376GvZW38VO4SqBNwdnQ"
  },
  {
    "token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ..."
  },
  {
    "token": "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ..."
  }
]
```

প্রতিটা token `{"token": "..."}` format এ!

## 💻 Use Token

```python
import json

# Load tokens
with open('generated_tokens.json') as f:
    tokens = json.load(f)

# Use first token
token = tokens[0]["token"]
print(token)
```

## 📝 credentials.txt Format

```
4437768628,JOBAYAR_CODX-IPP3PKDJB
4437769139,JOBAYAR_CODX-IYMKLOVER
4437769273,JOBAYAR_CODX-2AJDB0KJC
```

## ✅ That's It!

Simple and clean. প্রতিটা token `{"token": "..."}` format এ।
