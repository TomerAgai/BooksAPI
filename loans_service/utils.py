import requests

def get_book_details(isbn):
    try:
        response = requests.get(f'http://books:8000/books', params={'ISBN': isbn})
        response.raise_for_status()
        books = response.json()
        if books:
            return books[0]
        else:
            raise ValueError("Book not found")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching book details: {str(e)}")