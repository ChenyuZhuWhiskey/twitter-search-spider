# Tweet Search Spider Using webdriver(Chrome) and Beautiful Soup

## requirements:
- `BeautifulSoup, pymongo` and `webdriver`
- if you like to use Firefox to scrape, please modify the following code in `twitterSpider.py`:
`browser = webdriver.Chrome()`


## Usage:
- Download `account.py`, set your account (do not use your personal account)
- Download `twitterSpider.py`,select your covered serching area, e.g.:
`keywords = ['bitcoin', 'BTC']`
`time_start = '2016-03-21'`
`time_end = '2019-05-28'`
`language = 'laneg=en'`
`tweets_wanted = 10000`
- You can also set your wanted location of dataset:
`Client = MongoClient('mongodb://localhost:27017/')`
`db = Client['twitterData']`
`collection = db.twitter`
- make sure that your mongodb service has been started:
`brew start mongodb server`
