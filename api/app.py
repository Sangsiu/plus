
from __future__ import annotations
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import csv
import io

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from mnet_signup_bot.bot import run_single

app = FastAPI(title="Mnet Signup Service", version="1.0.0")

templates = Jinja2Templates(directory="api/templates")

class SignupReq(BaseModel):
    email: EmailStr
    password: str
    gender: str = "m"
    birth_year: str = "1998"
    locale: str = "en"
    device_name: Optional[str] = None
    marketing_terms_version: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/signup")
def signup(req: SignupReq):
    try:
        run_single(
            email=req.email, password=req.password, gender=req.gender,
            birth_year=req.birth_year, locale=req.locale, device_name=req.device_name,
            marketing_terms_version=req.marketing_terms_version
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-signup")
async def batch_signup(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")
    content = await file.read()
    ok = 0
    total = 0
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV parse error: {e}")

    for row in reader:
        total += 1
        email = (row.get("email") or "").strip()
        password = (row.get("password") or "").strip()
        if not email or not password:
            continue
        gender = (row.get("gender") or "m").strip()
        birth_year = (row.get("birth_year") or "1998").strip()
        device_name = (row.get("device_name") or None)
        locale = (row.get("locale") or "en").strip()
        terms_ver = (row.get("marketing_terms_version") or None)
        try:
            run_single(
                email=email, password=password, gender=gender, birth_year=birth_year,
                locale=locale, device_name=device_name, marketing_terms_version=terms_ver
            )
            ok += 1
        except Exception as e:
            logging.error("[batch] %s: %s", email, e)
    return {"ok": True, "processed": total, "success": ok}
