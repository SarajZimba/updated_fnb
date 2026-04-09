# email_utils.py
# from flask_mail import Message
# from root.app import mail, app  # import mail and app from your Flask app

# def send_email_flask(to, subject, html, attachments=None, sender_name="Alice Restaurant"):
#     """Send a single email via Flask-Mail."""
#     with app.app_context():  # ensure app context for Flask-Mail
#         msg = Message(
#             subject=subject,
#             recipients=[to],
#             html=html,
#             sender=f"{sender_name} <{app.config['MAIL_USERNAME']}>"
#         )

#         # Attach files if provided
#         if attachments:
#             for file in attachments:
#                 msg.attach(
#                     filename=file["filename"],
#                     content_type=file.get("content_type", "application/octet-stream"),
#                     data=file["data"]
#                 )

#         mail.send(msg)

# email_utils.py

def send_email_flask(to, subject, html, attachments=None, sender_name="Alice Restaurant"):
    from root.app import mail, app  # import here to avoid circular import
    from flask_mail import Message

    with app.app_context():
        msg = Message(
            subject=subject,
            # subject=f"Advertising Report For Alice Restaurant",
            recipients=[to],
            html=html,
            sender=f"{sender_name} <{app.config['MAIL_USERNAME']}>"
        )

        if attachments:
            for file in attachments:
                msg.attach(
                    filename=file["filename"],
                    content_type=file["content_type"],
                    data=file["data"]
                )

        mail.send(msg)
