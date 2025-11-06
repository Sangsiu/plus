
# Mnet Signup Service (Python)

Automasi registrasi (authToken → save-tmp) via FastAPI dan CLI.

## Struktur
```
mnet_signup_service/
├─ api/
│  └─ app.py                # FastAPI endpoints (/signup, /batch-signup, /health)
├─ src/
│  └─ mnet_signup_bot/
│     ├─ __init__.py
│     ├─ http.py            # Session + retry helper
│     ├─ bot.py             # Core signup logic
│     └─ cli.py             # CLI (single/batch)
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

## Menjalankan lokal
```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
# Jalankan API
export PYTHONPATH=src
uvicorn api.app:app --host 0.0.0.0 --port 8000
# Buka: http://localhost:8000/docs
```

## Jalankan Docker
```bash
docker compose up --build -d
# Buka: http://localhost:8000/docs
```

## API
- `POST /signup` body:
```json
{
  "email": "user@example.com",
  "password": "Defa12345!",
  "gender": "m",
  "birth_year": "1998",
  "locale": "en",
  "device_name": "optional",
  "marketing_terms_version": "20221106"
}
```
- `POST /batch-signup` form-data:
  - file: CSV (`email,password[,gender,birth_year,device_name,locale,marketing_terms_version]`)

## CLI
Single:
```bash
python -m mnet_signup_bot.cli single --email user@example.com --password "Defa12345!"
```
Batch:
```bash
python -m mnet_signup_bot.cli batch --csv daftar_signup.csv
```

> Gunakan secara bertanggung jawab dan sesuai ketentuan layanan situs terkait.
