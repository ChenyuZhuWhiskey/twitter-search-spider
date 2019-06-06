import time
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
import json



def yearTodDays(year):
    dayCount = 0
    for oneYear in range(1, year+1):
        dayCount += 366 if year%4==0 else 365
    return dayCount

def countMonthToDays(mon,year):
    monCount = 0
    for oneMon in range(1, mon+1):
        if oneMon == 2:
            monCount += 29 if year%4 == 0 else 28
        elif oneMon <= 7:
            monCount += 30 if oneMon%2 == 0 else 31
        else:
            monCount += 31 if oneMon%2 ==0 else 30
    return monCount
                

def searchTimeSplit(time_start, time_end):
    '''Split search time by days'''
    startTimeArr = time_start.split('-')
    endTimeArr = time_end.split('-')
    for i in range(len(startTimeArr)):
        startTimeArr[i] = int(startTimeArr[i])
        endTimeArr[i] = int(endTimeArr[i])

    dayCount = (yearTodDays(endTimeArr[0]) + countMonthToDays(endTimeArr[1],endTimeArr[0]) + endTimeArr[2]) - (yearTodDays(startTimeArr[0]) + monToDays(startTimeArr[1],endTimeArr[0]) + startTimeArr[2])
    print('search days span: ' ,dayCount)
    date_startTime = datetime.date(startTimeArr[0],startTimeArr[1],startTimeArr[2])
    timeSpan = [str(date_startTime)]
    date_afterPlus = date_startTime
    for _ in range(dayCount):
        delta = datetime.timedelta(days=1)
        date_afterPlus = date_afterPlus + delta
        timeSpan.append(str(date_afterPlus))
    return timeSpan

def monthStrtoNum(monStr):
    month_strDict = {'Jan':'01','Feb':'02','Mar':'03','Apr':'30','May':'31','Jun':'30','Jul':'31','Aug':'31','Sep':'30','Oct':'31','Nov':'30','Dec':'31'}
    return month_strDict.get(monStr)

def tweetTime_process(tweetTime):
    hour = tweetTime.split()[0].split(':')[0]
    minute = tweetTime.split()[0].split(':')[1]
    isAM = True if tweetTime.split()[1] == 'AM' else False
    day = tweetTime.split()[3]
    if not isAM:
        hour = str(int(hour)+12)
    mon_str = tweetTime.split()[4]
    mon_num = monthStrtoNum(mon_str)
    year = tweetTime.split()[5]
    time_processed = year + '-' + mon_num + '-' + day + '-' + hour + '-' + minute
    return time_processed

def getTwitterSearchUrl(keywords, time_start, time_end):
    '''process search url'''
    url_twitterSearchTemplate = 'https://twitter.com/search?f=tweets&q={}since%3A{}%20until%3A{}&src=typd&laneg=en'
    keywords_processed = ''
    for oneKeyword in keywords:
        keywords_processed = keywords_processed + oneKeyword + '%20'
        if oneKeyword != keywords[-1]:
            keywords_processed = keywords_processed + 'OR%20'
    url_twitterSearch = url_twitterSearchTemplate.format(
        keywords_processed, time_start, time_end)
    return url_twitterSearch

getTweetUrl = lambda tweet_id: 'https://twitter.com/APompliano/status/{}'.format(tweet_id)

def scrollPageToEnd(browser):
    time_scrollStart = time.time()
    while(time.time() - time_scrollStart < 600):
        try:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            browser.implicitly_wait(0.5)
        except:
           time.sleep(1)
        
    print('scroll finished, start collecting')

def collectTweetData(browser,keywords, time_start, time_end):
    tweetData_collected = []
    tweetData_count = 0
    searchUrl = getTwitterSearchUrl(keywords, time_start, time_end)
    try:
        browser.get(searchUrl)
        time.sleep(5)
    except:
        browser.get(searchUrl)
        time.sleep(30)
    print(searchUrl)
    scrollPageToEnd(browser)
    bs = BeautifulSoup(browser.page_source,"html.parser")
    tweets_all = bs.select('.tweet')
    for tweet in tweets_all:
        if (tweet.get('data-user-id') is not None and tweet.select_one('.tweet-text') is not None):
            tweet_nickname = tweet.get('data-name')
            tweet_usrId = tweet.get('data-user-id')
            tweet_content = tweet.select_one('.tweet-text').text
            tweet_tweetId = tweet.get('data-tweet-id')
            tweet_tweetTime = tweet.select_one('.tweet-timestamp').get('data-original-title')
            if tweet_tweetTime == None:
                tweet_tweetTime = tweet.select_one('.tweet-timestamp').get('title')
            tweet_tweetTime_afterProcess = tweetTime_process(tweet_tweetTime)

            tweet_actions_all = tweet.select_one('.ProfileTweet-actionList')

            tweet_action_reply = tweet_actions_all.select_one('.ProfileTweet-action--reply')
            if tweet_action_reply.select_one('.ProfileTweet-actionCount--isZero') != None:
                tweet_replyNum = 0 
            elif tweet_action_reply.select_one('.ProfileTweet-actionCountForPresentation') != None:
                tweet_replyNum = tweet_action_reply.select_one('.ProfileTweet-actionCountForPresentation').text
            else:
                tweet_replyNum = tweet_action_reply.select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count')

            tweet_action_retweet = tweet_actions_all.select_one('.ProfileTweet-action--retweet')
            if tweet_action_retweet.select_one('.ProfileTweet-actionCount--isZero') != None:
                tweet_retweetNum = 0 
            elif tweet_action_retweet.select_one('.ProfileTweet-actionCountForPresentation') != None:
                tweet_retweetNum = tweet_action_retweet.select_one('.ProfileTweet-actionCountForPresentation').text
            else:
                tweet_retweetNum = tweet_action_retweet.select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count')

            tweet_action_favorite = tweet_actions_all.select_one('.ProfileTweet-action--favorite')
            if tweet_action_favorite.select_one('.ProfileTweet-actionCount--isZero') != None:
                tweet_favoriteNum = 0 
            elif tweet_action_favorite.select_one('.ProfileTweet-actionCountForPresentation') != None:
                tweet_favoriteNum = tweet_action_favorite.select_one('.ProfileTweet-actionCountForPresentation').text
            else:
                tweet_favoriteNum = tweet_action_favorite.select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count')
            
            try:
                tweet_replyNum = int(tweet_replyNum)
            except:
                tweet_replyNum = int(float(tweet_replyNum.split('K')[0])*1000)
            try:
                tweet_retweetNum = int(tweet_retweetNum)
            except:
                tweet_retweetNum = int(float(tweet_retweetNum.split('K')[0])*1000)
            try:
                tweet_favoriteNum = int(tweet_favoriteNum)
            except:
                tweet_favoriteNum = int(float(tweet_favoriteNum.split('K')[0])*1000)
            
            
            tweetData_collected_oneTweet = [tweet_nickname,
                                            tweet_usrId,
                                            tweet_content,
                                            tweet_tweetId,
                                            tweet_tweetTime_afterProcess,
                                            tweet_replyNum,
                                            tweet_favoriteNum,
                                            tweet_retweetNum,
                                        ]
            
            #print(tweetData_collected_oneTweet)
            tweetData_collected.append(tweetData_collected_oneTweet)
            tweetData_count += 1
    print('tweet data between ' + time_start + ' and ' + time_end + ' has been collected')
    print('num of tweets: ', tweetData_count)
    return tweetData_collected, tweetData_count


                        
if __name__ == '__main__':

    '''covered search area'''
    keywords = ['bitcoin', 'BTC']
    time_start = '2019-06-02'
    time_end = '2019-06-03'

    fileName = 'data_twitter_noComments_from{}_to{}'.format(time_start,time_end)

    fp = open(fileName,'w')


    '''Log in twitter'''
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    #global browserForGetReply
    browser = webdriver.Chrome()
    #browserForGetReply = webdriver.Chrome()
    browser.set_page_load_timeout(30)
    #browserForGetReply.set_page_load_timeout(30)

    tweetData_all = [[],[],[],[],[],[],[],[]]
    tweetData_count_all = 0
    timeSearchSpan = searchTimeSplit(time_start,time_end)
    for i in range(len(timeSearchSpan) - 1):
        tweetData_oneDay, tweetData_count_oneDay = collectTweetData(browser,keywords, timeSearchSpan[i], timeSearchSpan[i+1])
        for j in range(len(tweetData_oneDay)):
            for k in range(len(tweetData_all)):
                tweetData_all[k].append(tweetData_oneDay[j][k])
        tweetData_count_all += tweetData_count_oneDay
    #collection.insert_one(tweetData_all)
    json.dump(tweetData_all,fp,ensure_ascii=False)
    print('----all tweets data has been collected successfully!----')
    print('total: ', tweetData_count_all)
    fp.close()
