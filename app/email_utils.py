import aiosmtplib
from email.message import EmailMessage
from .core.config import get_settings

settings = get_settings()

SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASS = settings.SMTP_PASS

async def send_verification_email(to_email: str, token: str):
    verify_link = f"http://localhost:8000/verify-email?token={token}"

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "이메일 인증 요청"
    msg.set_content(f"아래 링크를 클릭해 이메일 인증을 완료하세요:\n{verify_link}")

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        start_tls=True
    )