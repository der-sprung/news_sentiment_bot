#!/usr/bin/env python
# coding: utf-8

# In[59]:


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
import datetime as dt


# In[60]:


# my_url = 'http://apne.ws/GqNnwLn'


# In[81]:


def ap_news(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 5)
    browser_url = driver.current_url
    
    if 'apnews.com' not in browser_url:
        driver.quit()
        return (True, '', True)
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''h1[class*='Component-heading']''').get_attribute('textContent')
    except:
        title = ''
        blank_alert = True

    # find author
    try:
        author = driver.find_element_by_css_selector('''span[class*='Component-bylines']''').get_attribute('textContent')[3:].title()
    except:
        author = ''
        blank_alert = True

    # find date
    try:
        timecode = driver.find_element_by_css_selector('span.Timestamp').get_attribute('outerHTML')
        index = timecode.find('title=') + 7
        date = timecode[index:(index+10)]
    except:
        date = ''
        blank_alert = True

    # find meta tags
    try:
        meta_tags = driver.find_element_by_name('keywords').get_attribute('content').split(',')
    except:
        meta_tags = ''
        blank_alert = True

    # find HTML elements of article text
    try:
        p_elements = driver.find_elements_by_css_selector('''p''')
    except:
        driver.quit()
        return (True, '', True)
    
    # concatenate article text from each element into one string
    content = ''''''
    for e in p_elements:
        text = e.get_attribute('textContent')
        content += (' ' + text)

    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title)

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@ap [Associated Press]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count
    }
    
    # add meta tags as separate entities
    index = 0
    for tag in meta_tags:
        new_tag = 'meta_tag_' + str(index)
        new_scores[new_tag] = tag
        index += 1

    if 'AP Week in Pictures' in new_scores['title']:
        not_news_alert = True
    elif 'AP Photos' in new_scores['title']:
        not_news_alert = True
    elif 'PHOTO GALLERY' in new_scores['title']:
        not_news_alert = True
    elif 'https://apnews.com/article' not in browser_url:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()
    
    return (blank_alert, new_scores, not_news_alert)


# In[82]:


def skynews_UK(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 5)
    browser_url = driver.current_url
    
    if 'news.sky.com' not in browser_url:
        driver.quit()
        return (True, '', True)
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''span[class*='sdc-article-header__long-title']''')        .get_attribute('textContent')
    except:
        title = ''
        blank_alert = True

    # find author
    try:
        author = driver.find_element_by_css_selector('''[class*='sdc-article-author__link']''').get_attribute('textContent').title()
    except:
        try:
            author = driver.find_element_by_css_selector('''p[class*='author']''').get_attribute('textContent').title()
            index = author.find(',')
            author = author[3:index].strip()
        except:
            author = ''
            blank_alert = True

    # find date
    try:
        timecode = driver.find_element_by_css_selector('''p[class*='sdc-article-date__date-time']''')        .get_attribute('textContent')
        index = timecode.find(' ') + 1
        date_string = timecode[index:-10]
        date_object = dt.datetime.strptime(date_string, '%d %B %Y')
        date = dt.datetime.strftime(date_object, '%Y-%m-%d')
        
    except:
        date = ''
        blank_alert = True

    # find metatags
    # find overall topic, take text and add to meta_tags list
    try:
        topic = driver.find_element_by_css_selector('''a[aria-current="true"]''')
        meta_tags = [topic.get_attribute('textContent')]
        # find all subtags, take text and add to list. Add list to meta_tags list
        article_tags = [el.get_attribute('textContent') for el in driver.find_elements_by_css_selector('''a[class='sdc-article-tags__link']''')]
        meta_tags.extend(article_tags)
    except:
        meta_tags = []

    # find HTML elements of article text
    try:
        p_elements = driver.find_elements_by_xpath('''//div[@data-component-name='sdc-article-body']/p''')
    except:
        driver.quit()
        return (True, '', True)
    
    # concatenate article text from each element into one string
    content = ''''''
    for e in p_elements:
        text = e.get_attribute('textContent')
        content += (' ' + text)

    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title)

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@SkyNews [Sky News UK]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count
    }
    
    # add meta tags as separate entities
    index = 0
    for tag in meta_tags:
        new_tag = 'meta_tag_' + str(index)
        new_scores[new_tag] = tag
        index += 1

    # check article is actually a news article
    
    if 'Live updates:' in new_scores['title']:
        not_news_alert = True
    elif 'live:' in new_scores['title']:
        not_news_alert = True
    elif 'COVID news live' in new_scores['title']:
        not_news_alert = True
    elif 'newspaper front pages' in new_scores['title']:
        not_news_alert = True
    elif 'The Sky News Daily podcast' in new_scores['title']:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()

    return (blank_alert, new_scores, not_news_alert)


# In[83]:


def skynews_AU(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 10)
    browser_url = driver.current_url
    
    if 'skynews.com.au' not in browser_url:
        driver.quit()
        return (True, '', True)
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''h1[id*='story-headline']''')        .get_attribute('textContent')
    except:
        try:
            title = driver.find_element_by_css_selector('''div[class*='module-header vms-header']''')            .get_attribute('textContent')
        except:
            title = ''
            blank_alert = True

    # find author
    try:
        author = driver.find_element_by_css_selector('''span[data-tgev-container*='story-byline']''')        .get_attribute('textContent').title()
    except:
        author = ''
        blank_alert = True

    # find date
    try:
        timecode = driver.find_element_by_css_selector('''div[id*='publish-date']''')        .get_attribute('textContent')
        index = timecode.find('-') - 1
        date_string = timecode[:index]
        date_object = dt.datetime.strptime(date_string, '%B %d, %Y')
        date = dt.datetime.strftime(date_object, '%Y-%m-%d')
        
    except:
        date = ''
        blank_alert = True

    # there are no meta tags in SkyNews   
    # separate publication topics by URL string
    prime_topics = {'australia-news' : 'Australia News',
              'world-news' : 'World News',
              'opinion' : 'Opinion',
              'business' : 'Business',
              'lifestyle' : 'Lifestyle'}
    
    try:
        meta_tag_content = driver.find_element_by_xpath('''//ul[@id='breadcrumbs']''').get_attribute('textContent')
        current_url = driver.current_url
        meta_tags = []

        for topic in prime_topics:
            if current_url.find(topic) != -1:
                tag_1 = prime_topics[topic]
                tag_2 = meta_tag_content[len(tag_1):].strip()
                meta_tags.extend([tag_1,tag_2])
    except:
        meta_tags = []

    # find HTML elements of article text 
    # note: p tags are contained in one of 2 divs that can be found in all articles (one is always empty)
    
    # find p tags in each div
    try:
        p_1 = [el.get_attribute('textContent') for el in driver.find_elements_by_xpath('''//div[@id='story-body']/p''')]
        p_2 = [el.get_attribute('textContent') for el in driver.find_elements_by_xpath('''//div[@class="video-body"]/p''')]

        # find which div has more p tags, and append to p_elements
        if len(p_1) > 0 and len(p_2) > 0:
            p_elements = p_1 + p_2
            ele_solve = 'p_1 + p_2'
        elif len(p_1) > 0 and len(p_2) <= 0:
            p_elements = p_1
            ele_solve = 'p_1'
        elif len(p_1) <= 0 and len(p_2) > 0:
            p_elements = p_2
            ele_solve = 'p_2'
        else:
            p_elements = []
    except:
        driver.quit()
        return (True, '', True)
  
    # concatenate article text from each element into one string, remove special punctuation
    content = ''''''
    for e in p_elements:
        text = e.replace('‘','').replace('’','')
        content += (' ' + text)

    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title.replace('‘','').replace('’',''))

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@SkyNewsAust [Sky News Australia]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count
    }
    
    # add meta tags as separate entities
    index = 0
    for tag in meta_tags:
        new_tag = 'meta_tag_' + str(index)
        new_scores[new_tag] = tag
        index += 1

    # check article is actually a news article
    
    if 'Live updates:' in title:
        not_news_alert = True
    elif 'live:' in title:
        not_news_alert = True
    elif 'COVID news live' in title:
        not_news_alert = True
    elif 'newspaper front pages' in title:
        not_news_alert = True
    elif 'LIVE BLOG:' in title:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()

    return (blank_alert, new_scores, not_news_alert)


# In[84]:


def guardian(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 10)
    browser_url = driver.current_url
    
    if 'https://www.theguardian.com/' not in browser_url:
        driver.quit()
        return (True, '', True)
    elif '/video/' in browser_url:
        driver.quit()
        return (True, '', True)
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''h1''')        .get_attribute('textContent')
    except:
        title = ''
        blank_alert = True

    # find author
    try:
        author = driver.find_element_by_css_selector('''a[rel='author']''')        .get_attribute('textContent').title()
    except:
        author = ''
        blank_alert = True

    # find date
    try:
        timecode = driver.find_element_by_css_selector('''label[for*='dateToggle']''')        .get_attribute('textContent')
        date_string = timecode[:-11]
        date_object = dt.datetime.strptime(date_string, '%a %d %b %Y')
        date = dt.datetime.strftime(date_object, '%Y-%m-%d')
    except:
        try:
            timecode = driver.find_element_by_css_selector('''div[class='dcr-18svo86']''')            .get_attribute('textContent')
            date_string = timecode[:-11]
            date_object = dt.datetime.strptime(date_string, '%a %d %b %Y')
            date = dt.datetime.strftime(date_object, '%Y-%m-%d')
        except:
            date = ''
            blank_alert = True

    # there are no meta tags in Guardian - pull from URL instead 
    # remove 'https://www.theguardian.com/' from URL and find location of next '/'
    try:
        url_tail = browser_url.replace('https://www.theguardian.com/','')
        index = url_tail.find('/')
        meta_tags = [url_tail[:index]]
        try:
            meta_tag_2 = [driver.find_element_by_xpath('''//div[@class='dcr-1u8qly9']/a''').get_attribute('textContent')]
        except:
            try:
                meta_tag_2 = [el.get_attribute('textContent') for el in driver.find_elements_by_xpath('''//div[@class='dcr-q9y0k5']/a''')]
            except:
                meta_tag_2 = []
        meta_tags.extend(meta_tag_2)
    except:
        meta_tags = []

    # find HTML elements of article text 
    try:
        p_elements = driver.find_element_by_css_selector('div#maincontent>div')
    except:
        driver.quit()
        return (True, '', True)

    # concatenate article text from each element into one string, remove special punctuation
    content = p_elements.get_attribute('textContent')

    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title.replace('‘','').replace('’',''))

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@Guardian [The Guardian]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count
    }
    
    # add meta tags as separate entities
    index = 0
    for tag in meta_tags:
        new_tag = 'meta_tag_' + str(index)
        new_scores[new_tag] = tag
        index += 1

    # check article is actually a news article
    
    if 'Live updates:' in title:
        not_news_alert = True
    elif 'live:' in title:
        not_news_alert = True
    elif 'COVID news live' in title:
        not_news_alert = True
    elif 'newspaper front pages' in title:
        not_news_alert = True
    elif 'LIVE BLOG:' in title:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()

    return (blank_alert, new_scores, not_news_alert)


# In[85]:


def smh(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 10)
    browser_url = driver.current_url
    
    # check if link in smh domain
    if 'https://www.smh.com.au' not in browser_url:
        driver.quit()
        return (True, '', True)
    
    # looking for "live news" page (skip these)
    try:
        live_div = driver.find_element_by_css_selector('''div._1u5WD''')
        driver.quit()
        return (True, '', True)
    except:
        live_div = None
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''h1[itemprop='headline']''')        .get_attribute('textContent')
    except:
        title = ''
        blank_alert = True

    # find author
    try:
        author = driver.find_element_by_css_selector('''a[title*='Articles by']''')        .get_attribute('textContent').title()
    except:
        author = ''
        blank_alert = True

    # find date
    try:
        timecode = driver.find_element_by_css_selector('''span[class='_2xetH']''')        .get_attribute('textContent')
        
        # split date elements by whitespaces, add first 3 elements to date_string
        date_el = timecode.split()
        date_string = ''
        index = 0
        for el in date_el:
            index += 1
            if index < 4:
                date_string = date_string + el + ' '
        # format date_string
        date_object = dt.datetime.strptime(date_string, '%B %d, %Y ')
        date = dt.datetime.strftime(date_object, '%Y-%m-%d')
    except:
        date = ''
        blank_alert = True

    # there are no meta tags - pull from URL instead 
    # remove 'https://www.smh.com.au' from URL and find location of next '/'
    try:
        url_tail_1 = browser_url.replace('https://www.smh.com.au/','')
        index_1 = url_tail_1.find('/')
        meta_tag_1 = url_tail_1[:index_1]

        url_tail_2 = url_tail_1.replace((meta_tag_1 + '/'),'')
        index_2 = url_tail_2.find('/')
        meta_tag_2 = url_tail_2[:index_2]

        meta_tags = [meta_tag_1, meta_tag_2]
    except:
        meta_tags = []

    # find HTML elements of article text 
    try:
        p_elements = driver.find_element_by_css_selector('''div[class*='_1665V']''')
    except:
        driver.quit()
        return (True, '', True)

    # concatenate article text from each element into one string, remove special punctuation
    content = p_elements.get_attribute('textContent')

    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title.replace('‘','').replace('’',''))

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@smh [Sydney Morning Herald]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count
    }
    
    # add meta tags as separate entities
    index = 0
    for tag in meta_tags:
        new_tag = 'meta_tag_' + str(index)
        new_scores[new_tag] = tag
        index += 1

    # check article is actually a news article
    if 'Australia news LIVE:' in title:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()
    
    return (blank_alert, new_scores, not_news_alert)


# In[86]:


def betoota(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 10)
    browser_url = driver.current_url
    
    # check if link in smh domain
    if 'https://www.betootaadvocate.com/' not in browser_url:
        driver.quit()
        return (True, '', True)
    elif 'https://www.betootaadvocate.com/betoota-podcast/' in browser_url:
        driver.quit()
        return (True, '', True)
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''h1[class='entry-title']''')        .get_attribute('textContent')
    except:
        title = ''
        blank_alert = True

    # find author
    try:
        byline = driver.find_element_by_xpath('''//div[@class='td-post-content tagdiv-type']/p[1]''')        .get_attribute('textContent').title()
        index = byline.find('Editor') - 3
        author = byline[:index]
    except:
        author = ''
        blank_alert = True

    # find date
    try:
        timecode = driver.find_element_by_css_selector('''meta[itemprop='datePublished']''')        .get_attribute('outerHTML')
        index = timecode.find('content=') + 9
        date = timecode[index:index+10]
    except:
        date = ''
        blank_alert = True

    # there are no meta tags - pull from URL instead 
    # remove 'https://www.smh.com.au' from URL and find location of next '/'
    try:
        url_tail_1 = browser_url.replace('https://www.betootaadvocate.com/','')
        index_1 = url_tail_1.find('/')
        meta_tag_1 = url_tail_1[:index_1]

        other_tag_el = driver.find_elements_by_css_selector('''li[class='entry-category']''')
        other_tags = [el.get_attribute('textContent') for el in other_tag_el]

        meta_tags = [meta_tag_1]
        meta_tags.extend(other_tags)
    except:
        meta_tags = []

    # find HTML elements of article text 
    try:
        p_elements = driver.find_element_by_css_selector('''div[class*='td-post-content tagdiv-type']''')
    except:
        driver.quit()
        return (True, '', True)

    # concatenate article text from each element into one string, remove special punctuation
    content = p_elements.get_attribute('textContent')

    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title.replace('‘','').replace('’',''))

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@BetootaAdvocate [Betoota Advocate]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count
    }
    
    # add meta tags as separate entities
    index = 0
    for tag in meta_tags:
        new_tag = 'meta_tag_' + str(index)
        new_scores[new_tag] = tag
        index += 1

    # check article is actually a news article
    
    if 'Australia news LIVE:' in title:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()
    
    return (blank_alert, new_scores, not_news_alert)


# In[87]:


def newscom(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 10)
    browser_url = driver.current_url
    
    # check if link in news.com domain
    if 'https://www.news.com.au/' not in browser_url:
        driver.quit()
        return (True, '', True)
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''h1[class='story-headline']''')        .get_attribute('textContent')
    except:
        title = ''
        blank_alert = True

    # find author
    try:
        author = driver.find_element_by_css_selector('''div[class='name']''')        .get_attribute('textContent').title()
    except:
        try:
            author = driver.find_element_by_css_selector('''span[class='author-name']''')            .get_attribute('textContent').title()
        except:
            author = ''
            blank_alert = True

    # find date
    try:       
        timecode = driver.find_element_by_css_selector('''div[class='other-info']''')        .get_attribute('textContent')

        months = ['January', 'February', 'March', 'April', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        for m in months:
            if timecode.find(m) != -1:
                index = timecode.find(m)
        datetime = timecode[index:]
        date_object = dt.datetime.strptime(datetime, '%B %d, %Y%I:%M%p')
        date = dt.datetime.strftime(date_object, '%Y-%m-%d')
    except:
        date = ''
        blank_alert = True

    # there are no meta tags - pull from URL instead 
    # remove 'https://www.news.com.au/' from URL and find location of next '/'
    try:
        url_tail_1 = browser_url.replace('https://www.news.com.au/','')
        index_1 = url_tail_1.find('/')
        meta_tag_1 = url_tail_1[:index_1]

        url_tail_2 = url_tail_1.replace((meta_tag_1 + '/'),'')
        index_2 = url_tail_2.find('/')
        meta_tag_2 = url_tail_2[:index_2]

        meta_tags = [meta_tag_1, meta_tag_2]
    except:
        meta_tags = []

    # find HTML elements of article text 
    try: 
        p_elements = driver.find_elements_by_xpath('''//div[@class='story-content']/p''')
    except:
        driver.quit()
        return (True, '', True)

    # concatenate article text from each element into one string, remove special punctuation
    content = ''''''
    for el in p_elements:
        if el.get_attribute('textContent').find('READ MORE') != -1:
            continue
        else:
            content = content + " " + el.get_attribute('textContent')
    
    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title.replace('‘','').replace('’',''))

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@newscomauHQ [news.com]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count
    }
    
    # add meta tags as separate entities
    index = 0
    for tag in meta_tags:
        new_tag = 'meta_tag_' + str(index)
        new_scores[new_tag] = tag
        index += 1

    # check article is actually a news article
    if 'Australia news LIVE:' in title:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()
    
    return (blank_alert, new_scores, not_news_alert)


# In[88]:


def reuters(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 10)
    browser_url = driver.current_url
    
    # check if link in reuters domain
    if 'https://www.reuters.com/' not in browser_url:
        driver.quit()
        return (True, '', True)
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''h1''')        .get_attribute('textContent')
    except:
        title = ''
        blank_alert = True

    # find author
    try:
        author = driver.find_element_by_css_selector('''meta[name='article:author']''')        .get_attribute('content').title()
        
        # check if multiple authors, edit to primary author
        if author.find(',') != -1:
            names = author.split(',')
            author = names[0]
    except:
        author = ''
        blank_alert = True

    # find date
    try:       
        timecode = driver.find_element_by_css_selector('''meta[name='article:published_time']''')        .get_attribute('content').title()
        date = timecode[:10]
        #date_object = dt.datetime.strptime(datetime, '%B %d, %Y%I:%M%p')
        #date = dt.datetime.strftime(date_object, '%Y-%m-%d')
    except:
        date = ''
        blank_alert = True

    # there are no meta tags - pull from URL instead 
    # remove 'https://www.reuters.com/' from URL and find location of next '/'
    try:
        url_tail = browser_url.replace('https://www.reuters.com/','')
        index = url_tail.find('/')
        meta_tag = url_tail[:index]
    except:
        meta_tags = []

    # find HTML elements of article text 
    try: 
        p_elements = driver.find_elements_by_xpath('''//div[@class='ArticleBody__content___2gQno2 paywall-article']/p''')
    except:
        driver.quit()
        return (True, '', True)

    # concatenate article text from each element into one string, remove special punctuation
    content = ''''''
    for el in p_elements:
        text = el.get_attribute('textContent')
        content += (' ' + text)
    
    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title.replace('‘','').replace('’',''))

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@reuters [Reuters]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count,
        'meta_tag_0' : meta_tag
    }

    # check article is actually a news article
    if 'Australia news LIVE:' in title:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()
    
    return (blank_alert, new_scores, not_news_alert)


# In[89]:


def abc(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 10)
    browser_url = driver.current_url
    
    # check if correct domain
    if 'https://www.abc.net.au/' not in browser_url:
        driver.quit()
        return (True, '', True)
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''h1[data-component='Heading']''')        .get_attribute('textContent')
    except:
        title = ''
        blank_alert = True

    # find author
    try:
        author_string = driver.find_element_by_css_selector('''meta[property='article:author']''')        .get_attribute('content').title()
        index_1 = author_string.rfind('/')
        author_slice = author_string[:index_1]
        index_2 = author_slice.rfind('/') + 1
        author_dirty = author_slice[index_2:]
        author = author_dirty.replace('-',' ')
    except:
        author = ''
        blank_alert = True

    # find date
    try:       
        timecode = driver.find_element_by_css_selector('''meta[property='article:published_time']''')        .get_attribute('content')
        date = timecode[:10]
    except:
        date = ''
        blank_alert = True

    # there are no meta tags - pull from URL instead 
    # remove 'https://www.news.com.au/' from URL and find location of next '/'
    try:
        meta_tag_el = driver.find_elements_by_css_selector('''meta[property='article:tag']''')
        meta_tags = []

        for el in meta_tag_el:
            meta_tags.append(el.get_attribute('content'))
    except:
        meta_tags = []
    
    # find HTML elements of article text 
    try: 
        p_elements = driver.find_elements_by_css_selector('''p[class='_1HzXw']''')
    except:
        driver.quit()
        return (True, '', True)

    # concatenate article text from each element into one string, remove special punctuation
    content = ''''''
    for el in p_elements:
        text = el.get_attribute('textContent')
        content += (' ' + text)
    
    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title.replace('‘','').replace('’',''))

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@abcnews [ABC News]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count
    }
    
    # add meta tags as separate entities
    index = 0
    for tag in meta_tags:
        new_tag = 'meta_tag_' + str(index)
        new_scores[new_tag] = tag
        index += 1

    # check article is actually a news article
    if 'NRL ScoreCentre' in title:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()
    
    return (blank_alert, new_scores, not_news_alert)


# In[90]:


def sbs(my_url):
    
    # check URL is URL (to avoid typing errors registered as link entities)
    if 'http' not in my_url:
        return (True, '', True)
    
    # open chrome driver & search my_url
    driver = webdriver.Chrome(executable_path=r'C:\Users\theyc\Documents\Drivers\chromedriver_win32\chromedriver.exe')
    driver.get(my_url)
    WebDriverWait(driver, 10)
    browser_url = driver.current_url
    
    # check if correct domain
    if 'https://www.sbs.com.au/' not in browser_url:
        driver.quit()
        return (True, '', True)
    
    # warning for blank entries. False if all values found successful
    blank_alert = False
    
    # find title
    try:
        title = driver.find_element_by_css_selector('''h1''')        .get_attribute('textContent')
    except:
        title = ''
        blank_alert = True

    # find author
    try:
        author_string = driver.find_element_by_css_selector('''meta[class*='article__meta-author--block']''')        .get_attribute('textContent').title()
        author = author_string[3:]
    except:
        author = ''
        blank_alert = True

    # find date
    try:       
        timecode = driver.find_element_by_css_selector('''meta[itemprop='datePublished']''')        .get_attribute('content')
        date = timecode[:10]
    except:
        date = ''
        blank_alert = True

    # there are no meta tags for SBS or topic breakdown
    try:
        meta_tag = driver.find_element_by_css_selector('''div[class='article__topic']''')        .get_attribute('textContent').title().strip()
    except:
        meta_tag = ''
    
    # find HTML elements of article text 
    try: 
        p_elements = driver.find_elements_by_css_selector('''div[class='text-body']''')
    except:
        driver.quit()
        return (True, '', True)

    # concatenate article text from each element into one string, remove special punctuation
    content = ''''''
    for el in p_elements:
        text = el.get_attribute('textContent')
        content += (' ' + text)
    
    # SID polarity analysis (VADER)
    vader_content = sid.polarity_scores(content)
    vader_title = sid.polarity_scores(title.replace('‘','').replace('’',''))

    # word counter
    word_count = len(content.split())

    new_scores = {
        'title' : title,
        'author' : author,
        'date' : date,
        'publication' : '@SBSNews [SBS News]',
        'article_neg' : vader_content['neg'],
        'article_neu' : vader_content['neu'],
        'article_pos' : vader_content['pos'],
        'article_compound' : vader_content['compound'],
        'title_neg' : vader_title['neg'],
        'title_neu' : vader_title['neu'],
        'title_pos' : vader_title['pos'],
        'title_compound' : vader_title['compound'],
        'vader_diff' : vader_content['compound'] - vader_title['compound'],
        'word_count' : word_count
    }
    
    # add meta tag to dictionary
    new_scores['meta_tag_0'] = meta_tag

    # check article is actually a news article
    if 'NRL ScoreCentre' in title:
        not_news_alert = True
    else:
        not_news_alert = False
        
    # close selenium chrome driver
    driver.quit()
    
    return (blank_alert, new_scores, not_news_alert)


# In[ ]:




