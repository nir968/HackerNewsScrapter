#scrapter = הגירודים
from bs4 import BeautifulSoup
import requests

HACKERNEWS_URL = "https://news.ycombinator.com/newest"

POST_FIELDS = ['Title', 'URL', 'Author', 'Points', 'Number of comments', 'Page number']


def fetch_page( page_number: int) -> str | None:

    url = f"{HACKERNEWS_URL}?p={page_number}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.text
        
        elif response.status_code == 404:
            print(f"Page {page_number} not found (404). ")
            return None

        else:
            print(f"Error fetching page {page_number}: Status code {response.status_code}")
            return None

         
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_number}: {e}")
        return None
    

#parse
def parse_posts_from_html(html_content: str, page_num: int) -> list[dict]:
        
    posts_data = []
    soup = BeautifulSoup(html_content, "html.parser")


    for post_row in soup.find_all("tr", class_="athing"):
       
            title, url, author = "N/A", "N/A", "N/A"
            points, comments_num = 0, 0
        #get title and url
            title_span = post_row.find("span", class_="titleline")
            if title_span:
                    title_link = title_span.find("a")  
            else:
                    title_link = None #check if title_span is exists and then find a(link)
                    
            title_link = post_row.find("a", class_="titlelink")
            if title_link:  
                    title = title_link.text
                    url = title_link.get("href", "N/A")

                    if url.startswith("item?id="):
                        url = f"https://news.ycombinator.com/{url}"


            score_row = post_row.find_next_sibling("tr")#go to next tr
        #get author and points
            if score_row:
                score_span = score_row.find("span", class_="score")
                if score_span:
                    try:
                        points = int(score_span.text.split()[0])
                    except (ValueError, IndexError):# if conversion fails (no points found..)
                        points = 0

                author_link = score_row.find("a", class_="hnuser")
                if author_link:
                    author = author_link.text
                else:   
                    author = "N/A"
        #get number of comments
                subtext_links = score_row.find_all('a')
                    
                if subtext_links:
                    #comment_link = next((a for a in subtext_links if 'comment' in a.text or 'discuss' in a.text), None)
                    for link in subtext_links:
                        if 'comment' in link.text or 'discuss' in link.text:
                            comment_link = link
                            break
                    
                    comments_num = 0

                    if comment_link and 'comment' in comment_link.text:
                        try:
                            comments_num = int(comment_link.text.split()[0])
                        except (ValueError, IndexError):
                            comments_num = 0
                    else:
                        comments_num = 0 



                post = {"Title": title,
                        "URL": url,
                        "Author": author,
                        "Points": points,
                        "Number of comments": comments_num,
                        "Page number": page_num}


                posts_data.append(post)

    return posts_data
    