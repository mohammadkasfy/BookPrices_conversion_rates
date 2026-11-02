import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import ezgmail
from pathlib import Path



def scrape_books():
    """Download the first page and return a list of book dictionaries."""

    url = "https://books.toscrape.com/"

    response = requests.get(url, timeout=20)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    book_cards = soup.select("article.product_pod")

    if not book_cards:
        raise ValueError("No book cards were found. Check the page structure.")

    book_list = []

    for card in book_cards:
        # Find the HTML elements we need.
        title_link = card.select_one("h3 a")
        price = card.select_one(".price_color")
        stock = card.select_one(".availability")

        # Read their values.
        title = title_link["title"]

        price_text = price.get_text(strip=True)
        price_gbp = float(price_text.replace("£", ""))

        availability = stock.get_text(strip=True)

        # Turn the relative link into a complete URL.
        book_url = urljoin(url, title_link["href"])

        # Store this book's details in a dictionary.
        book_details = {
            "title": title,
            "price_gbp": price_gbp,
            "availability": availability,
            "url": book_url
        }

        # Add the dictionary to our list.
        book_list.append(book_details)

    return book_list

def get_exchange_rate():
    """Get the number of Turkish Lira equivalent to one British pound."""

    url = "https://open.er-api.com/v6/latest/GBP"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()

    if data.get("result") != "success":
        raise ValueError("The API could not provide exchange rates.")

    rate = data["rates"]["TRY"]

    return rate


def display_books(books, exchange_rate):
    """Display each book's price in pounds and turkish lira."""

    print(f"Found {len(books)} books.")
    print(f"Exchange rate: 1 GBP = TRY {exchange_rate:,.2f}")
    # , → add thousands separators.
    # .2f → display two decimal places.
    
    print("Rates By Exchange Rate API: https://www.exchangerate-api.com")
    print()

    for number, book in enumerate(books, start=1):
        price_try = book["price_gbp"] * exchange_rate

        print(f"{number}. {book['title']}")
        print(f"   Price in pounds: GBP {book['price_gbp']:.2f}")
        print(f"   Price in Turkish lira:  TRY {price_try:,.2f}")
        print(f"   Availability: {book['availability']}")
        print(f"   Link: {book['url']}")
        print()

def email_books(books, exchange_rate):
    """Create an email containing all the book prices."""

    recipient = "mohammadkasfy@gmail.com"

    subject = "Book Price Watcher"

    body = "Here are the books from the first page.\n"
    body += "These are demonstration book prices.\n\n"
    body += f"Exchange rate: 1 GBP = TRY {exchange_rate:,.2f}\n"
    body += (
        "Rates By Exchange Rate API: "
        "https://www.exchangerate-api.com\n\n"
    )

    for number, book in enumerate(books, start=1):
        price_try = book["price_gbp"] * exchange_rate

        body += f"{number}. {book['title']}\n"
        body += f"GBP {book['price_gbp']:.2f}\n"
        body += f"TRY {price_try:,.2f}\n"
        body += f"Availability: {book['availability']}\n"
        body += f"Link: {book['url']}\n\n"

    # Locate the Gmail files beside main.py.
    
    ezgmail.send(recipient, subject, body)

    print(f"Email sent to {recipient}")

def main():
    books = scrape_books()
    exchange_rate = get_exchange_rate()
    display_books(books, exchange_rate)
    #email_books(books, exchange_rate)


if __name__ == "__main__":
    interval_seconds = 24 * 60 * 60

    try:        
        while True:
            try:
                main()
            except Exception as error:
                print(f"The check failed: {error}")

            print("Waiting 24 hours before the next check...")
            time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting...")    