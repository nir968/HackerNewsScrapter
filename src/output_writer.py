import  csv
from typing import List, Dict

FIELDNAMES = ['Title', 'URL', 'Points', 'Author', 'Number of comments', 'Page number']

def write_to_csv(posts: List[Dict], filename: str = 'hacker_news_results.csv'):

    if not posts:
        print("No posts to write to CSV.")
        return
    
    try:
        with open(filename,'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            for post in posts:
                writer.writerow(post)

    except Exception as e:
        print(f"Error writing to CSV file: {e}")    
    