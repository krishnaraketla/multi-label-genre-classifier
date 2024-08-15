import json
import csv
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Set up Selenium with Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
service = Service('/Users/krishna/Downloads/chromedriver-mac-arm64/chromedriver')  # Update with your chromedriver path
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_books(url):
    driver.get(url)
    time.sleep(3)  # Wait for JavaScript to load content

    books = {}
    a_tags = driver.find_elements(By.TAG_NAME, 'a')
    for a_tag in a_tags:
        href = a_tag.get_attribute('href')
        if href and '/books/view/' in href:
            book_name = a_tag.text.strip()
            books[href] = book_name  # Store the full URL and book name
    
    return books

def save_checkpoint(checkpoint, filename='data/checkpoint_genres.json'):
    with open(filename, 'w') as f:
        json.dump(checkpoint, f)

def load_checkpoint(filename='data/checkpoint_genres.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_to_csv(df, csv_file='data/books_data.csv'):
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8')
    else:
        df.to_csv(csv_file, index=False, encoding='utf-8')

if __name__ == "__main__":
    # Load genres from JSON file
    with open('data/genres_map.json', 'r', encoding='utf-8') as jsonfile:
        genres_map = json.load(jsonfile)

    # Load checkpoint
    checkpoint = load_checkpoint()

    # Initialize data storage
    all_data = []

    # Start from the last saved checkpoint
    start_index = checkpoint.get('last_genre_index', 0)

    # Iterate over the genres starting from the last checkpoint
    for idx, (genre_name, genre_info) in enumerate(list(genres_map.items())[start_index:], start=start_index):
        print(f"Processing genre {idx+1}/{len(genres_map)}: {genre_name}")

        # Get books for the current genre
        books_map = get_books(genre_info['genre_url'])

        # Append books to data list
        for url, title in books_map.items():
            all_data.append({'title': title.replace('\n', ' '), 'url': url, 'genre': genre_name})

        # Save checkpoint every 10 genres
        if (idx + 1) % 10 == 0 or (idx + 1) == len(genres_map):
            # Create a DataFrame
            df = pd.DataFrame(all_data)

            # Save to CSV
            save_to_csv(df)

            # Clear the list to free memory
            all_data.clear()

            # Update and save checkpoint
            checkpoint['last_genre_index'] = idx + 1
            save_checkpoint(checkpoint)
            print(f"Checkpoint saved at genre {idx + 1}.")

    # Save any remaining data
    if all_data:
        df = pd.DataFrame(all_data)
        save_to_csv(df)
        all_data.clear()

    # Close the browser
    driver.quit()

    print("Scraping complete. Data saved to 'books_data.csv'")