import argparse
import ftplib
import os

help_message = """\
LIST - list directory
UPLOAD <filename> - upload file to server
DOWNLOAD <filename> - download file from server
EXIT - exit client
HELP - show this message
"""


def list_files(ftp):
    ftp.retrlines("LIST")


def upload_file(ftp, file_path: str):
    with open(file_path, "rb") as file:
        ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)
    print(f"File '{file_path}' was successfully loaded to the server")


def download_file(ftp, file_name: str):
    with open(file_name, "wb") as file:
        ftp.retrbinary(f"RETR {file_name}", file.write)
    print(f"File '{file_name}' was successfully downloaded from the server")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FTP Client")
    parser.add_argument("host", type=str, help="ftp-server address")
    parser.add_argument("user", type=str, help="username")
    parser.add_argument("password", type=str, help="password")

    return parser.parse_args()


def main(ftp_host: str, ftp_user: str, ftp_password: str):
    ftp = ftplib.FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_password)
    print(help_message)

    while True:
        command = input("> ")
        parts = command.split()
        command_name = parts[0].strip().upper()

        if command_name == "LIST":
            list_files(ftp)
        elif command_name == "UPLOAD":
            filename = command[len(command_name) + 1 :].strip()
            upload_file(ftp, filename)
        elif command_name == "DOWNLOAD":
            filename = command[len(command_name) + 1 :].strip()
            download_file(ftp, filename)
        elif command_name == "EXIT":
            print("Exiting...")
            break
        elif command_name == "HELP":
            print(help_message)
        else:
            print("Unknown command. Type 'HELP' to get available commands")

    ftp.quit()


if __name__ == "__main__":
    args = parse_arguments()
    main(args.host, args.user, args.password)
