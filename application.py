#!/usr/bin/env python

import json
import threading

from gui import *
from email_services import SendEmailServices
from email_services import ReadEmailServices
from email_services import BasicEmailHeadersParser


class Application:
    def __init__(self, config_file):
        self.__title = str()
        self.__imap_host = str()
        self.__smtp_host = str()
        self.__imap_port = int()
        self.__smtp_port = int()
        self.__indexed_mails = dict()
        self.__indexed_mails_count = dict()

        self.__import_settings(config_file)

        self.__main_window = MainWindow()
        self.__login_screen = LoginScreen(self.__main_window)
        self.__write_email_screen = WriteEmailScreen(self.__main_window)
        self.__mailbox_screen = MailboxScreen(self.__main_window)
        self.__email_rendering_screen = EmailRenderingScreen(self.__main_window)
        self.__send_email_services = SendEmailServices()
        self.__read_email_services = ReadEmailServices()

        self.__setup_main_window()
        self.__setup_login_screen()
        self.__setup_mailbox_screen()
        self.__setup_write_email_screen()
        self.__setup_email_rendering_screen()

    def __setup_main_window(self):
        self.__main_window.title(self.__title)
        self.__main_window.minsize(400, 500)

    def __setup_email_services(self):
        # def connecting():
        #     self.__login_screen.login_button["state"] = "disabled"

        imap_connected = self.__read_email_services.connect_to_server(self.__imap_host, self.__imap_port)
        smtp_connected = self.__send_email_services.connect_to_server(self.__smtp_host, self.__smtp_port)

        if not imap_connected and not smtp_connected:
            self.__login_screen.status["text"] = "Connection error"

        #     self.__login_screen.login_button["state"] = "normal"
        #
        # threading.Thread(target=connecting).start()

    def __setup_login_screen(self):
        self.__login_screen.login_button["command"] = self.__login_screen_login_button

    def __setup_write_email_screen(self):
        self.__write_email_screen.send_email_button["command"] = self.__write_email_screen_send_email_button
        self.__write_email_screen.back_button["command"] = self.__write_email_screen_back_button

    def __setup_mailbox_screen(self):
        self.__mailbox_screen.mails_list.bind("<<TreeviewSelect>>", self.__mailbox_screen_item_selected_event)
        self.__mailbox_screen.mailboxes_list.bind("<<ComboboxSelected>>", self.__mailbox_screen_mailbox_selected)
        self.__mailbox_screen.write_button["command"] = self.__mailbox_screen_write_email_button
        self.__mailbox_screen.refresh_button["command"] = self.__mailbox_screen_refresh_button
        self.__mailbox_screen.more_button["command"] = self.__mailbox_screen_show_more_button
        self.__mailbox_screen.logout_button["command"] = self.__mailbox_screen_logout_button

    def __setup_email_rendering_screen(self):
        self.__email_rendering_screen.back_button["command"] = self.__email_rendering_screen_back_button
        self.__email_rendering_screen.respond_button["command"] = self.__email_rendering_screen_respond_button
        self.__email_rendering_screen.redirect_button["command"] = self.__email_rendering_screen_redirect_button

    def __login_screen_login_button(self):
        def logging_in():
            password = self.__login_screen.password.get()
            username = self.__login_screen.username.get()

            self.__setup_email_services()

            smtp_logged_in = self.__send_email_services.login_to_server(username, password)
            imap_logged_in = self.__read_email_services.login_to_server(username, password)

            if not smtp_logged_in and not imap_logged_in:
                self.__login_screen.status["text"] = "SMTP and IMAP login failed"
                return

            self.__write_email_screen.from_address.insert(0, self.__login_screen.username.get())

            self.__login_screen.grid_remove()
            self.__main_window.minsize(800, 500)
            if imap_logged_in:
                self.__mailbox_screen.show()

                mailboxes = self.__read_email_services.get_mailboxes()
                self.__mailbox_screen.mailboxes_list["values"] = tuple(mailboxes)
                for mailbox in mailboxes:
                    self.__indexed_mails[mailbox] = []
                    self.__indexed_mails_count[mailbox] = 0
                self.__mailbox_screen.mailboxes_list.set(mailboxes[0])
                self.__mailbox_screen_mailbox_selected()
                return

            if not imap_logged_in and smtp_logged_in:
                self.__write_email_screen.show()

        threading.Thread(target=logging_in).start()

    def __populate_mailbox_screen(self, start_index, stop_index, selected_mailbox):
        self.__mailbox_screen.mailboxes_list["state"] = "disabled"
        self.__mailbox_screen.refresh_button["state"] = "disabled"
        self.__mailbox_screen.more_button["state"] = "disabled"
        self.__mailbox_screen.logout_button["state"] = "disabled"

        basic_headers_parser = BasicEmailHeadersParser()
        while start_index > stop_index:
            email_headers = self.__read_email_services.get_email_headers(start_index)
            basic_headers_parser.parse(email_headers)

            self.__indexed_mails[selected_mailbox].append(email_headers)
            self.__mailbox_screen.mails_list.insert("", "end", str(start_index),
                                                    text=basic_headers_parser.from_address,
                                                    values=(
                                                        basic_headers_parser.subject,
                                                        basic_headers_parser.date)
                                                    )

            start_index -= 1

        self.__mailbox_screen.mailboxes_list["state"] = "readonly"
        self.__mailbox_screen.refresh_button["state"] = "normal"
        self.__mailbox_screen.more_button["state"] = "normal"
        self.__mailbox_screen.logout_button["state"] = "normal"

    def __mailbox_screen_mailbox_selected(self, event=None):
        selected_mailbox = self.__mailbox_screen.mailboxes_list.get()
        emails_count = self.__read_email_services.select_mailbox(selected_mailbox)

        self.__mailbox_screen.mails_list.delete(*self.__mailbox_screen.mails_list.get_children())

        if not emails_count:
            self.__mailbox_screen.mails_list.insert("", "end", text="No mails available")
            return

        if self.__indexed_mails_count[selected_mailbox] != emails_count:
            self.__indexed_mails[selected_mailbox] = []
            self.__indexed_mails_count[selected_mailbox] = emails_count

            stop_index = emails_count - 25
            if stop_index < 1:
                stop_index = 1

            threading.Thread(target=self.__populate_mailbox_screen, args=(emails_count, stop_index,
                                                                          selected_mailbox)).start()
        else:
            basic_headers_parser = BasicEmailHeadersParser()
            for email_headers in self.__indexed_mails[selected_mailbox]:
                basic_headers_parser.parse(email_headers)
                self.__mailbox_screen.mails_list.insert("", "end", str(emails_count),
                                                        text=basic_headers_parser.from_address,
                                                        values=(
                                                            basic_headers_parser.subject,
                                                            basic_headers_parser.date)
                                                        )
                emails_count -= 1

    def __mailbox_screen_refresh_button(self):
        self.__mailbox_screen_mailbox_selected()

    def __mailbox_screen_item_selected_event(self, virtual_event=None):
        def selecting_item():
            selected_mailbox = self.__mailbox_screen.mailboxes_list.get()
            mail_index = int(self.__mailbox_screen.mails_list.selection()[0])
            mail_content = self.__read_email_services.get_body(mail_index)
            local_mail_index = self.__indexed_mails_count[selected_mailbox] - mail_index
            mail_header = self.__indexed_mails[selected_mailbox][local_mail_index]

            self.__mailbox_screen.grid_remove()
            self.__email_rendering_screen.set_header(mail_header)
            self.__email_rendering_screen.set_content(mail_content, mail_header.get_content_subtype())
            self.__email_rendering_screen.show()

        threading.Thread(target=selecting_item).start()

    def __mailbox_screen_write_email_button(self):
        self.__mailbox_screen.grid_remove()
        self.__write_email_screen.show()

    def __mailbox_screen_show_more_button(self):
        selected_mailbox = self.__mailbox_screen.mailboxes_list.get()
        local_email_count = self.__indexed_mails_count[selected_mailbox]
        start_index = local_email_count - len(self.__indexed_mails[selected_mailbox])

        stop_index = start_index - 25
        if stop_index < 1:
            stop_index = 1

        threading.Thread(target=self.__populate_mailbox_screen,
                         args=(start_index, stop_index, selected_mailbox)).start()

    def __mailbox_screen_logout_button(self):
        self.__login_screen.clear_all()
        self.__mailbox_screen.clear_all()
        self.__write_email_screen.clear_all()
        self.__email_rendering_screen.clear_all()

        self.__send_email_services.logout()
        self.__read_email_services.logout()

        self.__mailbox_screen.grid_remove()
        self.__login_screen.show()

    def __write_email_screen_send_email_button(self):
        def sending_email():
            from_address = self.__write_email_screen.from_address.get()
            to_address = self.__write_email_screen.to_address.get()
            cc = self.__write_email_screen.cc.get()
            bcc = self.__write_email_screen.bcc.get()
            subject = self.__write_email_screen.subject.get()
            text = self.__write_email_screen.text.get(1.0, END)

            email_msg = self.__send_email_services.create_email_message(from_address, to_address, subject, text, cc,
                                                                        bcc, _charset="utf-8")
            self.__send_email_services.send_email(email_msg)

            self.__write_email_screen.clear_all()

        threading.Thread(target=sending_email).start()

        self.__write_email_screen.grid_remove()
        self.__mailbox_screen.show()

    def __write_email_screen_back_button(self):
        self.__write_email_screen.grid_remove()
        self.__write_email_screen.clear_all()
        self.__mailbox_screen.show()

    def __email_rendering_screen_back_button(self):
        self.__email_rendering_screen.grid_rmv()
        self.__mailbox_screen.show()

    def __email_rendering_screen_respond_button(self):
        selected_mailbox = self.__mailbox_screen.mailboxes_list.get()
        mail_index = int(self.__mailbox_screen.mails_list.selection()[0])
        local_mail_index = self.__indexed_mails_count[selected_mailbox] - mail_index
        mail_header = self.__indexed_mails[selected_mailbox][local_mail_index]

        self.__email_rendering_screen.grid_remove()
        self.__write_email_screen.show()
        self.__write_email_screen.to_address.insert(0, mail_header["From"])
        self.__write_email_screen.subject.insert(0, "Re:" + mail_header["Subject"])

    def __email_rendering_screen_redirect_button(self):
        selected_mailbox = self.__mailbox_screen.mailboxes_list.get()
        mail_index = int(self.__mailbox_screen.mails_list.selection()[0])
        local_mail_index = self.__indexed_mails_count[selected_mailbox] - mail_index
        mail_header = self.__indexed_mails[selected_mailbox][local_mail_index]
        mail_content = self.__read_email_services.get_body(mail_index)

        self.__email_rendering_screen.grid_remove()
        self.__write_email_screen.show()
        self.__write_email_screen.subject.insert(0, "Fwd:" + mail_header["Subject"])
        self.__write_email_screen.text.insert(1.0, mail_content)

    def __import_settings(self, file: str):
        with open(file, "r") as file:
            config = json.load(file)
            title = list(config.keys())[0]
            config = config[title]

            self.__title = title
            self.__imap_host = config["imap"]["host"]
            self.__imap_port = config["imap"]["port"]
            self.__smtp_host = config["smtp"]["host"]
            self.__smtp_port = config["smtp"]["port"]

    def run(self):
        self.__login_screen.show()
        self.__main_window.mainloop()
