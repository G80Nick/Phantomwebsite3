import os
import smtplib
from email.message import EmailMessage

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.post("/api/contact")
def contact():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    details = (payload.get("details") or "").strip()

    if not name or not email or not details:
        return jsonify({"ok": False, "message": "Please complete all fields before sending."}), 400

    recipient = os.environ.get("CONTACT_TO", "phantom3dviews@gmail.com")
    subject = f"New inquiry from {name}"
    body = f"Name: {name}\nEmail: {email}\n\nDetails:\n{details}"

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"

    if smtp_host and smtp_user and smtp_password:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = recipient
        msg.set_content(body)

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_use_tls:
                    server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            return jsonify({"ok": True, "message": "Message sent successfully."})
        except Exception as exc:
            return jsonify({"ok": False, "message": f"Message received, but delivery failed: {exc}"}), 500

    return jsonify({"ok": True, "message": "Message received locally. Configure SMTP to send it by email."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
