#!/usr/bin/env python3
"""
Test both no-DLT alert options:
  1. Fast2SMS Quick SMS  (needs FAST2SMS_API_KEY in .env)
  2. WhatsApp CallMeBot  (needs CALLMEBOT_PHONE + CALLMEBOT_APIKEY in .env)

Run after setting up one of the options.
"""

import os, sys, requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

PHONE     = "9187488437"
MESSAGE   = (
    "ANPR TEST: Your vehicle KA05EF2008 (Maruti Alto) was DENIED fuel "
    "at Pump PUMP-001. Reason: Exceeds petrol age limit (17 yrs / limit 15 yrs). "
    "Please apply for Fitness Certificate at RTO. -PollutionControl"
)

# ── Fast2SMS Quick SMS ──────────────────────────────────────────────────────
def test_fast2sms():
    key = os.getenv("FAST2SMS_API_KEY", "")
    if not key:
        print("  ⚠️  FAST2SMS_API_KEY not set in .env — skipping")
        return False

    print(f"  Sending via Fast2SMS Quick SMS to {PHONE}...")
    try:
        resp = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            json={"route": "q", "message": MESSAGE, "language": "english", "flash": 0, "numbers": PHONE},
            headers={"authorization": key, "Content-Type": "application/json"},
            timeout=15
        )
        data = resp.json()
        if data.get("return") is True:
            print(f"  ✅ Fast2SMS SENT! Response: {data}")
            return True
        else:
            print(f"  ❌ Fast2SMS failed: {data}")
            return False
    except Exception as e:
        print(f"  ❌ Fast2SMS error: {e}")
        return False

# ── WhatsApp CallMeBot ──────────────────────────────────────────────────────
def test_callmebot():
    cb_phone = os.getenv("CALLMEBOT_PHONE", "")
    cb_key   = os.getenv("CALLMEBOT_APIKEY", "")
    if not cb_phone or not cb_key:
        print("  ⚠️  CALLMEBOT_PHONE or CALLMEBOT_APIKEY not set in .env — skipping")
        print("  Setup: Save +34 644 59 26 19 in WhatsApp → send 'I allow callmebot to send me messages'")
        return False

    print(f"  Sending WhatsApp to +{cb_phone} via CallMeBot...")
    try:
        resp = requests.get(
            "https://api.callmebot.com/whatsapp.php",
            params={"phone": cb_phone, "text": MESSAGE, "apikey": cb_key},
            timeout=20
        )
        if resp.status_code == 200 and "Message Sent" in resp.text:
            print(f"  ✅ WhatsApp SENT! Check your WhatsApp.")
            return True
        else:
            print(f"  ❌ CallMeBot: {resp.status_code} — {resp.text[:150]}")
            return False
    except Exception as e:
        print(f"  ❌ CallMeBot error: {e}")
        return False

# ── Main ────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  ANPR Alert System — Live Test")
print("="*60)
print(f"  Target  : +91-{PHONE}")
print(f"  Message : {MESSAGE[:60]}...")
print("="*60)

print("\n[1] Testing Fast2SMS Quick SMS (no DLT)...")
ok1 = test_fast2sms()

print("\n[2] Testing WhatsApp CallMeBot (free)...")
ok2 = test_callmebot()

print("\n" + "="*60)
if ok1 or ok2:
    print("  ✅ SUCCESS — alert system is live!")
    if ok1: print("     SMS delivered via Fast2SMS Quick")
    if ok2: print("     WhatsApp delivered via CallMeBot")
else:
    print("  ℹ️  No providers configured yet.")
    print()
    print("  FASTEST OPTION — Fast2SMS (no DLT):")
    print("  1. Go to: https://fast2sms.com/dashboard/devapi")
    print("  2. Copy your API key")
    print("  3. In .env, uncomment and fill:")
    print("     FAST2SMS_API_KEY=paste_key_here")
    print("  4. Run this test again: python test_sms.py")
    print()
    print("  FREE OPTION — WhatsApp CallMeBot:")
    print("  1. Save +34 644 59 26 19 in WhatsApp")
    print("  2. Send: 'I allow callmebot to send me messages'")
    print("  3. Get API key, add to .env:")
    print("     CALLMEBOT_PHONE=919187488437")
    print("     CALLMEBOT_APIKEY=paste_key_here")
print("="*60 + "\n")
