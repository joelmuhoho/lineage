from flask import current_app as app, render_template, request
from flask_mail import Message
from threading import Thread
from app.extensions import mail
from itsdangerous import URLSafeSerializer
from queue import Queue


def send_async_email(app, msg):
    try:
        with app.app_context():
            mail.send(msg)
        return True, None
    except Exception as e:
        error_msg = str(e)
        # app.logger.error(f"Failed to send email: {error_msg}")
        print(f"Failed to send email: {error_msg}")
        return False, error_msg


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    try:
        # Create the application context here
        ctx = app.app_context()
        result_queue = Queue()

        def send_and_queue_result():
            with ctx:
                result = send_async_email(app, msg)
                result_queue.put(result)

        email_thread = Thread(target=send_and_queue_result)
        email_thread.start()
        email_thread.join(timeout=10)

        if not email_thread.is_alive():
            try:
                success, error = result_queue.get_nowait()
                return success, error
            except Exception as e:
                return False, f"Failed to get email sending result: {str(e)}"
        else:
            # Kill the thread if it's still running
            return False, "Email sending timeout"

    except Exception as e:
        error_msg = str(e)
        print(f"Error creating email thread: {error_msg}")
        return False, error_msg



# send reset password link to user
def send_password_reset_email(user):
    token = user.get_reset_password_token(app.config['SECRET_KEY'])
    send_email('[Lineage] Reset Your Password',
               sender=app.config['ADMINS'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_email_verification_link(user):
    try:
        url_root = request.url_root
        auth_s = URLSafeSerializer(app.config["SECRET_KEY"], app.config["SALT"])
        token = auth_s.dumps({"user_id": user.user_id})

        success, error = send_email(
            '[Lineage] Verify Email',
            sender=app.config['ADMINS'],
            recipients=[user.email],
            text_body=render_template('email/verify_email.txt',
                                      link=f'{url_root}{token}',
                                      user=user),
            html_body=render_template('email/verify_email.html',
                                      link=f'{url_root}verify_email/{token}',
                                      user=user)
        )

        if success:
            return True, None
        else:
            print(f"=====>{error}")
            return False, error

    except Exception as e:
        error_msg = str(e)
        # app.logger.error(f"Error in sendEmailVerificationLink: {error_msg}")
        print(f"Error in sendEmailVerificationLink: {error_msg}")
        return False, error_msg
