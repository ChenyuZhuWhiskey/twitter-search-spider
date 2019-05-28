import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from account import usr_name
from account import password

url_tweetsTemplate = 'https://twitter.com/APompliano/status/{}'
url_twitterSearchTemplate = 'https://twitter.com/search?f=tweets&q={}since%3A{}%20until%3A{}&src=typd&{}'

'''set mongodb Client'''
Client = MongoClient('mongodb://localhost:27017/')
db = Client['twitterData']
collection = db.twitter

'''covered search area'''
keywords = ['bitcoin', 'BTC']
time_start = '2016-03-21'
time_end = '2019-05-28'
language = 'laneg=en'
tweets_wanted = 10000  # number of expected tweets


def tweetTime_process(tweetTime):
    hour = tweetTime.split()[0].split(':')[0]
    minute = tweetTime.split()[0].split(':')[1]
    isAM = True if tweetTime.split()[1] == 'AM' else False
    day = tweetTime.split()[3]
    if not isAM:
        hour = str(int(hour)+12)
    mon_str = tweetTime.split()[4]
    if mon_str == 'Jan':
        mon = '01'
    elif mon_str == 'Feb':
        mon = '02'
    elif mon_str == 'Mar':
        mon = '03'
    elif mon_str == 'Apr':
        mon = '04'
    elif mon_str == 'May':
        mon = '05'
    elif mon_str == 'Jun':
        mon = '06'
    elif mon_str == 'Jul':
        mon = '07'
    elif mon_str == 'Aug':
        mon = '08'
    elif mon_str == 'Sep':
        mon = '09'
    elif mon_str == 'Oct':
        mon = '10'
    elif mon_str == 'Nov':
        mon = '11'
    else:
        mon = '12'
    year = tweetTime.split()[5]
    time_processed = year + '-' + mon + '-' + day + '-' + hour + '-' + minute
    return time_processed


def repeat(f, num, *args):
    for i in range(num):
        f(*args)


'''process search url'''
keywords_processed = ''
for oneKeyword in keywords:
    keywords_processed = keywords_processed + oneKeyword + '%20'
    if oneKeyword != keywords[-1]:
        keywords_processed = keywords_processed + 'OR%20'
url_twitterSearch = url_twitterSearchTemplate.format(
    keywords_processed, time_start, time_end, language)




'''Log in twitter'''
browser = webdriver.Chrome()
browserForGetReply = webdriver.Chrome()
url = 'https://twitter.com/login?lang=zh-cn'

print("tring to log in twitter right now")
browser.get(url)
my_usrname = browser.find_element_by_class_name('js-username-field')
my_usrname.click()
my_usrname.send_keys(usr_name)
time.sleep(2)
my_password = browser.find_element_by_class_name('js-password-field')
my_password.click()
time.sleep(0.5)
my_password.send_keys(password)
time.sleep(2)
my_login = browser.find_element_by_class_name('EdgeButtom--medium')
my_login.click()


browserForGetReply.get(url)
my_usrname1 = browserForGetReply.find_element_by_class_name(
    'js-username-field')
my_usrname1.click()
my_usrname1.send_keys(usr_name)
time.sleep(2)
my_password2 = browserForGetReply.find_element_by_class_name(
    'js-password-field')
my_password2.click()
time.sleep(0.5)
my_password2.send_keys(password)
time.sleep(2)
my_login2 = browserForGetReply.find_element_by_class_name('EdgeButtom--medium')
my_login2.click()

print('login accomplished')

browser.get(url_twitterSearch)

tweets_cont = 0

while(True):
    repeat(browser.execute_script, 50,
           "window.scrollTo(0, document.body.scrollHeight);")
    bs = BeautifulSoup(browser.page_source, "html.parser")
    tweets_all = bs.select('.tweet')
    if (len(tweets_all) < tweets_wanted):
        repeat(browser.execute_script, 50,
               "window.scrollTo(0, document.body.scrollHeight);")


for tweet in tweets_all:
    if (tweet.get('data-user-id') != None):
        nickname = tweet.select_one('.fullname').text
        usrId = tweet.get('data-user-id')
        content = tweet.select_one('.tweet-text').text
        tweetId = tweet.get('data-tweet-id')
        tweetTime = tweet.select_one('.tweet-timestamp').get('title')
        tweetTime = tweetTime_process(tweetTime)
        try:
            action_all = tweet.select_one('.ProfileTweet-actionCountList')
            replyNum = int(action_all.select_one('.ProfileTweet-action--reply').select_one(
                '.ProfileTweet-actionCount').get('data-tweet-stat-count'))
            retweetNum = int(action_all.select_one('.ProfileTweet-action--retweet').select_one(
                '.ProfileTweet-actionCount').get('data-tweet-stat-count'))
            favoriteNum = int(action_all.select_one('.ProfileTweet-action--favorite').select_one(
                '.ProfileTweet-actionCount').get('data-tweet-stat-count'))
        except:
            reply = tweet.select_one('.ProfileTweet-action--reply')
            if reply.select_one('.ProfileTweet-actionCount--isZero') == None:
                replyNum = reply.select_one(
                    '.ProfileTweet-actionCountForPresentation').text
            else:
                replyNum = 0
            retweet = tweet.select_one('.ProfileTweet-action--retweet')
            if retweet.select_one('.ProfileTweet-actionCount--isZero') == None:
                retweetNum = retweet.select_one(
                    '.ProfileTweet-actionCountForPresentation').text
            else:
                retweetNum = 0
            favorite = tweet.select_one('.ProfileTweet-action--favorite')
            if favorite.select_one('.ProfileTweet-actionCount--isZero') == None:
                favoriteNum = tweet.select_one(
                    '.ProfileTweet-actionCountForPresentation').text
            else:
                favoriteNum = 0

        loneReply = ['None']
        convReply = ['None']
        if replyNum != 0:
            browserForGetReply.get(url_tweetsTemplate.format(tweetId))
            # time.sleep(2)
            repeat(browser.execute_script, (replyNum % 5) + 1,
                    "window.scrollTo(0, document.body.scrollHeight);")
            bs_loneReply = BeautifulSoup(
                browserForGetReply.page_source, "html.parser")
            try:
                loneReply_all = bs_loneReply.select(
                    '.ThreadedConversation--loneTweet')
                print('The tweet ' + '[' + str(tweetId) +
                      '] ' + 'has lone reply, scraping now')
                loneReply.remove('None')
                for singleLoneReply in loneReply_all:
                    tweet_loneReply = singleLoneReply.selct_one('.tweet')
                    loneReply_tweetId = tweet_loneReply.get('data-item-id')
                    loneReply_usrId = tweet_loneReply.select_one(
                        '.fullname').text
                    loneReply_tweetTime = tweet_loneReply.select_one(
                        '.tweet-timestamp').get('data-original-title')
                    try:
                        loneReply_tweetTime = tweetTime_process(
                            loneReply_tweetTime)
                    except:
                        print('no loneReply_tweetTime')
                    loneReply_content = tweet_loneReply.select_one(
                        '.tweet-text').text
                    loneReply_replyNum = 0
                    try:
                        loneReply_action_all = singleLoneReply.select_one(
                            '.ProfileTweet-actionCountList')
                        loneReply_retweetNum = int(loneReply_action_all.select_one(
                            '.ProfileTweet-action--retweet').select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count'))
                        loneReply_favoriteNum = int(loneReply_action_all.select_one(
                            '.ProfileTweet-action--favorite').select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count'))
                    except:
                        loneReply_retweet = singleLoneReply.select_one(
                            '.ProfileTweet-action--retweet')
                        if loneReply_retweet.select_one('.ProfileTweet-actionCount--isZero') == None:
                            loneReply_retweetNum = singleLoneReply.select_one(
                                '.ProfileTweet-actionCountForPresentation').text
                        else:
                            loneReply_retweetNum = 0
                        loneReply_favorite = singleLoneReply.select_one(
                            '.ProfileTweet-action--favorite')
                        if loneReply_favorite.select_one('.ProfileTweet-actionCount--isZero') == None:
                            loneReply_favoriteNum = singleLoneReply.select_one(
                                '.ProfileTweet-actionCountForPresentation').text
                        else:
                            loneReply_favoriteNum = 0
                    loneReply_oneTweet = {'loneReply_tweetId': loneReply_tweetId,
                                          'loneReply_usrId': loneReply_usrId,
                                          'loneReply_tweetTime': loneReply_tweetTime,
                                          'loneReply_content': loneReply_content,
                                          'loneReply_replyNum': loneReply_replyNum,
                                          'loneReply_retweetNum': loneReply_retweetNum,
                                          'loneReply_favoriteNum': loneReply_favoriteNum
                                          }
                    loneReply.append(loneReply_oneTweet)
                print(
                    'Lone replies in the tweet [' + str(tweetId) + ']' + ' has been collected.')
            except:
                pass

            try:
                convReply_moreItems_all = browserForGetReply.find_elements_by_class_name(
                    'ThreadedConversation-moreReplies')
                for covReply_moreItem in convReply_moreItems_all:
                    moreReplyButton = covReply_moreItem.find_element_by_class_name(
                        'ThreadedConversation-moreRepliesLink')
                    moreReplyButton.click()
                    time.sleep(0.5)
            except:
                print('The tweet [' + str(tweetId) + ']' +
                      " has no 'more replies options'")
                pass

            try:
                bs_convReply = BeautifulSoup(
                    browserForGetReply.page_source, "html.parser")
                convReply_all = bs_convReply.select('.ThreadedConversation')
                convReply.remove('None')
                print('The tweet' + str(tweet_id) +
                      ' has convsersation reply, scraping now')
                for singleCovReply_all in convReply_all:
                    convReply_oneTweet = []
                    tweet_ConvReply_all = singleCovReply_all.select('.tweet')
                    for tweet_ConvReply in tweet_ConvReply_all:
                        convReply_nickname = tweet_ConvReply.select_one(
                            '.fullname').text
                        convReply_usrId = tweet_ConvReply.get('data-user-id')
                        convReply_content = tweet_ConvReply.select_one(
                            '.tweet-text').text
                        convReply_tweetId = tweet_ConvReply.get(
                            'data-tweet-id')
                        convReply_tweetTime = tweet_ConvReply.select_one(
                            '.tweet-timestamp').get('data-original-title')
                        try:
                            convReply_tweetTime = tweetTime_process(
                                convReply_tweetTime)
                        except:
                            print('no convReply_tweetTime')
                        convReply_single = {'convReply_nickname': convReply_nickname,
                                            'convReply_usrId': convReply_usrId,
                                            'convReply_content': convReply_content,
                                            'convReply_tweetId': convReply_tweetId,
                                            'convReply_tweetTime': convReply_tweetTime
                                            }
                        convReply_oneTweet.append(convReply_single)
                    convReply.append(convReply_oneTweet)
                print(
                    'Conversation replies in the tweet [' + str(tweetId) + ']' + ' has been collected.')
            except:
                print('The tweet [' + str(tweetId) + ']' +
                      ' has no conversation replies')
                pass
        tweetData_collected = {'nickname': nickname,
                               'usrId': usrId,
                               'content': content,
                               'tweetId': tweetId,
                               'tweetTime': tweetTime,
                               'replyNum': replyNum,
                               'retweetNum': retweetNum,
                               'favoriteNum': favoriteNum,
                               'loneReply': loneReply,
                               'convReply': convReply
                               }
        collection.insert(tweetData_collected)
        print('The tweet [' + str(tweetId) + ']' +
              ' has been scraped successfully!')
        tweets_cont += 1
print('Process in the end, num of scraped tweets: ', tweets_cont)
