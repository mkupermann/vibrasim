"""Telegram bot notification channel for EQMOD autopilot.

Reads credentials from ~/.eqmod/autopilot/notify_config.json:
    {
      "telegram_bot_token": "1234567890:AAA...",
      "telegram_chat_id": "123456789"
    }

Falls back to environment variables EQMOD_TELEGRAM_BOT_TOKEN and
EQMOD_TELEGRAM_CHAT_ID if the file is absent.

Sends via single HTTPS POST to https://api.telegram.org/bot<TOKEN>/sendMessage.
No third-party dependencies — uses stdlib urllib.

Setup instructions (one-time, ~5 min):

    1. Open Telegram, message @BotFather.
    2. /newbot → choose a name (e.g. "EQMOD Autopilot") and a username
       ending in "bot" (e.g. "eqmod_michael_bot").
    3. BotFather replies with a token like "1234567890:AAA...". Save it.
    4. Search for your new bot in Telegram by its username, open the chat,
       press "Start" (or send "hello"). This creates a chat the bot can
       message back.
    5. In a browser, open:
           https://api.telegram.org/bot<TOKEN>/getUpdates
       Find your numeric chat_id in the response JSON
       (path: result[*].message.chat.id).
    6. Write the credentials to ~/.eqmod/autopilot/notify_config.json:
           {
             "telegram_bot_token": "...",
             "telegram_chat_id": "..."
           }
    7. Verify with: python tools/notify_telegram.py --test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CONFIG_PATH = Path.home() / ".eqmod/autopilot/notify_config.json"


def load_config() -> tuple[str | None, str | None]:
    """Return (bot_token, chat_id) from config file or env. Either may be None."""
    token = os.environ.get("EQMOD_TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("EQMOD_TELEGRAM_CHAT_ID")
    if not (token and chat_id) and CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text())
            token = token or cfg.get("telegram_bot_token")
            chat_id = chat_id or cfg.get("telegram_chat_id")
        except (json.JSONDecodeError, OSError):
            pass
    return token, chat_id


def _post_telegram(token: str, chat_id: str, text: str, parse_mode: str | None) -> tuple[bool, str]:
    """Single attempt to POST to Telegram. Returns (ok, reason)."""
    fields = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }
    if parse_mode is not None:
        fields["parse_mode"] = parse_mode
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(fields).encode()
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode())
        if payload.get("ok"):
            return True, ""
        return False, f"telegram api: {payload.get('description', payload)}"
    except urllib.error.HTTPError as exc:
        try:
            body_text = exc.read().decode()[:500]
        except Exception:
            body_text = ""
        return False, f"http {exc.code}: {body_text}"
    except (urllib.error.URLError, TimeoutError) as exc:
        return False, f"network error: {exc!r}"
    except Exception as exc:
        return False, f"unexpected: {exc!r}"


def send_telegram(subject: str, body: str) -> tuple[bool, str]:
    """Send a Telegram message. Returns (success, failure_reason).

    Two-step delivery:
      1. Try plain text (no parse_mode) — most reliable for any content.
         The 2026-05-20T23:43 /results incident was caused by Markdown
         parse failing on underscores in identifiers like
         `count_energy_flux_through` (unbalanced italic marker → 400).
         Plain text bypasses every parse class.
      2. (Removed Markdown attempt — was the source of the silent fail.)

    Subject is prepended as `[SUBJECT] ` rather than as Markdown bold,
    since bold formatting is not load-bearing.
    """
    token, chat_id = load_config()
    if not token:
        return False, "no telegram_bot_token configured"
    if not chat_id:
        return False, "no telegram_chat_id configured"

    text = f"[{subject}]\n\n{body}" if subject else body
    if len(text) > 4000:
        text = text[:3950] + "\n\n... (truncated)"

    return _post_telegram(token, chat_id, text, parse_mode=None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", action="store_true",
                        help="send a probe message and exit with status")
    parser.add_argument("--subject", default="[EQMOD test] probe")
    parser.add_argument("--body", default="Telegram channel reachability probe.")
    args = parser.parse_args()

    if args.test:
        ok, reason = send_telegram(args.subject, args.body)
        print(f"send_telegram: {'OK' if ok else 'FAIL'}{(': ' + reason) if reason else ''}")
        return 0 if ok else 1
    print("(no action — use --test)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
