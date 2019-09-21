#!/usr/bin/env python

import smtplib
from email.mime.text import MIMEText
from termcolor import colored
from mailparser import parse_from_bytes
import typing
import imaplib
import re


"""
    Acest modul contine toate functionalitatile de citire si trimitere pentru email-uri
"""


class SendEmailServices:
    def __init__(self):
        self.__server = smtplib.SMTP_SSL()
        self.__show_details = True
        self.__is_connected = False

    def show_details(self, show_details: bool) -> None:
        self.__show_details = show_details

    def __output(self, output: typing.Any) -> None:
        if self.__show_details:
            print(output)

    @staticmethod
    def create_email_message(_from: str, _to: str, _subject: str, _text: str, _cc: str = "", _bcc: str = "",
                             _subtype: str = "plain", _charset: str = "us-ascii") -> MIMEText:
        email_message = MIMEText(_text, _subtype, _charset)
        email_message["Subject"] = _subject
        email_message["From"] = _from
        email_message["To"] = _to
        email_message["Cc"] = _cc
        email_message["Bcc"] = _bcc
        return email_message

    def connect_to_server(self, address: str, port: int = 465) -> bool:
        if not isinstance(address, str) or not isinstance(port, int):
            raise SendEmailServicesException(f"wrong arg types: ({type(address)}, {type(port)}); (str, int) required")

        try:
            self.__server = smtplib.SMTP_SSL(address)
            code, message = self.__server.connect(address, port)
            ok = 200 <= code < 300

            if ok:
                code = colored(str(code), "green")
            else:
                code = colored(str(code), "red")

            self.__output(f"[+] connected successfully to '{address}'")
            self.__output(f"[+] connection result: code: {code}, server response: {message.decode()}")

            self.__is_connected = True

            return ok
        except Exception:
            self.__output(colored(f"[-] connection to '{address}' failed", "red"))
            return False

    def is_connected(self) -> bool:
        return self.__is_connected

    def login_to_server(self, username: str, password: str) -> bool:
        if not isinstance(username, str) or not isinstance(password, str):
            raise SendEmailServicesException(
                f"wrong arg types: ({type(username)}, {type(password)}); (str, str) required"
            )

        try:
            code, message = self.__server.login(username, password)
            ok = 200 <= code < 300

            if ok:
                code = colored(str(code), "green")
            else:
                code = colored(str(code), "red")

            self.__output(f"[+] login result: code: {code}, server response: {message.decode()}")

            return ok
        except Exception:
            self.__output(colored("[-] login failed", "red"))
            return False

    def send_email(self, email_message: MIMEText) -> bool:
        if not isinstance(email_message, MIMEText):
            raise SendEmailServicesException(f"wrong arg type: {type(email_message)}; {MIMEText} required")

        try:
            self.__server.send_message(email_message)
            self.__output("[+] email sent successfully")
            return True
        except Exception:
            self.__output(colored("[-] error sending email", "red"))
            return False

    def logout(self):
        try:
            self.__server.close()
            self.__output("[+] SMTP logout succeeded")
            self.__is_connected = False
            return True
        except Exception:
            self.__output(colored("[-] SMTP logout failed", "red"))
            return False


class ReadEmailServices:
    def __init__(self):
        self.__server = None
        self.__show_details = True
        self.__is_connected = False

    def show_details(self, show_details: bool) -> None:
        if not isinstance(show_details, bool):
            raise ReadEmailServicesException(f"wrong arg type: {type(show_details)}; {bool} required")

        self.__show_details = show_details

    def __output(self, output: typing.Any) -> None:
        if self.__show_details:
            print(output)

    def connect_to_server(self, address: str, port: int = 993) -> bool:
        if not isinstance(address, str) or not isinstance(port, int):
            raise ReadEmailServicesException(f"wrong arg type: {type(address)}, {type(port)}; (str, int) required")

        try:
            self.__server = imaplib.IMAP4_SSL(address, port)
            self.__output(f"[+] connected successfully to '{address}'")

            self.__is_connected = True

            return True
        except Exception:
            self.__output(colored(f"[-] connection to '{address}' failed", "red"))
            return False

    def is_connected(self) -> bool:
        return self.__is_connected

    @staticmethod
    def __highlight_status(status) -> str:
        if status == "OK":
            status = colored(status, "green")
        else:
            status = colored(status, "red")
        return status

    def login_to_server(self, username: str, password: str) -> bool:
        if not isinstance(username, str) or not isinstance(password, str):
            raise ReadEmailServicesException(f"wrong arg type: {type(username)}, {type(password)}; (str, str) required")

        try:
            status, response = self.__server.login(username, password)
            _status = self.__highlight_status(status)

            self.__output(f"[+] login result: status: {_status}, server response: {response}")
            return status == "OK"

        except Exception:
            self.__output(colored("[-] login failed", "red"))
            return False

    def get_mailboxes(self) -> list:
        try:
            status, response = self.__server.list()
            status = self.__highlight_status(status)

            self.__output(f"[+] mailboxes listing result: status: {status}, server response: {response}")
        except Exception:
            self.__output(colored("mailbox listing failed", "red"))
            return []

        mailboxes = list()
        for mailbox in response:
            if isinstance(mailbox, bytes):
                mailbox = mailbox.decode("utf-8")

            mailboxes.append(re.findall('(?:")(.+?)(?:")', mailbox)[-1])
        return mailboxes

    def select_mailbox(self, mailbox: str = "INBOX") -> int:
        if not isinstance(mailbox, str):
            raise ReadEmailServicesException(f"wrong arg type: {type(mailbox)}; str required")

        try:
            status, response = self.__server.select('"' + mailbox + '"')
            status = self.__highlight_status(status)

            self.__output(f"[+] mailbox selecting result: status {status}, server response: {response}")
            return int(response[0])

        except Exception:
            self.__output(colored(f"[-] error selecting mailbox: {mailbox}", "red"))
            return 0

    def get_email_headers(self, index: int = 1) -> MIMEText:
        if not isinstance(index, int):
            raise ReadEmailServicesException(f"wrong arg type: {type(index)}; int required")

        email_headers = MIMEText("")
        if index <= 0:
            return email_headers

        status, response = self.__server.fetch(str(index).encode("utf-8"),
                                               "(BODY[HEADER.FIELDS (SUBJECT FROM TO DATE CONTENT-TYPE)])")
        if not response[0]:
            return email_headers

        headers = parse_from_bytes(response[0][1]).headers
        for [header_name, header_value] in headers.items():
            if header_name.lower() == "content-type":
                header_value = header_value.split("boundary")[0]
                email_headers.set_type(header_value)
                continue
            email_headers[header_name] = header_value

        return email_headers

    def get_emails_headers(self, count: int = 1) -> list:
        if not isinstance(count, int):
            raise ReadEmailServicesException(f"wrong arg type: {type(count)}; int required")

        headers = list()
        if count <= 0:
            return headers
        i = 1

        while True:
            header = self.get_email_headers(i)
            headers.append(header)

            if i == count:
                break

            i += 1
        # headers.reverse()
        return headers

    def get_body(self, index: int = 1) -> str:
        if not isinstance(index, int):
            raise ReadEmailServicesException(f"wrong arg type: {type(index)}; int required")

        try:
            status, data = self.__server.fetch(str(index).encode("utf-8"), "(RFC822)")
            email_message = parse_from_bytes(data[0][1])
            return str(email_message.body)
        except Exception:
            self.__output(colored("[-] body fetching failed", "red"))
            return ""

    def logout(self):
        try:
            self.__server.logout()
            self.__output("[+] IMAP logout succeeded")
            self.__is_connected = False
            return True
        except Exception:
            self.__output(colored("[-] IMAP logout failed", "red"))
            return False


class BasicEmailHeadersParser(object):
    def __init__(self, content: MIMEText = None):
        self.from_address = str()
        self.subject = str()
        self.to_address = str()
        self.date = str()

        if content:
            self.parse(content)

    @staticmethod
    def __process_charset(string: str):
        _result = ""
        if not string:
            return _result
        result = [string[j] for j in range(len(string)) if ord(string[j]) in range(65536)]
        for char in result:
            _result += char
        return _result

    @staticmethod
    def __parse_regular(string: str, max_length=35):
        if len(string) > max_length > 0:
            string = string[:max_length - 3] + "..."

        return string

    @staticmethod
    def __parse_date(date: str) -> str:
        date = date.split(" ")
        date = " ".join(date[:4])

        return date

    @staticmethod
    def __contain_alphanumerics(string: str) -> bool:
        for char in string:
            if char.isalnum():
                return True
        return False

    @staticmethod
    def __parse_address(address: str) -> str:
        if not address:
            return "No address"

        if "<" in address and ">" in address:
            [name, email] = address.split("<", 1)

            if not BasicEmailHeadersParser.__contain_alphanumerics(name):
                email = email.split(">", 1)[0]
                return email

            name.strip(" ")

            return name
        return address

    @staticmethod
    def __parse_subject(subject: str) -> str:
        if not subject:
            return "No subject"
        return subject

    def parse(self, content: MIMEText) -> None:
        if not isinstance(content, MIMEText):
            raise BasicEmailHeadersParserException(f"wrong arg type: {type(content)}; MIMEText required")

        self.from_address = self.__parse_regular(self.__parse_address(self.__process_charset(content["From"])))
        self.subject = self.__parse_regular(self.__parse_subject(self.__process_charset(content["Subject"])))
        self.date = self.__parse_regular(self.__parse_date(self.__process_charset(content["Date"])))
        self.to_address = self.__parse_regular(self.__parse_address(self.__process_charset(content["To"])))


class SendEmailServicesException(Exception):
    def __init__(self, e):
        super().__init__(e)


class ReadEmailServicesException(Exception):
    def __init__(self, e):
        super().__init__(e)


class BasicEmailHeadersParserException(Exception):
    def __init__(self, e):
        super().__init__(e)
