import pytest
import requests_mock
import argparse
import os
import sys
import csv
from io import StringIO


#functions to test-------------------------------------------------------------------

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.processor import filter_posts, run_scrapting_pipeline 
from src.scrapter import parse_posts_from_html  
from src.output_writer import write_to_csv, FIELDNAMES

# fake data for testing
#from .mock_data import MOCK_HTML_PAGE_1, MOCK_HTML_PAGE_2 



MOCK_HTML_PAGE_1 = """
<table class="itemlist">
    <tr class="athing" id="410001">
        <td align="right" valign="top" class="title">1.</td>
        <td class="votelinks"></td>
        <td class="title"><a href="http://example.com/high" class="titlelink">High Score Post</a></td>
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
        <td class="title"><a href="http://example.com/low" class="titlelink">Low Score Post</a></td>
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
        <td class="title"><a href="http://example.com/mid" class="titlelink">Mid Score Post</a></td>
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




# maintrain for tests

def test_parse_posts_correctly():
   
    posts = parse_posts_from_html(MOCK_HTML_PAGE_1, 1)
    
    assert len(posts) == 2
    assert posts[0]['Title'] == 'High Score Post'
    assert posts[0]['Points'] == 180
    assert posts[1]['Number of comments'] == 0 # "discuss" אמור להפוך ל-0

def test_filter_posts_score():
    
    raw_posts = parse_posts_from_html(MOCK_HTML_PAGE_1, 1) 
    
    # סינון: רק פוסטים עם ציון מעל 100
    filtered = filter_posts(raw_posts, min_score=100, max_score=1000)
    assert len(filtered) == 1
    assert filtered[0]['Title'] == 'High Score Post'

# --- בדיקות Pipeline עם Mocking (החלק החשוב ביותר) ---

@pytest.fixture
def mock_config_default():
    """יוצר אובייקט config בסיסי לבדיקות Mocking."""
    # זהו אובייקט argparse.Namespace מזויף
    return argparse.Namespace(
        min_score=0,
        max_score=1000,
        max_posts=50, 
        skip_pages=[]
    )

def test_pipeline_basic_two_pages(requests_mock, mock_config_default):
    """בדיקה של pipeline שעובר שני עמודים עד שמקבל 404."""
    
    # Mocking: מזייפים את תגובות השרת:
    requests_mock.get("https://news.ycombinator.com/newest?p=1", text=MOCK_HTML_PAGE_1)
    requests_mock.get("https://news.ycombinator.com/newest?p=2", text=MOCK_HTML_PAGE_2)
    # מזייפים 404 לעמוד 3 כדי שהלולאה תעצור:
    requests_mock.get("https://news.ycombinator.com/newest?p=3", status_code=404)
    
    posts = run_scrapting_pipeline(mock_config_default)
    
    assert len(posts) == 3
    assert posts[0]['Page number'] == 1
    assert posts[2]['Page number'] == 2
    assert posts[2]['Title'] == 'Mid Score Post'

def test_pipeline_stop_at_max_posts(requests_mock, mock_config_default):
    """בדיקה שה-pipeline עוצר כשהוא מגיע ל-max_posts."""
    
    # מזייפים מספיק עמודים כדי לאסוף את המגבלה:
    requests_mock.get("https://news.ycombinator.com/newest?p=1", text=MOCK_HTML_PAGE_1)
    requests_mock.get("https://news.ycombinator.com/newest?p=2", text=MOCK_HTML_PAGE_1) 

    requests_mock.get("https://news.ycombinator.com/newest?p=3", status_code=404)
    
    # מגבילים את הכמות ל-3 פוסטים (מתוך 4 זמינים)
    mock_config_default.max_posts = 3
    
    posts = run_scrapting_pipeline(mock_config_default)
    
    # הבדיקה: צריך להיות 3 פוסטים בלבד
    assert len(posts) == 3
    # הפוסט השלישי שנאסף הוא ה'High Score Post' מעמוד 2
    assert posts[2]['Title'] == 'High Score Post' 

def test_pipeline_skip_page(requests_mock, mock_config_default):
    """בדיקה שה-pipeline מדלג על עמוד 2 כנדרש."""
    
    requests_mock.get("https://news.ycombinator.com/newest?p=1", text=MOCK_HTML_PAGE_1) # 2 פוסטים
    requests_mock.get("https://news.ycombinator.com/newest?p=2", text=MOCK_HTML_PAGE_2) # זה העמוד המדלג (יכיל 'Mid Score Post')
    requests_mock.get("https://news.ycombinator.com/newest?p=3", text=MOCK_HTML_PAGE_1) # 2 פוסטים נוספים
    requests_mock.get("https://news.ycombinator.com/newest?p=4", status_code=404)
    
    # מגדירים Skip Pages ל-2
    mock_config_default.skip_pages = [2]
    mock_config_default.max_posts = 10
    
    posts = run_scrapting_pipeline(mock_config_default)
    
    # הבדיקה: אמורים להיות 4 פוסטים בלבד (מ-עמוד 1 ו-3)
    assert len(posts) == 4
    assert posts[0]['Page number'] == 1
    assert posts[2]['Page number'] == 3
    # בדיקה שלא נאסף אף פוסט מ-Page 2 (Mid Score Post)
    assert not any(p['Title'] == 'Mid Score Post' for p in posts)