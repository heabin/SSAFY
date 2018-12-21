# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from slacker import Slacker
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template



slack = Slacker('xoxb-507380538243-507421535427-Zh8gEdFP575b8JnEHyNCa1xF')
# Get users list
response = slack.users.list()
users = response.body['members']

# If you need to proxy the requests
proxy_endpoint = 'http://myproxy:3128'
slack = Slacker('xoxb-507380538243-507421535427-Zh8gEdFP575b8JnEHyNCa1xF',
                http_proxy=proxy_endpoint,
                https_proxy=proxy_endpoint)

app = Flask(__name__)

slack_token = "xoxb-507380538243-507421535427-Zh8gEdFP575b8JnEHyNCa1xF"
slack_client_id = "507380538243.507419964291"
slack_client_secret = "5739c8c0426e3f7b4cb01d3a10f7bfc8"
slack_verification = "BrL9pEWdpqWqYlRIkjquUrIi"
sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    # 여기에 함수를 구현해봅시다.
    url = "http://www.jobkorea.co.kr/Top100/?Main_Career_Type=1&Search_Type=1&BizJobtype_Bctgr_Code=10016&BizJobtype_Bctgr_Name=IT%C2%B7%EC%9D%B8%ED%84%B0%EB%84%B7&Major_Big_Code=0&Major_Big_Name=%EC%A0%84%EC%B2%B4&Edu_Level_Code=9&Edu_Level_Name=%EC%A0%84%EC%B2%B4"
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")

    keywords = []

    i = 1

    for keyword,title,day in zip(soup.find_all("a", class_="coLink"),soup.find_all("a", class_="link"),soup.find_all("span", class_="day")):
        if i < 11:
            x = "{index}위: {keyword} - {title} / {day}".format(index=i, keyword=keyword.get_text().strip(), title=title.get_text().strip(),day=day.get_text().strip())
            # x = str(i)+"위: "+keyword.get_text() +" / "+ name.get_text()
            keywords.append(x)
            print(x)
            i += 1

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.

    return u'\n'.join(keywords)


def _crawl_job_keywords(text):
    # 여기에 함수를 구현해봅시다.
    url = "http://www.jobkorea.co.kr/Top100/?Main_Career_Type=2&Search_Type=1&BizJobtype_Bctgr_Code=10016&BizJobtype_Bctgr_Name=IT%C2%B7%EC%9D%B8%ED%84%B0%EB%84%B7&Major_Big_Code=0&Major_Big_Name=%EC%A0%84%EC%B2%B4&Edu_Level_Code=9&Edu_Level_Name=%EC%A0%84%EC%B2%B4"
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")

    keywords = []

    i = 1

    for keyword in (soup.find_all("div", class_="Tit")):
        if (text in keyword):
            x = "{index}부문: {keyword} - {title} / {day}".format(index=i, keyword=keyword.get_text().strip())

            # x = str(i)+"위: "+keyword.get_text() +" / "+ name.get_text()
            keywords.append(x)
            print(x)
            i += 1

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.

    return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        if('안녕' in text):
            print('**************************************************')
            #slack.chat.post_message('#general', 'Hello!')
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text="#####################################################"+ "\n"+
                     '안녕하세요 오늘의 취업정보를 알려드리겠습니다!' + "\n" +
                     "#####################################################" + "\n"
            )


        if ('신입' in text):
            print('**************************신입************************')
            keywords = _crawl_naver_keywords(text)
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords
            )

        if ('경력' in text):
            print('*************************경력*************************')
            keywords = _crawl_job_keywords(text)
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords
            )



        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)
