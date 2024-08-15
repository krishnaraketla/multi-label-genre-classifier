from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from smash_words_genres_scraper import get_genres
import json
import pandas as pd
from tqdm import tqdm
import os

# Set up Selenium with Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = Service('/Users/krishna/Downloads/chromedriver-mac-arm64/chromedriver')  # Update with your chromedriver path
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_description(url):
    driver.get(url)
    
    try:
        # Wait for the page to load
        time.sleep(5)
        
        # Scroll down the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Try to find the description using different methods
        description_divs = driver.find_elements(By.XPATH, '//div[@class="mt-2" and contains(@style, "white-space: pre-wrap;")]')
        
        if not description_divs:
            # If not found, try to switch to iframe (if any)
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                driver.switch_to.frame(iframe)
                description_divs = driver.find_elements(By.XPATH, '//div[@class="mt-2" and contains(@style, "white-space: pre-wrap;")]')
                if description_divs:
                    break
                driver.switch_to.default_content()
        
        description = ""
        for div in description_divs:
            # Use JavaScript to get the text content
            description += driver.execute_script("return arguments[0].textContent;", div) + "\n"
        
        return description.strip()
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""
    
def get_genre_ids(genres, genres_map_file='data/genres_map.json'):
    # Load the genres_map from the JSON file
    with open(genres_map_file, 'r', encoding='utf-8') as jsonfile:
        genres_map = json.load(jsonfile)
    
    genre_ids = []
    
    # Iterate through the genres dictionary
    for genre_url, genre_name in genres.items():
        # Check if the genre_name exists in the genres_map
        if genre_name in genres_map:
            genre_ids.append(genres_map[genre_name]['id'])
    return genre_ids

def load_checkpoint(csv_file):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding='utf-8')
        processed_books = df.shape[0]
        return processed_books
    return 0

if __name__ == "__main__":
    csv_file = 'data/desc_genres_data.csv'
    checkpoint_interval = 100
    
    # Load the books map
    with open('data/books_map.json', 'r', encoding='utf-8') as jsonfile:
        books_map = json.load(jsonfile)
    
    # Check where to start from (if checkpoint exists)
    start_index = load_checkpoint(csv_file)
    print(start_index)
    
    # Create a list to store the data
    data = []
    
    # Iterate over each book in the books_map starting from the checkpoint
    for i, (book_url, book_title) in enumerate(tqdm(list(books_map.items())[start_index:], desc="Processing Books", unit="book"), start=start_index + 1):
        # Get the description and genres
        description = get_description(book_url)
        genres = get_genres(book_url)
        
        # Get genre IDs
        genre_ids = get_genre_ids(genres)
        
        # Append data to the list
        data.append({
            "description": description,
            "genres": ", ".join(map(str, genre_ids))
        })
        
        # Save the checkpoint every 100 books
        if i % checkpoint_interval == 0:
            df = pd.DataFrame(data)
            if os.path.exists(csv_file):
                # Append to the existing CSV without writing the header
                df.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8')
            else:
                # Write with header if the file doesn't exist
                df.to_csv(csv_file, index=False, encoding='utf-8')
            data = []  # Clear the list after saving
            print(f"Checkpoint saved after {i} books")
    
    # Save any remaining data
    if data:
        df = pd.DataFrame(data)
        if os.path.exists(csv_file):
            df.to_csv(csv_file, mode='a', header=False, index=False, encoding='utf-8')
        else:
            df.to_csv(csv_file, index=False, encoding='utf-8')
    
    # Close the browser
    driver.quit()

    print(f"Data saved to '{csv_file}'")