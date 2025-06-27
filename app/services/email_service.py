from flask import current_app as app, render_template, request
from flask_mail import Message
from threading import Thread
from app.extensions import mail
from itsdangerous import URLSafeSerializer
from queue import Queue


def send_async_email(app, msg):
    """
    Send an asynchronous email using the given application context.

    This function attempts to send an email message within the context of the
    provided application. If the email sending fails, it logs the error message
    and returns the failure state along with the error details.

    Parameters:
        app (flask.Flask): The Flask application instance used to provide
            the application context.
        msg (flask_mail.Message): The email message to be sent.

    Returns:
        Tuple[bool, Optional[str]]: A tuple where the first element indicates
            success (True) or failure (False) in sending the email, and the
            second element contains the error message as a string if the sending
            failed, or None if no error occurred.
    """
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
    """
    Sends an email with both text and HTML content asynchronously. The function creates
    a thread that handles the email sending operation, ensuring non-blocking behavior
    for the caller. Provides feedback on the success or failure of the email sending
    operation.

    Arguments:
        subject (str): The subject of the email.
        sender (str): The email address of the sender.
        recipients (list of str): A list of recipient email addresses.
        text_body (str): The plain text content of the email.
        html_body (str): The HTML content of the email.

    Returns:
        tuple: A tuple containing two elements:
            - A boolean indicating whether the email was successfully sent (True)
              or not (False).
            - A string providing additional information about the success or error.
    """
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

def send_password_reset_email(user):
    """
    Send a password reset email to a specified user.

    This function generates a password reset token for the given user using
    a secret key from the application configuration. It then sends an email
    containing the reset token to the user's registered email address. Both
    text and HTML versions of the email are sent.

    Args:
        user: The user object for whom the password reset email is being sent.

    Raises:
        Does not raise any explicit errors. Errors related to token generation,
        sending emails, or template rendering might occur during execution.
    """
    token = user.get_reset_password_token(app.config['SECRET_KEY'])
    send_email('[Lineage] Reset Your Password',
               sender=app.config['ADMINS'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_email_verification_link(user):
    """
    Send an email containing a verification link to a specified user. The verification
    link is constructed using a securely generated token containing the user's ID
    and the application's root URL. The email includes both plain text and HTML
    content templates.

    Parameters:
    user (User): The user object representing the recipient of the verification
    email. It must have a `user_id` and `email` attribute.

    Returns:
    tuple[bool, str|None]: A tuple where the first element indicates the success
    status of the email sending operation (True if successful, False otherwise),
    and the second element provides an error message as a string if an error
    occurred or None if the operation was successful.

    Raises:
    Exception: Re-raised exception in case of any unhandled error during
    the email sending process, logged for debugging purposes.
    """
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
