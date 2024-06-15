import requests
from flask import jsonify

# """""""""""""""""""""""""""" #
"remove the follwoing before submission"
import os
from dotenv import load_dotenv
load_dotenv()

# belongs to a.tomer2000@gmail.com
API_KEY = os.getenv("API_KEY")

# """""""""""""""""""""""""""" #

book_id_counter = 0

def fetch_from_google_books(isbn):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    query = f"?q=isbn:{isbn}"
    try:
        response = requests.get(base_url + query)
        response.raise_for_status()
        if response.status_code == 200 and response.json()['totalItems'] > 0:
            data = response.json()['items'][0]['volumeInfo']
            authors = " and ".join(data.get('authors', ['Unknown'])) 
            publisher = data.get('publisher', 'missing')
            publishedDate = data.get('publishedDate', 'missing')
            if not (publishedDate and ((len(publishedDate) == 10 and "-" in publishedDate) or (len(publishedDate) == 4 and publishedDate.isdigit()))):
                publishedDate = 'missing'

            return authors, publisher, publishedDate
    except:
        if response.json()['totalItems'] == 0:
            return jsonify({"error": "no items returned from Google Book API for given ISBN number"}), 400
    return None, None, None

# def fetch_language_from_openlibrary(isbn):
#     base_url = "https://openlibrary.org/search.json"
#     query = f"?q=isbn:{isbn}&fields=key,title,author_name,language"
#     response = requests.get(base_url + query)
#     if response.status_code == 200:
#         data = response.json()
#         languages = [lang for doc in data['docs'] for lang in doc.get('language', [])]
#         if not languages: 
#             languages.append('missing')
#         return languages
#     return ['missing']

# def generate_summary(book_title, author_name):
#     try:
#         genai.configure(api_key=API_KEY)
#         model = genai.GenerativeModel('gemini-pro')
#         prompt = f"Summarize the book \"{book_title}\" by {author_name} in 5 sentences or less."
#         response = model.generate_content(prompt)
#         return response.text.strip()

#     except Exception as e:
#         print(f"An error occurred while generating the summary: {e}")
#         return "Summary not available."
