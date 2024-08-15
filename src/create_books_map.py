import csv
import json

def create_books_map(csv_file='data/books_data.csv', json_file='data/books_map.json'):
    books_map = {}

    # Open the CSV file and read the data
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        # Iterate through each row and build the dictionary
        for row in csv_reader:
            url = row['url']
            title = row['title']
            books_map[url] = title
    
    # Save the dictionary to a JSON file
    with open(json_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(books_map, jsonfile, ensure_ascii=False, indent=4)
    
    print(f"Books map has been created and saved to '{json_file}'.")

if __name__ == "__main__":
    create_books_map()