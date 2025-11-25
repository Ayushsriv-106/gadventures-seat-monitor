import os
import re
import smtplib
import ssl
from email.message import EmailMessage
import asyncio
from playwright.async_api import async_playwright

URL = "https://www.gadventures.com/trips/egypt-jordan-pyramids-petra/DJAC/#departures-container"

async def check_seats(url: str) -> int | None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        body_text = await page.inner_text("body")
        await browser.close()

    # Detect "7+ Available", "5 Available", etc.
    m = re.search(r"(\d+)\+?\s+Available", body_text, re.I)
    if m:
        return int(m.group(1))
    return None

def send_email(seats: int | None):
    gmail_user = os.environ["GMAIL_USER"]
    gmail_pass = os.environ["GMAIL_APP_PASSWORD"]
    to = os.environ.get("RECIPIENT_EMAIL", gmail_user)

    subject = "Daily G Adventures Seat Report"
    if seats is None:
        body = (
            "No availability number detected today.\n"
            f"Check manually: {URL}"
        )
    else:
        body = (
            f"Seats currently showing as: {seats}\n\n"
            f"URL: {URL}"
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = to
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)

    print("Daily email sent.")

async def main():
    seats = await check_seats(URL)
    print("Detected seats:", seats)
    send_email(seats)

if __name__ == "__main__":
    asyncio.run(main())
