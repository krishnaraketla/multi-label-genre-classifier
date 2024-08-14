from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from smash_words_genres_scraper import get_genres

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
    
if __name__ == "__main__":
    base_url = 'https://www.smashwords.com/books/view/1592962'
    
    # Get the description
    # description = get_description(base_url)
    genres = get_genres(base_url)
    
    print(genres)

    # Close the browser
    driver.quit()