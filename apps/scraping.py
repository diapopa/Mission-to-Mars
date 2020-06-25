# Import dependencies
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    print('start scraping')
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    
    news_title, news_paragraph = mars_news(browser)

    hems = hemispheres(browser)

    # Run all scraping functions and store results in dictionary
    print('creating dictionary')
    test_data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hems
    }
    print('created')
    browser.quit()
    return test_data


# Set the executable path and initialize the chrome browser in splinter
executable_path = {'executable_path': 'chromedriver'}
browser = Browser('chrome', **executable_path)

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Set up the HTML parser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    browser.click_link_by_partial_text('more info')

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        mars_df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    mars_df.columns=['Description', 'Mars']
    mars_df.set_index('Description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return mars_df.to_html(classes="table table-striped")

def get_hem_img(browser,hem_text):
    # Function to find the hemisphere image url
    browser.find_by_text(hem_text).click()
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    hem_img = news_soup.select_one('li').find('a')
    hem_img = hem_img['href']
    return hem_img

def hemispheres(browser):

    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Set up the HTML parser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # Find the names of the four hemispheres
    hem = news_soup.find_all("h3")
    hem1 = hem[0].get_text()
    hem2 = hem[1].get_text()
    hem3 = hem[2].get_text()
    hem4 = hem[3].get_text()

    # Retrieve the image url for the first hemisphere
    hem1_img = get_hem_img(browser, hem1)
    
    # Visit URL and retrieve the image url for the second hemisphere
    browser.visit(url)
    hem2_img = get_hem_img(browser, hem2)
    
    # Visit URL and retrieve the image url for the third hemisphere
    browser.visit(url)
    hem3_img = get_hem_img(browser, hem3)
    
    # Visit URL and retrieve the image url for the fourth hemisphere
    browser.visit(url)
    hem4_img = get_hem_img(browser, hem4)

    # Create dictionary 
    hem1_dict = {"title": hem1, "img_url": hem1_img}
    hem2_dict = {"title": hem2, "img_url": hem2_img}
    hem3_dict = {"title": hem3, "img_url": hem3_img}
    hem4_dict = {"title": hem4, "img_url": hem4_img}

    # Create list of dictionaries
    hems = []
    hems.append(hem1_dict)
    hems.append(hem2_dict)
    hems.append(hem3_dict)
    hems.append(hem4_dict)

    return hems

# End the session
browser.quit()

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())