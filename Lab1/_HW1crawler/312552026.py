import sys, time, requests, json, queue, threading, re, os
from bs4 import BeautifulSoup

outputStatus = False

threads = os.cpu_count()

totalPush = 0
totalBoo = 0
pushIdCnt = {}
booIdCnt = {}
keywordImageUrls = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "cookie": "over18=1",
}


def sleep():
    time.sleep(0.05)


def request(url):
    global outputStatus
    r = requests.get(url, headers=headers)
    while r.status_code != 200:
        if outputStatus:
            print("Request Error URL: ", url, "Code: ", r.status_code)
        sleep()
        r = requests.get(url, headers=headers)
    return r


def crawl():
    global outputStatus
    startTime = time.time()
    # create articles.jsonl
    print(
        "",
        end="",
        file=open("articles.jsonl", "w", encoding="utf-8"),
    )
    # create popular_articles.jsonl
    print(
        "",
        end="",
        file=open("popular_articles.jsonl", "w", encoding="utf-8"),
    )

    # Search to 2023
    url = "https://www.ptt.cc/bbs/Beauty/index.html"
    r = request(url)
    soup = BeautifulSoup(r.text.encode("utf-8"), "html.parser")
    prevPageUrl = soup.find_all("a", class_="btn wide")[1]["href"]
    page = int(re.findall(r"\d+", prevPageUrl)[0])
    while True:
        if outputStatus:
            print("Search to 2023, Page: ", page, end="\r", flush=True)
        url = "https://www.ptt.cc/bbs/Beauty/index" + str(page) + ".html"
        r = request(url)
        soup = BeautifulSoup(r.text.encode("utf-8"), "html.parser")
        # find all articles in the page
        articles = soup.find_all("div", class_="r-ent")
        for article in articles:
            articleDate = article.find("div", class_="date").text.strip()
            articleDate = articleDate.replace("/", "")
            if len(articleDate) == 3:
                articleDate = "0" + articleDate
            if articleDate == "1231":
                break
        if articleDate == "1231":
            break
        page -= 1
        sleep()
    lastPage = page
    finish = False

    # Crawl articles in 2023
    while True:
        if outputStatus:
            print("Crawl articles in 2023, Page: ", page, end="\r", flush=True)
        url = "https://www.ptt.cc/bbs/Beauty/index" + str(page) + ".html"
        r = request(url)
        soup = BeautifulSoup(r.text.encode("utf-8"), "html.parser")
        # find all articles in the page
        articles = soup.find_all("div", class_="r-ent")
        for article in articles:
            articleDate = article.find("div", class_="date").text.strip()
            articleDate = articleDate.replace("/", "")
            if len(articleDate) == 3:
                articleDate = "0" + articleDate
            articleData = {
                "date": articleDate,
                "title": article.find("div", class_="title").text.strip(),
                "url": (
                    "https://www.ptt.cc" + article.find("a")["href"]
                    if article.find("a")
                    else ""
                ),
            }
            # skip the missing url
            if "https://www.ptt.cc" == articleData["url"]:
                continue
            # skip the announcement
            if "[公告]" in articleData["title"]:
                continue
            # stop crawling if the article is in 2022
            if page < lastPage - 10 and articleDate == "1231":
                finish = True
                continue
            # skip the article if it is 2024
            if page == lastPage and articleDate == "0101":
                continue
            # save result
            print(
                json.dumps(articleData, ensure_ascii=False),
                file=open("articles.jsonl", "a", encoding="utf-8"),
            )
            # if the article is popular, write it to popular_articles.jsonl
            hit = article.find("div", "nrec").text.strip()
            if hit == "爆":
                print(
                    json.dumps(articleData, ensure_ascii=False),
                    file=open("popular_articles.jsonl", "a", encoding="utf-8"),
                )
        if finish:
            break
        page -= 1
        sleep()
    if outputStatus:
        print("\nTotal Time: ", round(time.time() - startTime, 2))


def calculatePushAndBoo(urlQueue):
    global totalPush, totalBoo, pushIdCnt, booIdCnt, outputStatus
    while not urlQueue.empty():
        url = urlQueue.get()
        if outputStatus:
            print("URL: ", url, end="\r", flush=True)
        r = request(url)
        soup = BeautifulSoup(r.text.encode("utf-8"), "html.parser")
        pushes = soup.find_all("div", class_="push")
        for push in pushes:
            pushTag = push.find("span", class_="push-tag").text.strip()
            pushId = push.find("span", class_="push-userid").text.strip()
            # calculate the number of push and boo
            if pushTag == "推":
                totalPush += 1
                if pushId not in pushIdCnt:
                    pushIdCnt[pushId] = 1
                else:
                    pushIdCnt[pushId] += 1
            elif pushTag == "噓":
                totalBoo += 1
                if pushId not in booIdCnt:
                    booIdCnt[pushId] = 1
                else:
                    booIdCnt[pushId] += 1
        urlQueue.task_done()
        sleep()


def push(startDate, endDate):
    global totalPush, totalBoo, pushIdCnt, booIdCnt, outputStatus
    startTime = time.time()
    # read articles.jsonl
    with open("articles.jsonl", "r", encoding="utf-8") as f:
        urlQueue = queue.Queue()
        for line in f:
            if startDate <= json.loads(line)["date"] <= endDate:
                urlQueue.put(json.loads(line)["url"])
    # create threads to calculate the number of push and boo
    threadList = []
    for i in range(threads):
        t = threading.Thread(target=calculatePushAndBoo, args=(urlQueue,))
        threadList.append(t)
        t.start()
    for t in threadList:
        t.join()
    # wait for all threads to finish
    urlQueue.join()
    # sort the result
    sortedPushIdCnt = sorted(
        pushIdCnt.items(), key=lambda x: (x[1], x[0]), reverse=True
    )
    sortedBooIdCnt = sorted(booIdCnt.items(), key=lambda x: (x[1], x[0]), reverse=True)
    # top 10 push and boo user
    top10PushIdCnt = []
    for user in sortedPushIdCnt[:10]:
        top10PushIdCnt.append({"user_id": user[0], "count": user[1]})
    top10BooIdCnt = []
    for user in sortedBooIdCnt[:10]:
        top10BooIdCnt.append({"user_id": user[0], "count": user[1]})
    result = {
        "push": {"total": totalPush, "top10": top10PushIdCnt},
        "boo": {"total": totalBoo, "top10": top10BooIdCnt},
    }
    # save result
    print(
        json.dumps(result, indent=4, ensure_ascii=False),
        end="",
        file=open(f"push_{startDate}_{endDate}.json", "w", encoding="utf-8"),
    )
    if outputStatus:
        print("\nTotal Time: ", round(time.time() - startTime, 2))


def popular(startDate, endDate):
    global outputStatus
    startTime = time.time()
    popularCnt = 0
    allImageUrl = []
    # read popular_articles.jsonl
    with open("popular_articles.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            # if the article is in the date range, find the image urls
            if startDate <= json.loads(line)["date"] <= endDate:
                url = json.loads(line)["url"]
                if outputStatus:
                    print("Popular Articles: ", url, end="\r", flush=True)
                popularCnt += 1
                r = request(url)
                # find all image urls in the article
                imageUrls = [
                    url
                    for url in re.findall(
                        "https?://[^\s]*\.(?:jpg|jpeg|png|gif)", r.text
                    )
                    if "cache.ptt.cc" not in url
                ]
                imageUrls = list(set(imageUrls))
                allImageUrl += imageUrls
                sleep()
    result = {"number_of_popular_articles": popularCnt, "image_urls": allImageUrl}
    # save the result
    print(
        json.dumps(result, indent=4, ensure_ascii=False),
        end="",
        file=open(f"popular_{startDate}_{endDate}.json", "w", encoding="utf-8"),
    )
    if outputStatus:
        print("\nTotal Time: ", round(time.time() - startTime, 2))


def searchKeyword(urlQueue, keyword):
    global keywordImageUrls, outputStatus
    while not urlQueue.empty():
        url = urlQueue.get()
        if outputStatus:
            print("URL: ", url, end="\r", flush=True)
        r = request(url)
        soup = BeautifulSoup(r.text.encode("utf-8"), "html.parser")
        content = soup.find("div", id="main-content").text
        # if the keyword is in the article, find the image urls
        if keyword in content.split("發信站")[0]:
            imageUrls = [
                url
                for url in re.findall("https?://[^\s]*\.(?:jpg|jpeg|png|gif)", r.text)
                if "cache.ptt.cc" not in url
            ]
            keywordImageUrls += imageUrls
        urlQueue.task_done()
        sleep()


def keyword(startDate, endDate, keyword):
    global keywordImageUrls
    startTime = time.time()
    # read articles.jsonl
    with open("articles.jsonl", "r", encoding="utf-8") as f:
        urlQueue = queue.Queue()
        for line in f:
            if startDate <= json.loads(line)["date"] <= endDate:
                urlQueue.put(json.loads(line)["url"])
    # create 5 threads to find the image urls
    threadList = []
    for i in range(threads):
        t = threading.Thread(target=searchKeyword, args=(urlQueue, keyword))
        threadList.append(t)
        t.start()
    for t in threadList:
        t.join()
    # wait for all threads to finish
    urlQueue.join()
    result = {"image_urls": keywordImageUrls}
    # save the result
    print(
        json.dumps(result, indent=4, ensure_ascii=False),
        end="",
        file=open(
            f"keyword_{startDate}_{endDate}_{keyword}.json", "w", encoding="utf-8"
        ),
    )
    if outputStatus:
        print("\nTotal Time: ", round(time.time() - startTime, 2))


if __name__ == "__main__":
    if sys.argv[1] == "crawl":
        crawl()
    elif sys.argv[1] == "push" and len(sys.argv) == 4:
        push(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "popular" and len(sys.argv) == 4:
        popular(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "keyword" and len(sys.argv) == 5:
        keyword(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Invalid Command")
