import argparse #for config parsing
from typing import List,Dict

from src.scrapter import fetch_page, parse_posts_from_html


def filter_posts(posts: List[Dict], min_score: int, max_score: int) -> List[Dict]:
    
    filtered = []

    for post in posts:

        score = post.get('Points', 0)

        if min_score <= score <= max_score:
            filtered.append(post)

    return filtered



def run_scrapting_pipeline(config: argparse.Namespace) -> List[Dict]:

    all_posts = []
    curent_page = 1

    print("\n*** Starting Scraping Pipeline ***\n")

    while True:

        if curent_page in config.skip_pages:
            print(f"Skipping page {curent_page} as requested.")
            curent_page += 1
            continue

        print(f"Fetching and processing page {curent_page}...")
        html_content = fetch_page(curent_page)
        #Stop Condition1
        if html_content is None:
            print("Stopping: Received no content or network error.")
            break

        raw_posts = parse_posts_from_html(html_content, curent_page)

        newly_filtered_posts = filter_posts(raw_posts,config.min_score,config.max_score)

        for post in newly_filtered_posts:
            all_posts.append(post)
        #Stop Condition2
            if len(all_posts) >= config.max_posts:
                print("Reached maximum post count. Stopping.")
                return all_posts
            
        curent_page += 1

        #Stop Condition3
        if not raw_posts and curent_page > 1:
            print("No more posts found. Ending scraping.")
            break

    return all_posts