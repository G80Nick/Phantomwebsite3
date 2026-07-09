from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")
ROOT = Path(__file__).resolve().parent


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "phantom-contact"})


@app.get("/")
def index():
    return send_from_directory(ROOT, "index.html")


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
            app.logger.exception("Failed to send contact email")
            return jsonify({"ok": False, "message": f"Message received locally, but delivery failed: {exc}"}), 500

    app.logger.info("SMTP is not configured; contact message logged locally: %s", {"name": name, "email": email, "details": details})
    return jsonify({"ok": True, "message": "Message received locally. Configure SMTP to send it by email."})


@app.route("/<path:path>")
def serve_static(path: str):
    return send_from_directory(ROOT, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
