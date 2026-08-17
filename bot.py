#!/opt/homebrew/bin/python3.11
# EMBER Kitchen bot - stdlib only (urllib long polling), no dependencies.
import json, time, urllib.request, urllib.parse, os, sys, traceback

TOKEN = "8802336423:AAElIYMe4Vvul6E59Pn0fNIns_RzmZaXTTQ"
OWNER_ID = 780868306  # Yan - receives forwarded orders
WEBAPP_URL = "https://yanixvx.github.io/cafe-mini-app/"
BOT_USERNAME = "openyanixvxclawbot"
API = "https://api.telegram.org/bot" + TOKEN
LOGO = os.path.expanduser("~/Documents/cafe_mini_app/img/logo.jpg")

def api(method, params=None, files=None):
    if files:
        boundary = "----b" + "x" * 24
        body = b""
        for k, v in (params or {}).items():
            body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, k, v)).encode()
        for k, (fn, data, ctype) in files.items():
            body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n" % (boundary, k, fn, ctype)).encode() + data + b"\r\n"
        body += ("--%s--\r\n" % boundary).encode()
        req = urllib.request.Request(API + "/" + method, data=body,
                                     headers={"Content-Type": "multipart/form-data; boundary=" + boundary})
    else:
        req = urllib.request.Request(API + "/" + method,
                                     data=urllib.parse.urlencode(params or {}).encode())
    try:
        with urllib.request.urlopen(req, timeout=65) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def webapp_kb():
    return json.dumps({"inline_keyboard": [
        [{"text": "🍽 Open EMBER", "web_app": {"url": WEBAPP_URL}}],
        [{"text": "ℹ️ Info & hours", "callback_data": "info"}]
    ]})

def send_message(chat_id, text, kb=None, parse="HTML"):
    return api("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": parse,
                               "reply_markup": kb} if kb else {"chat_id": chat_id, "text": text, "parse_mode": parse})

def send_photo(chat_id, path, caption, kb=None):
    with open(path, "rb") as f:
        data = f.read()
    return api("sendPhoto", {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML",
                             "reply_markup": kb} if kb else {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"},
                          {"photo": (os.path.basename(path), data, "image/jpeg")})

WELCOME = ("🔥 <b>Welcome to EMBER!</b>\n\n"
           "Wood-fire kitchen & bar. Everything leaves our oven or open flame - "
           "nothing frozen, nothing fake.\n\n"
           "What's inside:\n"
           "🍽 Full menu, real photos\n"
           "🎲 <b>Surprise Plate</b> - spin, land a dish, save 20% tonight\n"
           "☕ <b>Lucky Cup</b> - six cups hide one coffee code, 50% off any coffee\n"
           "🪑 Table booking in one tap\n\n"
           "Tap the button below to open the menu 👇")

INFO = ("📍 24 Canal Street, Old Town\n"
        "📞 +1 (555) 014-8237\n"
        "🕐 Mon - Thu 11:00 - 23:00\n"
        "🕐 Fri - Sat 11:00 - 01:00\n"
        "🕐 Sun 12:00 - 22:00\n\n"
        "Order ahead in the app, or call us for a quick pickup.")

def cmd_reply(cmd):
    if cmd == "menu":
        return "Full menu is one tap away 👇", True
    if cmd == "surprise":
        return "🎲 <b>Surprise Plate</b>: pick a budget ($15 / $25 / $40), spin the wheel, land a random dish and get it 20% off tonight. Open the app and hit the Surprise tab 👇", True
    if cmd == "lucky":
        return "☕ <b>Lucky Cup</b>: six cups, one hidden coffee code. Pick the right cup and grab 50% off any coffee, valid for 24 hours. Open the app and hit the Lucky tab 👇", True
    if cmd == "book":
        return "🪑 To book a table, tap this link and send the message: https://t.me/%s?text=%s" % (BOT_USERNAME, urllib.parse.quote("🌿 TABLE REQUEST - EMBER\nGuests: 2\nTime: tonight\nPlease confirm availability.")), False
    return None, False

def handle_update(u):
    try:
        if "message" in u:
            m = u["message"]
            chat = m["chat"]["id"]
            text = (m.get("text") or "").strip()
            frm = m.get("from", {})
            uid = frm.get("id")
            cmd = text.split()[0].lower() if text.startswith("/") else ""

            if cmd == "/start":
                send_photo(chat, LOGO, WELCOME, webapp_kb())
                return
            if cmd in ("/menu", "/surprise", "/lucky", "/book"):
                reply, with_kb = cmd_reply(cmd[1:])
                send_message(chat, reply, webapp_kb() if with_kb else None)
                return

            # Forward orders / table requests to the owner
            if uid != OWNER_ID and ("NEW ORDER" in text or "TABLE REQUEST" in text):
                who = "@%s" % frm.get("username") if frm.get("username") else ("%s %s" % (frm.get("first_name", ""), frm.get("last_name", "") or "")).strip() or str(uid)
                api("sendMessage", {"chat_id": OWNER_ID, "text": "📥 %s\n%s" % (who, text), "parse_mode": "HTML"})
                send_message(chat, "✅ Received! We'll confirm your order shortly. Thank you! 🔥")
                return

            if text:
                send_message(chat, "Tap the <b>🍽 EMBER</b> button below to open the menu 👇", webapp_kb())

        elif "callback_query" in u:
            cq = u["callback_query"]
            cid = cq["message"]["chat"]["id"]
            data = cq.get("data", "")
            api("answerCallbackQuery", {"callback_query_id": cq["id"], "text": "EMBER Kitchen - 24 Canal Street"})
            if data == "info":
                send_message(cid, INFO)
    except Exception:
        traceback.print_exc()

def main():
    offset = 0
    print("EMBER bot polling started", flush=True)
    while True:
        try:
            res = api("getUpdates", {"offset": offset, "timeout": 50})
            if res and res.get("ok"):
                for u in res.get("result", []):
                    offset = u["update_id"] + 1
                    handle_update(u)
            else:
                time.sleep(3)
        except Exception:
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    main()
