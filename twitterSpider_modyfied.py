import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
import datetime


'''setting login account'''
usrname = 'chenyu_zhu@protonmail.com'
password = 'IrishWhiskey233'

def yearTodDays(year):
    dayCount = 0
    for oneYear in range(1, year+1):
        dayCount += 366 if year%4==0 else 365
    return dayCount

def monToDays(mon,year):
    monCount = 0
    for oneMon in range(1, mon+1):
        if oneMon == 2:
            monCount += 29 if year%4 == 0 else 28
        elif oneMon <= 7:
            monCount += 30 if oneMon%2 == 0 else 31
        else:
            monCOunt += 31 if oneMon%2 ==0 else 30
    return monCount
                

def searchTimeSplit(time_start, time_end):
    '''Split search time by days'''
    startTimeArr = time_start.split('-')
    endTimeArr = time_end.split('-')
    for i in range(len(startTimeArr)):
        startTimeArr[i] = int(startTimeArr[i])
        endTimeArr[i] = int(endTimeArr[i])

    dayCount = (yearTodDays(endTimeArr[0]) + monToDays(endTimeArr[1],endTimeArr[0]) + endTimeArr[2]) - (yearTodDays(startTimeArr[0]) + monToDays(startTimeArr[1],endTimeArr[0]) + startTimeArr[2])
    print('search days span: ' ,dayCount)
    date_startTime = datetime.date(startTimeArr[0],startTimeArr[1],startTimeArr[2])
    timeSpan = [str(date_startTime)]
    date_afterPlus = date_startTime
    for _ in range(dayCount+1):
        delta = datetime.timedelta(days=1)
        date_afterPlus = date_afterPlus + delta
        timeSpan.append(str(date_afterPlus))
    return timeSpan

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

def scrollPageToEnd():
    bs_beforeScroll = BeautifulSoup(browser.page_source, "html.parser")
    tweetsCount_beforeScroll = len(bs_beforeScroll.select('.tweet'))
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    bs_afterScroll = BeautifulSoup(browser.page_source, "html.parser")
    tweetsCount_afterScroll = len(bs_afterScroll.select('.tweet'))
    if(tweetsCount_beforeScroll < tweetsCount_afterScroll):
        print('tweets num before scroll: ', tweetsCount_beforeScroll)
        print('tweets num before scroll: ', tweetsCount_afterScroll)
        scrollPageToEnd()

def collectTweetData(keywords, time_start, time_end):
    tweetData_collected = []
    tweetData_count = 0
    searchUrl = getTwitterSearchUrl(keywords, time_start, time_end)
    browser.get(searchUrl)
    scrollPageToEnd()
    bs = BeautifulSoup(browser.page_source,"html.parser")
    tweets_all = bs.select('.tweet')
    for tweet in tweets_all:
        if (tweet.get('data-user-id') != None):
            tweet_nickname = tweet.select_one('.fullname').text
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
            
            tweet_replyNum = int(tweet_replyNum)
            tweet_retweetNum = int(tweet_retweetNum)
            tweet_favoriteNum = int(tweet_favoriteNum)
            tweet_loneReply = ['None']
            tweet_convReply = ['None']
            if (tweet_replyNum != 0):
                tweet_url =  getTweetUrl(tweet_tweetId)
                browserForGetReply.get(tweet_url)
                scrollPageToEnd()
                bs_loneReply = BeautifulSoup(browserForGetReply.page_source, "html.parser")
                if (bs_loneReply.select_one('.ThreadedConversation--loneTweet') != None):
                    print('the tweet ' + str(tweet_tweetId) + ' has lone reply, collecting now')
                    tweet_loneReply.remove('None')
                    loneReply_all = bs_loneReply.select('.ThreadedConversation--loneTweet')
                    for loneReply_oneReply in loneReply_all:
                        tweet_loneReply_oneReply = loneReply_oneReply.select_one('.tweet')
                        loneReply_tweetId = tweet_loneReply_oneReply.get('data-item-id')
                        loneReply_usrId = tweet_loneReply_oneReply.select_one('.fullname').text
                        loneReply_tweetTime = tweet_loneReply_oneReply.select_one('.tweet-timestamp').get('data-original-title')
                        if loneReply_tweetTime == None:
                            loneReply_tweetTime = tweet_loneReply_oneReply.select_one('.tweet-timestamp').get('title')
                        loneReply_tweetTime_afterProcess = tweetTime_process(loneReply_tweetTime)
                        loneReply_content = tweet_loneReply_oneReply.select_one('.tweet-text').text
                        loneReply_replyNum = 0

                        loneReply_actions_all = tweet_loneReply_oneReply.select_one('.ProfileTweet-actionList')

                        loneReply_action_retweet = loneReply_actions_all.select_one('.ProfileTweet-action--retweet')
                        if loneReply_action_retweet.select_one('.ProfileTweet-actionCount--isZero') != None:
                            loneReply_retweetNum = 0 
                        elif loneReply_action_retweet.select_one('.ProfileTweet-actionCountForPresentation') != None:
                            loneReply_retweetNum = loneReply_action_retweet.select_one('.ProfileTweet-actionCountForPresentation').text
                        else:
                            loneReply_retweetNum = loneReply_action_retweet.select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count')

                        loneReply_action_favorite = loneReply_actions_all.select_one('.ProfileTweet-action--favorite')
                        if loneReply_action_favorite.select_one('.ProfileTweet-actionCount--isZero') != None:
                            loneReply_favoriteNum = 0 
                        elif loneReply_action_favorite.select_one('.ProfileTweet-actionCountForPresentation') != None:
                            loneReply_favoriteNum = loneReply_action_favorite.select_one('.ProfileTweet-actionCountForPresentation').text
                        else:
                            loneReply_favoriteNum = loneReply_action_favorite.select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count')
                        loneReply_retweetNum = int(loneReply_retweetNum)
                        loneReply_favoriteNum = int(loneReply_favoriteNum)
                        loneReply_oneTweet = {'loneReply_tweetId': loneReply_tweetId,
                                              'loneReply_usrId': loneReply_usrId,
                                              'loneReply_tweetTime': loneReply_tweetTime_afterProcess,
                                              'loneReply_content': loneReply_content,
                                              'loneReply_replyNum': loneReply_replyNum,
                                              'loneReply_retweetNum': loneReply_retweetNum,
                                              'loneReply_favoriteNum': loneReply_favoriteNum
                                              }
                        tweet_loneReply.append(loneReply_oneTweet)
                    print('the lone reply in tweet ' + str(tweet_tweetId) + ' has been collected')
                elif (bs_loneReply.select_one('.ThreadedConversation') != None):
                    print('the tweet' + str(tweet_tweetId) + ' has conversation reply, collecting now')
                    tweet_convReply.remove('None')
                    try:
                        convReply_moreItems_all = browserForGetReply.find_elements_by_class_name('ThreadedConversation-moreReplies')
                        for covReply_moreItem in convReply_moreItems_all:
                            moreReplyButton = covReply_moreItem.find_element_by_class_name('ThreadedConversation-moreRepliesLink')
                            moreReplyButton.click()
                            time.sleep(0.5)
                    except:
                        pass
                    bs_convReply = BeautifulSoup(browserForGetReply.page_source, "html.parser")
                    convReply_all = bs_convReply.select('.ThreadedConversation')
                    
                    for convReply_oneReply in convReply_all:
                        convReply_oneTweet = []
                        tweet_convReply_oneTweet = convReply_oneReply.select('.tweet')
                        for tweet_convReply_oneReply in tweet_convReply_oneTweet:
                            convReply_tweetId = tweet_convReply_oneReply.get('data-item-id')
                            convReply_usrId = tweet_convReply_oneReply.select_one('.fullname').text
                            convReply_tweetTime = tweet_convReply_oneReply.select_one('.tweet-timestamp').get('data-original-title')
                            if convReply_tweetTime == None:
                                convReply_tweetTime = tweet_convReply_oneReply.select_one('.tweet-timestamp').get('title')
                            convReply_tweetTime_afterProcess = tweetTime_process(convReply_tweetTime)
                            convReply_content = tweet_convReply_oneReply.select_one('.tweet-text').text

                            convReply_actions_all = tweet_convReply_oneReply.select_one('.ProfileTweet-actionList')

                            convReply_action_reply = convReply_actions_all.select_one('.ProfileTweet-action--reply')
                            if convReply_action_reply.select_one('.ProfileTweet-actionCount--isZero') != None:
                                convReply_replyNum = 0 
                            elif convReply_action_reply.select_one('.ProfileTweet-actionCountForPresentation') != None:
                                convReply_replyNum = convReply_action_reply.select_one('.ProfileTweet-actionCountForPresentation').text
                            else:
                                convReply_replyNum = convReply_action_reply.select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count')

                            convReply_action_retweet = convReply_actions_all.select_one('.ProfileTweet-action--retweet')
                            if convReply_action_retweet.select_one('.ProfileTweet-actionCount--isZero') != None:
                                convReply_retweetNum = 0 
                            elif convReply_action_retweet.select_one('.ProfileTweet-actionCountForPresentation') != None:
                                convReply_retweetNum = convReply_action_retweet.select_one('.ProfileTweet-actionCountForPresentation').text
                            else:
                                convReply_retweetNum = convReply_action_retweet.select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count')

                            convReply_action_favorite = convReply_actions_all.select_one('.ProfileTweet-action--favorite')
                            if convReply_action_favorite.select_one('.ProfileTweet-actionCount--isZero') != None:
                                convReply_favoriteNum = 0 
                            elif convReply_action_favorite.select_one('.ProfileTweet-actionCountForPresentation') != None:
                                convReply_favoriteNum = convReply_action_favorite.select_one('.ProfileTweet-actionCountForPresentation').text
                            else:
                                convReply_favoriteNum = convReply_action_favorite.select_one('.ProfileTweet-actionCount').get('data-tweet-stat-count')

                            convReply_replyNum = int(convReply_replyNum)
                            convReply_retweetNum = int(convReply_retweetNum)
                            convReply_favoriteNum = int(convReply_favoriteNum)
                            convReply_oneReply = {'convReply_usrId': convReply_usrId,
                                                  'convReply_content': convReply_content,
                                                  'convReply_tweetId': convReply_tweetId,
                                                  'convReply_tweetTime': convReply_tweetTime_afterProcess,
                                                  'convReply_replyNum': convReply_replyNum,
                                                  'convReply_retweetNum': convReply_retweetNum,
                                                  'convReply_favoriteNum': convReply_favoriteNum
                                                  }
                            convReply_oneTweet.append(convReply_oneReply)
                        tweet_convReply.append(convReply_oneTweet)
            tweetData_collected_oneTweet = {'tweet_nickname': tweet_nickname,
                                            'tweet_usrId': tweet_usrId,
                                            'tweet_content': tweet_content,
                                            'tweet_tweetId': tweet_tweetId,
                                            'tweet_tweetTime': tweet_tweetTime_afterProcess,
                                            'tweet_replyNum': tweet_replyNum,
                                            'tweet_favoriteNum': tweet_favoriteNum,
                                            'tweet_loneReply': tweet_loneReply,
                                            'tweet_convReply': tweet_convReply
                                            }
            print(tweetData_collected_oneTweet)
            tweetData_collected.append(tweetData_collected_oneTweet)
            tweetData_count += 1
    print('tweet data between ' + time_start + ' and ' + time_end + ' has been collected')
    return tweetData_collected, tweetData_count


                        
if __name__ == '__main__':
    '''covered search area'''
    keywords = ['bitcoin', 'BTC']
    time_start = '2019-05-21'
    time_end = '2019-05-27'


    '''Log in twitter'''
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    global browser
    global browserForGetReply
    browser = webdriver.Chrome(chrome_options=option)
    browserForGetReply = webdriver.Chrome(chrome_options=option)
    browser.set_page_load_timeout(30)
    browserForGetReply.set_page_load_timeout(30)

    url = 'https://twitter.com/login?lang=en'

    print("tring to log in twitter right now")
    browser.get(url)
    my_usrname = browser.find_element_by_class_name('js-username-field')
    my_usrname.click()
    my_usrname.send_keys(usrname)
    my_password = browser.find_element_by_class_name('js-password-field')
    my_password.click()
    my_password.send_keys(password)
    my_login = browser.find_element_by_class_name('EdgeButtom--medium')
    my_login.click()


    browserForGetReply.get(url)
    my_usrname1 = browserForGetReply.find_element_by_class_name(
        'js-username-field')
    my_usrname1.click()
    my_usrname1.send_keys(usrname)
    my_password2 = browserForGetReply.find_element_by_class_name(
        'js-password-field')
    my_password2.click()
    my_password2.send_keys(password)
    my_login2 = browserForGetReply.find_element_by_class_name('EdgeButtom--medium')
    my_login2.click()

    print('login accomplished')

    tweetData_all = {}
    tweetData_count_all = 0
    timeSearchSpan = searchTimeSplit(time_start,time_end)
    for i in range(len(timeSearchSpan) - 1):
        tweetData_oneDay, tweetData_count_oneDay = collectTweetData(keywords, timeSearchSpan[i], timeSearchSpan[i+1])
        tweetData_all[timeSearchSpan[i]] = timeSearchSpan
        tweetData_count_all += tweetData_count_oneDay
    print('----all tweets data has been collected successfully!----')
    print('total: ', tweetData_count_all)

