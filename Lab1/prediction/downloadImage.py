import json, requests, time, re, urllib, os, queue, threading, random

# from PIL import Image
from bs4 import BeautifulSoup

downloadPath = "testImage/"

# threads = os.cpu_count()
threads = 10

opener = urllib.request.build_opener()
opener.addheaders = [
    (
        "User-Agent",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
    )
]
urllib.request.install_opener(opener)


def download(images):
    while not images.empty():
        imageUrl, isPopular, idx = images.get()
        print(imageUrl, isPopular, idx)
        imageName = idx + "." + imageUrl.split(".")[-1]
        try:
            local_filename, headers = urllib.request.urlretrieve(
                imageUrl, f"{downloadPath}{imageName}"
            )
            if int(headers.get("Content-Length")) != 503:
                print(
                    f"{downloadPath}{imageName},{isPopular}",
                    file=open("test.csv", "a", encoding="utf-8"),
                )
            else:
                os.remove(f"{downloadPath}{imageName}")
        except:
            print("Download Error: ", imageUrl)
            images.task_done()
            continue
        images.task_done()
        time.sleep(0.3)


if __name__ == "__main__":
    print(
        "",
        end="",
        file=open("test.csv", "w", encoding="utf-8"),
    )
    images = queue.Queue()
    idx = 0
    with open("data/imageURL.csv", "r", encoding="utf-8") as f:
        for line in f:
            idx += 1
            imageUrl, isPopular = line.strip().split(",")
            if "gif" not in imageUrl:
                if random.random() < 0.2:
                    images.put((imageUrl, isPopular, str(idx).zfill(5)))
    threadList = []
    for i in range(threads):
        t = threading.Thread(target=download, args=(images,))
        threadList.append(t)
        t.start()
    for t in threadList:
        t.join()
    images.join()
