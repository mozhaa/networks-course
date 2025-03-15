import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(args: argparse.Namespace):
    msg = MIMEMultipart()
    msg["From"] = args.from_email
    msg["To"] = args.to_email
    msg["Subject"] = args.subject

    if args.message is not None:
        message = args.message
    else:
        with open(args.message_file, "r+") as f:
            message = f.read()
    msg.attach(MIMEText(message, args.message_type))

    try:
        with smtplib.SMTP(args.smtp_host, args.smtp_port) as server:
            if args.use_tls:
                server.starttls()
            if args.smtp_login is not None and args.smtp_password is not None:
                server.login(args.smtp_login, args.password)
            server.send_message(msg)
            print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--to-email", type=str, required=True, help="email of receiver")
    parser.add_argument("--from-email", type=str, required=True, help="email of sender")
    parser.add_argument("--subject", type=str, required=True, help="mail subject")
    parser.add_argument("--message", type=str, help="message text")
    parser.add_argument("--message-file", type=str, help="file to read message from")
    parser.add_argument("--message-type", type=str, default="plain", choices=["plain", "html"], help="message type")
    parser.add_argument("--smtp-host", type=str, required=True, help="host of smtp server")
    parser.add_argument("--smtp-port", type=int, required=True, help="port of smtp server")
    parser.add_argument("--smtp-login", type=str, help="smtp server login")
    parser.add_argument("--smtp-password", type=str, help="smtp server password")
    parser.add_argument("--use-tls", action="store_true", help="use tls for this smtp server")
    args = parser.parse_args()
    if args.message is None and args.message_file is None:
        raise RuntimeError("Provide --message of --message-file flag")
    return args


if __name__ == "__main__":
    args = parse_arguments()
    send_email(args)
