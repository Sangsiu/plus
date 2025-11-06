
from __future__ import annotations
import argparse
import csv
import logging
import sys
from types import SimpleNamespace
from .bot import run_single

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Mnet signup bot (authToken -> save-tmp)")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--locale", default="en")
    common.add_argument("--gender", default="m", choices=["m", "f"])
    common.add_argument("--birth-year", type=str, default="1998")
    common.add_argument("--device-name", default=None)
    common.add_argument("--marketing-terms-version", default=None)
    common.add_argument("--timeout", type=int, default=30)
    common.add_argument("--retries", type=int, default=3)
    common.add_argument("--backoff", type=float, default=0.5)

    s = sub.add_parser("single", parents=[common], help="Run one signup")
    s.add_argument("--email", required=True)
    s.add_argument("--password", required=True)
    s.set_defaults(func="single")

    b = sub.add_parser("batch", parents=[common], help="Run batch signups from CSV")
    b.add_argument("--csv", required=True, help="CSV columns: email,password[,gender,birth_year,device_name,locale,marketing_terms_version]")
    b.set_defaults(func="batch")

    return p

def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "single":
        run_single(
            email=args.email, password=args.password, gender=args.gender,
            birth_year=args.birth_year, locale=args.locale,
            device_name=args.device_name, marketing_terms_version=args.marketing_terms_version,
            timeout=args.timeout, retries=args.retries, backoff=args.backoff
        )
        return 0

    if args.cmd == "batch":
        ok = 0
        total = 0
        with open(args.csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                email = row["email"].strip()
                password = row["password"].strip()
                gender = (row.get("gender") or args.gender).strip()
                birth_year = (row.get("birth_year") or args.birth_year)
                device_name = (row.get("device_name") or args.device_name)
                locale = (row.get("locale") or args.locale)
                terms_ver = row.get("marketing_terms_version") or args.marketing_terms_version
                try:
                    run_single(
                        email=email, password=password, gender=gender, birth_year=str(birth_year),
                        locale=locale, device_name=device_name, marketing_terms_version=terms_ver,
                        timeout=args.timeout, retries=args.retries, backoff=args.backoff
                    )
                    ok += 1
                except Exception as e:
                    logging.error("[%d] %s: %s", total, email, e)
        logging.info("Batch complete. Success: %d / %d", ok, total)
        return 0

    return 2

if __name__ == "__main__":
    sys.exit(main())
