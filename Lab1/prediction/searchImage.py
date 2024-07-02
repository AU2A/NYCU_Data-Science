import sys, time, requests, json, queue, threading, re
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "cookie": "over18=1",
}


def searchImageURL(urlQueue, imageURL):
    while not urlQueue.empty():
        url = urlQueue.get()
        print(url)
        r = requests.get(url, headers=headers)
        while r.status_code != 200:
            print("Request Error URL: ", url, "Code: ", r.status_code)
            time.sleep(0.1)
            r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text.encode("utf-8"), "html.parser")
        pushes = soup.find_all("div", class_="push")
        hits = 0
        for push in pushes:
            pushTag = push.find("span", class_="push-tag").text.strip()
            if pushTag == "推":
                hits += 1
            elif pushTag == "噓":
                hits -= 1
        imageUrls = [
            url
            for url in re.findall("https?://[^\s]*\.(?:jpg|png|gif|jpeg)", r.text)
            if "cache.ptt.cc" not in url
        ]
        imageUrls = list(set(imageUrls))
        if hits > 35:
            isPopular = 1
        else:
            isPopular = 0
        for imageUrl in imageUrls:
            imageURL.append((imageUrl, isPopular))
        urlQueue.task_done()
        time.sleep(0.05)


if __name__ == "__main__":
    urlQueue = queue.Queue()
    imageURL = []
    with open("articles.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            print(json.loads(line))
            url = json.loads(line)["url"]
            urlQueue.put(url)
    threadList = []
    for i in range(20):
        t = threading.Thread(target=searchImageURL, args=(urlQueue, imageURL))
        threadList.append(t)
        t.start()
    for t in threadList:
        t.join()
    urlQueue.join()
    print("", end="", file=open("imageURL.csv", "w", encoding="utf-8"))
    for imageUrl, isPopular in imageURL:
        print(
            f"{imageUrl},{isPopular}",
            file=open("imageURL.csv", "a", encoding="utf-8"),
        )
