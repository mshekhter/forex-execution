# =========================
# NOTIFICATIONS
# =========================

def send_email(subject, body):
    if not USE_EMAIL:
        return

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
    server.quit()

def send_telegram(body):
    if not USE_TELEGRAM:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": body}
    requests.post(url, json=payload, timeout=10)

def notify(subject, message):
    print(message)

    try:
        send_email(subject, message)
    except Exception as e:
        print(f"[{utcnow()}] EMAIL error: {e}")

    try:
        send_telegram(message)
    except Exception as e:
        print(f"[{utcnow()}] TELEGRAM error: {e}")
