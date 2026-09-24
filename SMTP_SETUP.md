# SMTP email verification setup

The app sends a verification email immediately after registration. The message contains a signed, single-use link that expires after 24 hours.

## Gmail setup

Use a Gmail account dedicated to sending application email. Enable two-step verification on that account, create a Google **App Password**, and use the 16-character app password below. Do not use the normal Gmail account password.

Set these environment variables before starting Flask:

```bash
export APP_BASE_URL="https://your-public-domain.example"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-sender@gmail.com"
export SMTP_PASSWORD="your-16-character-google-app-password"
export SMTP_FROM="your-sender@gmail.com"
```

Then start the app normally:

```bash
python3 app.py
```

## Behavior

When SMTP is configured and reachable, registration sends an email and shows the verification-pending page. Opening the link marks the account as `email_verified=True` and allows restaurant food submission after the restaurant’s ID and FSSAI files are uploaded.

If SMTP is not configured, the app still creates the account but clearly shows that no email was sent. It never claims that the mailbox was confirmed. For production, keep credentials in environment variables or a secret manager and use a persistent database for users and verification tokens; the current demo project stores data in memory.
