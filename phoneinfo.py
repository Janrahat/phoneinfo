#!/usr/bin/env python3
import argparse
import json
import os
import sys

try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone
except ImportError:
    sys.exit("Install dependencies: pip install phonenumbers requests")

import requests

TYPE_MAP = {
    0: "FIXED_LINE", 1: "MOBILE", 2: "FIXED_LINE_OR_MOBILE",
    3: "TOLL_FREE", 4: "PREMIUM_RATE", 5: "SHARED_COST",
    6: "VOIP", 7: "PERSONAL_NUMBER", 8: "PAGER", 9: "UAN",
    10: "VOICEMAIL", 99: "UNKNOWN",
}

# Approximate location hint from timezone name
def tz_location(tz: str) -> str:
    t = tz.split("/")[-1].replace("_", " ").title()
    return t

def remote_lookup(e164: str, lang: str = "en"):
    key = os.environ.get("NUMVERIFY_KEY")
    if not key:
        return None
    try:
        r = requests.get(
            "http://apilayer.net/api/validate",
            params={"access_key": key, "number": e164, "format": 1,
                    "country_code": "", "language": lang},
            timeout=10,
        )
        return r.json() if r.ok else None
    except requests.RequestException:
        return None

def lookup(number: str, lang: str = "en", remote: bool = False):
    p = phonenumbers.parse(number, None)

    # --- Location via geocoder (offline region/city) ---
    geo = geocoder.description_for_number(p, lang) or "unknown"
    # Secondary: timezone-based area hint
    tzs = timezone.time_zones_for_number(p)
    area_hint = ", ".join(tz_location(t) for t in tzs) if tzs else "unknown"

    info = {
        "input": number,
        "valid": phonenumbers.is_valid_number(p),
        "possible": phonenumbers.is_possible_number(p),
        "e164": phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164),
        "international": phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
        "national": phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.NATIONAL),
        "country_code": p.country_code,
        "country": geo,
        "location_area": area_hint,
        "number_type": TYPE_MAP.get(phonenumbers.number_type(p), "UNKNOWN"),
        "timezones": tzs,
        "carrier_local": carrier.name_for_number(p, lang) or "unknown",
    }

    if remote:
        data = remote_lookup(info["e164"], lang)
        if data:
            info["remote"] = {
                "carrier": data.get("carrier"),
                "line_type": data.get("line_type"),
                "location": data.get("location"),
                "country_name": data.get("country_name"),
                "country_code_cc": data.get("country_code"),
            }
        else:
            info["remote"] = "skipped (set NUMVERIFY_KEY)"
    return info

def main():
    ap = argparse.ArgumentParser(description="Powerful phone number information tool")
    ap.add_argument("number", help="e.g. +14155552671")
    ap.add_argument("--remote", action="store_true",
                    help="Live carrier/location via numverify (needs NUMVERIFY_KEY)")
    ap.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    ap.add_argument("--lang", default="en", help="Geocoder language (e.g. hi, es, ar)")
    args = ap.parse_args()

    try:
        info = lookup(args.number, args.lang, args.remote)
    except phonenumbers.NumberParseException as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return

    print("=" * 54)
    print(f" Input            : {info['input']}")
    print(f" Valid / Possible : {info['valid']} / {info['possible']}")
    print(f" E.164            : {info['e164']}")
    print(f" International    : {info['international']}")
    print(f" National         : {info['national']}")
    print(f" Country Code     : +{info['country_code']}")
    print(f" Country/Region   : {info['country']}")
    print(f" Location Area    : {info['location_area']}")
    print(f" Number Type      : {info['number_type']}")
    print(f" Timezones        : {', '.join(info['timezones']) or 'unknown'}")
    print(f" Carrier (local)  : {info['carrier_local']}")
    if args.remote and isinstance(info.get("remote"), dict):
        r = info["remote"]
        print("-" * 54)
        print(f" Remote carrier   : {r.get('carrier','unknown')}")
        print(f" Remote line type : {r.get('line_type','unknown')}")
        print(f" Remote location  : {r.get('location','unknown')}")
        print(f" Remote country   : {r.get('country_name','unknown')}")
    elif args.remote:
        print("-" * 54)
        print(" Remote lookup    : set NUMVERIFY_KEY to enable")
    print("=" * 54)

if __name__ == "__main__":
    main()
