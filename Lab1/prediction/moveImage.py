import json, requests, time, re, urllib, os, queue, threading, shutil
from PIL import Image


if __name__ == "__main__":
    with open("dataset.csv", "r") as f:
        for line in f:
            url, isPopular = line.strip().split(",")
            if isPopular == "1":
                shutil.copy2(url, "dataset/true")
            else:
                shutil.copy2(url, "dataset/false")
            print(url)
