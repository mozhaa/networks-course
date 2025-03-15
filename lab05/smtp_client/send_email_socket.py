import argparse
import socket


def send_email(
    from_email: str,
    to_email: str,
    subject: str,
    message: str,
    message_type: str,
    smtp_host: str,
    smtp_port: int,
) -> None:
    smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    smtp_socket.connect((smtp_host, smtp_port))

    smtp_socket.recv(1024).decode()

    smtp_socket.send(f"HELO {smtp_host}\r\n".encode())
    smtp_socket.recv(1024).decode()

    smtp_socket.send(f"MAIL FROM:<{from_email}>\r\n".encode())
    smtp_socket.recv(1024).decode()

    smtp_socket.send(f"RCPT TO:<{to_email}>\r\n".encode())
    smtp_socket.recv(1024).decode()

    smtp_socket.send(b"DATA\r\n")
    smtp_socket.recv(1024).decode()

    html_header = '\r\nContent-Type: text/html; charset="utf-8"' if message_type == "html" else ""
    email_message = f"From: {from_email}\r\nTo: {to_email}\r\nSubject: {subject}{html_header}\r\n\r\n{message}\r\n.\r\n"

    smtp_socket.send(email_message.encode())
    smtp_socket.recv(1024).decode()

    smtp_socket.send(b"QUIT\r\n")
    smtp_socket.recv(1024).decode()

    smtp_socket.close()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--to-email", type=str, required=True, help="email of receiver")
    parser.add_argument("--from-email", type=str, required=True, help="email of sender")
    parser.add_argument("--subject", type=str, required=True, help="mail subject")
    parser.add_argument("--message", type=str, help="message text")
    parser.add_argument("--message-file", type=str, help="file to read message from")
    parser.add_argument("--message-type", type=str, choices=["plain", "html"], default="plain", help="message type")
    parser.add_argument("--smtp-host", type=str, required=True, help="host of smtp server")
    parser.add_argument("--smtp-port", type=int, required=True, help="port of smtp server")
    args = parser.parse_args()
    if args.message is None and args.message_file is None:
        raise RuntimeError("Provide --message of --message-file flag")
    return args


if __name__ == "__main__":
    args = parse_arguments()
    if args.message is not None:
        message = args.message
    else:
        with open(args.message_file, "r+") as f:
            message = f.read()

    try:
        send_email(
            args.from_email,
            args.to_email,
            args.subject,
            message,
            args.message_type,
            args.smtp_host,
            args.smtp_port,
        )
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
