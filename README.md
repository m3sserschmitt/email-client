# email-client

This is a email client application with basic IMAP4_SSL and SMTP_SSL implementation.
It can be used to login to your Gmail acount (configured by default, see 'config.json') for reading and writing emails.
Google prevents connections from 'less secure application', so you need to enable 'alow less secure application' option from your google account.

Also, the application can be configured for other emails providers, as long as their servers use standard SMTP and IMAP protocols
(Yahoo, for example don't).
