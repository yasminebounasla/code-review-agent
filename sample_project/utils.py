import time
import math
import sys

def calculate_discount(price, discount):
    return price - (price * discount / 100)

def fetch_data(url):
    import urllib.request
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        return data
    except:
        pass

def process_list(items):
    result = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == items[j] and i != j:
                if items[i] not in result:
                    result.append(items[i])
    return result

def read_config(path):
    f = open(path)
    content = f.read()
    return content

def divide_all(numbers, divisor):
    results = []
    for n in numbers:
        results.append(n/divisor)
    return results

TMP=[]
CACHE={}
counter = 0

def increment():
    global counter
    counter = counter+1
    return counter