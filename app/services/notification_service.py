import smtplib
import urllib.parse
import urllib.request
from email.mime.text import MIMEText

from app.models.setting_model import SettingModel


def _get_setting(key):
    s = SettingModel.query.filter_by(setting_key=key).first()
    return s.setting_value if s else None


def send_email(to_addr, subject, message):
    smtp_host = _get_setting("smtp.host")
    smtp_port = _get_setting("smtp.port")
    smtp_user = _get_setting("smtp.username")
    smtp_pass = _get_setting("smtp.password")
    from_addr = _get_setting("smtp.from") or "cardvault@localhost"

    if not smtp_host or not to_addr:
        return False

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    try:
        port = int(smtp_port) if smtp_port else 587
        with smtplib.SMTP(smtp_host, port, timeout=10) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        return True
    except Exception:
        return False


def send_telegram(message):
    bot_token = _get_setting("telegram.bot.token")
    chat_id = _get_setting("telegram.chat.id")
    if not bot_token or not chat_id:
        return False
    try:
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": message[:4096],
        }).encode("utf-8")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False