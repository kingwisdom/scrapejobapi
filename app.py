import flask
from flask import Flask,request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = flask.Flask(__name__)
app.config["DEBUG"] = True

books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]




@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    return jsonify(books)

@app.route('/api/v1/resources/books', methods=['GET'])
def api_id():
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."
    results = []

    for book in books:
        if book['id'] == id:
            results.append(book)
    return jsonify(results)


@app.route('/api/awari/items', methods=['GET'])
def api_searches():
    if 'search' in request.args:
        search = request.args['search']
        locate = request.args['l']
    else:
        return "Error: No id field provided. Please specify an id."
    results = []

    products = []
    for x in range(1, 4):
        baseurl = f"https://www.jumia.com.ng/catalog/?q={search}&l={locate}&page={x}#catalog-listing"

        r = requests.get(baseurl)

        soup = BeautifulSoup(r.content, 'lxml')

        myList = soup.find_all('article', class_='prd _fb col c-prd')

        for item in myList:
            name = item.find('h3', class_='name').text.strip()
            price = item.find('div', class_='prc').text.strip()
            imgUrl = item.find('img', class_='img').get('data-src')
            link = item.find('a', href=True)['href']

            my_dict = {'Product Name': name, 'Product Price': price, "link": link, "image": imgUrl}
            products.append(my_dict)


    return jsonify(products)
    

# @app.route('/api/jobs', methods=['GET'])
# def api_search():
    if 'search' in request.args:
        search = request.args['search']
    else:
        return "Error: No search term provided. Please specify a search term.", 400
    jobs = []

    # Setup Selenium with Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    for x in range(0, 3):
        baseurl = f"https://www.indeed.com/jobs?q={search}&start={x*10}"
        driver.get(baseurl)
        time.sleep(3)  # Allow time for the page to load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_list = soup.find_all('div', class_='jobsearch-SerpJobCard')

        for job in job_list:
            title = job.find('h2', class_='title')
            company = job.find('span', class_='company')
            location = job.find('div', class_='location')
            summary = job.find('div', class_='summary')
            link = title.find('a', class_='jobtitle')['href'] if title else None

            if title and link:
                job_dict = {
                    'Job Title': title.text.strip(),
                    'Company': company.text.strip() if company else 'N/A',
                    'Location': location.text.strip() if location else 'N/A',
                    'Summary': summary.text.strip() if summary else 'N/A',
                    'Link': f"https://www.indeed.com{link}"
                }
                jobs.append(job_dict)

    driver.quit()
    return jsonify(jobs)


def fetch_jobs(search, page, driver):
    baseurl = f"https://uk.indeed.com/jobs?q={search}&start={page*10}&fromage=3"
    driver.get(baseurl)
    time.sleep(random.uniform(3, 6))  # Allow time for the page to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_list = soup.find_all('div', class_='job_seen_beacon')
    jobs = []

    for job in job_list:
        title = job.find('h2', class_='jobTitle')
        company = job.find('span', class_='css-63koeb eu4oa1w0')
        location = job.find('div', class_='css-1p0sjhy eu4oa1w0')
        summary = job.find('div', class_='css-9446fg eu4oa1w0')
        posted = job.find('span', class_='css-qvloho eu4oa1w0')
        link = title.find('a')['href'] if title and title.find('a') else None

        if title and link:
            job_dict = {
                'Job Title': title.text.strip(),
                'Company': company.text.strip() if company else 'N/A',
                'Location': location.text.strip() if location else 'N/A',
                'Summary': summary.text.strip() if summary else 'N/A',
                'posted': posted.text.strip() if posted else '-',
                'Link': f"https://www.indeed.com{link}"
            }
            jobs.append(job_dict)
    return jobs

@app.route('/api/search', methods=['GET'])
def api_search():
    if 'search' in request.args:
        search = request.args['search']
    else:
        return "Error: No search term provided. Please specify a search term.", 400

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    jobs = []
    driver = webdriver.Chrome(options=chrome_options)

    try:
        for x in range(3):  # Fetching the first 3 pages
            jobs.extend(fetch_jobs(search, x, driver))
            time.sleep(random.uniform(1, 3))  # Random delay between requests
    finally:
        driver.quit()

    return jsonify(jobs)


if __name__ == '__main__':
    app.run()
#    app.run(port=5000)
