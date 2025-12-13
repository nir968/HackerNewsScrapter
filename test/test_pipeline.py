import pytest
import requests_mock #to mock HTTP requests
import argparse #input by user(min_score,max_score,max_posts,skip_pages)
import os
import sys
import csv
from io import StringIO


# functions to test -------------------------------------------------------------------

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.processor import filter_posts, run_scraping_pipeline 
from src.scraper import parse_posts_from_html 
from src.output_writer import write_to_csv, FIELDNAMES

# fake data for testing
# from .mock_data import MOCK_HTML_PAGE_1, MOCK_HTML_PAGE_2 



MOCK_HTML_PAGE_1 = """
<table class="itemlist">
    <tr class="athing" id="410001">
        <td align="right" valign="top" class="title">1.</td>
        <td class="votelinks"></td>
        <td class="title">
            <span class="titleline">
                <a href="http://example.com/high">High Score Post</a> 
            </span>
        </td>
    </tr>
    <tr>
        <td colspan="2"></td>
        <td class="subtext">
            <span class="score" id="score_410001">180 points</span> by <a href="user?id=userA">userA</a> 
            | <a href="item?id=410001">2 comments</a> 
        </td>
    </tr>
    <tr class="athing" id="410002">
        <td align="right" valign="top" class="title">2.</td>
        <td class="votelinks"></td>
        <td class="title">
            <span class="titleline">
                <a href="http://example.com/low">Low Score Post</a>
            </span>
        </td>
    </tr>
    <tr>
        <td colspan="2"></td>
        <td class="subtext">
            <span class="score" id="score_410002">5 points</span> by <a href="user?id=userB">userB</a> 
            | <a href="item?id=410002">discuss</a> 
        </td>
    </tr>
</table>
<a class="morelink" href="news?p=2">More</a> 
"""


MOCK_HTML_PAGE_2 = """
<table class="itemlist">
    <tr class="athing" id="410003">
        <td align="right" valign="top" class="title">1.</td>
        <td class="votelinks"></td>
        <td class="title">
            <span class="titleline">
                <a href="http://example.com/mid">Mid Score Post</a>
            </span>
        </td>
    </tr>
    <tr>
        <td colspan="2"></td>
        <td class="subtext">
            <span class="score" id="score_410003">50 points</span> by <a href="user?id=userC">userC</a> 
            | <a href="item?id=410003">10 comments</a>
        </td>
    </tr>
</table>
"""
# main train for tests -------------------------------------------------------------------

def test_parse_posts_correctly():
    
    posts = parse_posts_from_html(MOCK_HTML_PAGE_1, 1)
    
    assert len(posts) == 2
    assert posts[0]['Title'] == 'High Score Post'
    assert posts[0]['Points'] == 180
    assert posts[1]['Number of comments'] == 0 # "discuss" should be converted to 0

def test_filter_posts_score():
    
    raw_posts = parse_posts_from_html(MOCK_HTML_PAGE_1, 1) 
    
    # Filter: Only posts with score above 100
    filtered = filter_posts(raw_posts, min_score=100, max_score=1000)
    assert len(filtered) == 1
    assert filtered[0]['Title'] == 'High Score Post'

# --- Pipeline Tests with Mocking (The most important part) ---

@pytest.fixture
def mock_config_default():
    """Creates a basic config object for Mocking tests."""
    # This is a fake argparse.Namespace object
    return argparse.Namespace(
        min_score=0,
        max_score=1000,
        max_posts=50, 
        skip_pages=[]
    )

def test_pipeline_basic_two_pages(requests_mock, mock_config_default):
    """Tests the pipeline across two pages until it receives a 404."""
    
    # Mocking: Faking server responses:
    requests_mock.get("https://news.ycombinator.com/newest?p=1", text=MOCK_HTML_PAGE_1)
    requests_mock.get("https://news.ycombinator.com/newest?p=2", text=MOCK_HTML_PAGE_2)
    # Faking 404 for page 3 so the loop stops:
    requests_mock.get("https://news.ycombinator.com/newest?p=3", status_code=404)
    
    posts = run_scraping_pipeline(mock_config_default)
    
    assert len(posts) == 3
    assert posts[0]['Page number'] == 1
    assert posts[2]['Page number'] == 2
    assert posts[2]['Title'] == 'Mid Score Post'

def test_pipeline_stop_at_max_posts(requests_mock, mock_config_default):
    """Tests that the pipeline stops when it reaches max_posts."""
    
    # Faking enough pages to collect the limit:
    requests_mock.get("https://news.ycombinator.com/newest?p=1", text=MOCK_HTML_PAGE_1)
    requests_mock.get("https://news.ycombinator.com/newest?p=2", text=MOCK_HTML_PAGE_1) 

    requests_mock.get("https://news.ycombinator.com/newest?p=3", status_code=404)
    
    # Limiting the count to 3 posts (out of 4 available)
    mock_config_default.max_posts = 3
    
    posts = run_scraping_pipeline(mock_config_default) # Running the new pipeline
    
    # Check: there should only be 3 posts
    assert len(posts) == 3
    # The third post collected should be the 'High Score Post' from Page 2
    assert posts[2]['Title'] == 'High Score Post' 

def test_pipeline_skip_page(requests_mock, mock_config_default):
    """Tests that the pipeline skips page 2 as required."""
    
    requests_mock.get("https://news.ycombinator.com/newest?p=1", text=MOCK_HTML_PAGE_1) # 2 posts
    requests_mock.get("https://news.ycombinator.com/newest?p=2", text=MOCK_HTML_PAGE_2) # This is the page to skip (contains 'Mid Score Post')
    requests_mock.get("https://news.ycombinator.com/newest?p=3", text=MOCK_HTML_PAGE_1) # 2 more posts
    requests_mock.get("https://news.ycombinator.com/newest?p=4", status_code=404)
    
    # Setting Skip Pages to 2
    mock_config_default.skip_pages = [2]
    mock_config_default.max_posts = 10
    
    posts = run_scraping_pipeline(mock_config_default)
    
    # Check: There should only be 4 posts (from pages 1 and 3)
    assert len(posts) == 4
    assert posts[0]['Page number'] == 1
    assert posts[2]['Page number'] == 3
    # Check that no posts were collected from Page 2 (Mid Score Post)
    assert not any(p['Title'] == 'Mid Score Post' for p in posts)
    # for each p in posts:
    #       if(['Title'] == 'Mid Score Post')
    #           assert False
    #       assert True

    # any() = returns True if any element of the iterable is true. If the iterable is empty, returns False