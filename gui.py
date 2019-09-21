#!/usr/bin/env python

from tkinter import *
from tkinter import ttk
from email.mime.text import MIMEText
from tkinterhtml import HtmlFrame
from bs4 import BeautifulSoup


"""
    Acest modul contine implementarea interfetei grafice
"""


class MainWindow(Tk):  # implemtarea ferestrei principale
    def __init__(self):
        super().__init__()

        self.__setup_root_window()

    def __setup_root_window(self):  # setarea unor proprietati ale ferestrei
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


class LoginScreen(ttk.Frame):  # implemantarea frame-ului de login
    def __init__(self, parent: MainWindow):
        super().__init__(parent)

        self.login_group = ttk.Frame(self)
        self.username = ttk.Entry(self.login_group)
        self.password = ttk.Entry(self.login_group)
        self.login_button = ttk.Button(self.login_group)
        self.status = ttk.Label(self.login_group)

        self.__setup__login_screen()

    def __setup__login_screen(self):  # setarea proprietatilor de baza
        username_label = ttk.Label(self.login_group)
        password_label = ttk.Label(self.login_group)

        self.configure(borderwidth=3, relief="sunken")

        self.login_group.configure(borderwidth=3, relief="raised")
        self.password.configure(show="*")
        self.login_button.configure(text="Login")
        self.status.configure(text="Enter your username and password")
        username_label.configure(text="Username:")
        password_label.configure(text="Password:")

        self.login_group.grid(row=1, column=1, sticky=(N, S, E, W))
        self.username.grid(row=1, column=1, sticky=(E, W))
        self.password.grid(row=2, column=1, sticky=(E, W))
        self.login_button.grid(row=3, column=0, columnspan=2, pady=4)

        username_label.grid(row=1, column=0)
        password_label.grid(row=2, column=0)

        self.status.grid(row=0, column=0, columnspan=2, sticky=(E, W))

        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=2)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

    def show(self):
        self.grid(column=0, row=0, sticky=(N, S, E, W))

    def clear_all(self):
        self.username.delete(0, "end")
        self.password.delete(0, "end")


class WriteEmailScreen(ttk.Frame):  # implementarea frame-ului de scriere
    def __init__(self, parent: MainWindow):
        super().__init__(parent, padding=(3, 3))

        self.from_address = ttk.Entry(self)
        self.to_address = ttk.Entry(self)
        self.cc = ttk.Entry(self)
        self.bcc = ttk.Entry(self)
        self.text = Text(self)
        self.subject = ttk.Entry(self)
        self.send_email_button = ttk.Button(self)
        self.back_button = ttk.Button(self)

        self.__setup_write_email_screen()

    def __setup_write_email_screen(self):
        self.configure(borderwidth=3, relief="sunken")

        self.send_email_button.configure(text="Send")
        self.back_button.configure(text="Back")

        self.from_address.grid(row=0, column=1, sticky=(W, E))
        self.to_address.grid(row=1, column=1, sticky=(W, E))
        self.cc.grid(row=2, column=1, sticky=(W, E))
        self.bcc.grid(row=3, column=1, sticky=(W, E))
        self.subject.grid(row=4, column=1, sticky=(W, E))

        ttk.Label(self, text="From:").grid(row=0, column=0, sticky=W, pady=1)
        ttk.Label(self, text="To:").grid(row=1, column=0, sticky=W, pady=1)
        ttk.Label(self, text="Cc:").grid(row=2, column=0, sticky=W, pady=1)
        ttk.Label(self, text="Bcc:").grid(row=3, column=0, sticky=W, pady=1)
        ttk.Label(self, text="Subject:").grid(row=4, column=0, sticky=W, pady=1)

        self.text.grid(row=5, column=0, columnspan=2, sticky=(N, S, E, W))
        self.send_email_button.grid(row=7, column=1, sticky=E, pady=2)
        self.back_button.grid(row=7, column=0, sticky=W, pady=2)

        self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)

    def show(self):
        self.grid(column=0, row=0, sticky=(N, S, E, W))

    def clear_all(self):
        self.to_address.delete(0, "end")
        self.cc.delete(0, "end")
        self.bcc.delete(0, "end")
        self.subject.delete(0, "end")
        self.text.delete(1.0, "end")


class MailboxScreen(Frame):  # implementarea frame-ului pentru inbox in care se listeaza
    # mail-urile
    def __init__(self, parent: MainWindow):
        super().__init__(parent)

        self.mailboxes_list = ttk.Combobox(self)
        self.mails_list = ttk.Treeview(self)
        self.write_button = ttk.Button(self)
        self.refresh_button = ttk.Button(self)
        self.more_button = ttk.Button(self)
        self.scrollbar = ttk.Scrollbar(self)
        self.logout_button = ttk.Button(self)

        self.__setup_read_email_screen()

    def __setup_read_email_screen(self):
        self.mailboxes_list.configure(state="readonly")
        self.write_button.configure(text="Write")
        self.mails_list.configure(columns=("Subject", "Date"), yscrollcommand=self.scrollbar.set)
        self.mails_list.heading("Subject", text="Subject")
        self.mails_list.heading("Date", text="Date")
        self.refresh_button.configure(text="Refresh")
        self.more_button.configure(text="Show More")
        self.logout_button.configure(text="Logout")
        self.scrollbar.configure(orient=VERTICAL, command=self.mails_list.yview)

        self.mailboxes_list.grid(column=1, row=0, sticky=W, padx=3)
        self.mails_list.grid(column=0, row=1, columnspan=5, sticky=(N, S, E, W))
        self.write_button.grid(column=4, row=0, sticky=E, padx=1)
        self.refresh_button.grid(column=3, row=0, sticky=E, padx=1)
        self.more_button.grid(column=2, row=0, sticky=E, padx=1)
        self.logout_button.grid(column=0, row=0, sticky=W, padx=1)
        self.scrollbar.grid(column=4, row=1, sticky=(N, S, E))

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

    def show(self):
        self.grid(column=0, row=0, sticky=(N, S, E, W))

    def clear_all(self):
        self.mailboxes_list.delete(0, "end")
        self.mails_list.delete(*self.mails_list.get_children())


class EmailRenderingScreen(ttk.Frame):  # implementarea frame-ului pentru randarea mail-urilor html si text
    def __init__(self, parent: MainWindow):
        super().__init__(parent)
        self.__parent = parent
        self.__email_renderer = HtmlFrame(self)
        self.__text_display = Text(self)
        self.back_button = ttk.Button(self)
        self.respond_button = ttk.Button(self)
        self.redirect_button = ttk.Button(self)
        self.header = ttk.Label(self)

        self.__setup__email_rendering_screen()

    def __setup__email_rendering_screen(self):
        self.configure(borderwidth=3, relief="sunken")

        self.back_button.configure(text="Back")
        self.respond_button.configure(text="Respond")
        self.redirect_button.configure(text="Redirect")

        self.back_button.grid(row=2, column=0, sticky=W)
        self.redirect_button.grid(row=2, column=2, sticky=E)
        self.respond_button.grid(row=2, column=1, sticky=E)
        self.header.grid(row=0, column=0, columnspan=3, sticky=(N, S, E, W))

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

    @staticmethod
    def process_content(content: str):
        bs = BeautifulSoup(content, features="lxml")
        for tag in bs.find_all("style"):
            content = content.replace(str(tag), "")

        return content.split("--- mail_boundary ---")[-1]

    def set_content(self, content: str, subtype: str = "plain"):
        if subtype == "plain":
            self.__text_display.configure(state="normal")
            self.__text_display.delete(1.0, "end")
            self.__text_display.insert(1.0, content)
            self.__text_display.configure(state="disabled")
            self.__text_display.grid(row=1, column=0, columnspan=3, sticky=(N, S, E, W))
        else:
            content = self.process_content(content)
            self.__email_renderer.set_content(content)
            self.__email_renderer.grid(row=1, column=0, columnspan=3, sticky=(N, S, E, W))
            self.__parent.geometry("800x300")

    def grid_rmv(self):
        self.__text_display.grid_remove()
        self.__email_renderer.grid_remove()
        self.grid_remove()

    def set_header(self, header: MIMEText):
        from_address = header["From"]
        to_address = header["To"]
        subject = header["Subject"]
        date = header["Date"]
        self.header["text"] = f"From: {from_address}\nTo: {to_address}\nSubject: {subject}\nDate: {date}"

    def show(self):
        self.grid(column=0, row=0, sticky=(N, S, E, W))

    def clear_all(self):
        self.__text_display.delete(1.0, "end")
        self.header["text"] = ""
