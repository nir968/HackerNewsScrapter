import argparse #for config parsing
from typing import List,Dict

from src.scraper import fetch_page, parse_posts_from_html


def filter_posts(posts: List[Dict], min_score: int, max_score: int) -> List[Dict]:
    
    filtered = []

    for post in posts:

        score = post.get('Points', 0)#

        if min_score <= score <= max_score:
            filtered.append(post)

    return filtered



def run_scraping_pipeline(config: argparse.Namespace) -> List[Dict]:

    all_posts = []
    current_page = 1

    print("\n*** Starting Scraping Pipeline ***\n")

    while True:

        if current_page in config.skip_pages:
            print(f"Skipping page {current_page} as requested.")
            current_page += 1
            continue

        print(f"Fetching and processing page {current_page}...")
        html_content = fetch_page(current_page)
        #Stop Condition1
        if html_content is None:
            print("Stopping: Received no content or network error.")
            break

        raw_posts = parse_posts_from_html(html_content, current_page)

        newly_filtered_posts = filter_posts(raw_posts,config.min_score,config.max_score)

        #print(f"DEBUG: Filtered posts from page {current_page}: {len(newly_filtered_posts)}")#debug
        #print(f"DEBUG: Total posts so far: {len(all_posts)}")   #debug

        for post in newly_filtered_posts:
            all_posts.append(post)
        #Stop Condition2
            if len(all_posts) >= config.max_posts:
                print("Reached maximum post count. Stopping.")
                return all_posts
            
        current_page += 1

        #Stop Condition3
        if not raw_posts and current_page > 1:
            print("No more posts found. Ending scraping.")
            break

    return all_posts