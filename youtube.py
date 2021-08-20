import json

import requests
import asyncio
import csv
import time
from timeit import default_timer
from concurrent.futures import ThreadPoolExecutor

START_TIME = default_timer()


def read_csv():
    result = []
    with open('test/youtube/valid.csv_split_ae') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                url = "http://localhost:8000/youtube/v3/search?"
                url = "https://www.googleapis.com/youtube/v3/search?"
                parameters = row[11].replace(";", "&")
                parameters = parameters.replace(":", "=")
                #parameters = parameters.replace("AUTHENTICATION_TOKEN_HERE", "apikey")
                parameters = parameters.replace("AUTHENTICATION_TOKEN_HERE", "apikey")
                if 'key' not in parameters:
                    #parameters = parameters + "&key=apikey"
                    parameters = parameters + "&key=apikey"

                allparameters = parameters.split("&")
                for letter in allparameters:
                    if 'publishedBefore' in letter or 'publishedAfter' in letter:
                        allparameters.remove(letter)
                        date = letter.split("=")
                        date = date[0] + "=" + ':'.join(date[1:])
                        allparameters.append(date)
                allparameters = "&".join(allparameters)
                request = url + allparameters
                result.append(request)
                line_count += 1
    return result


# https://60f496853cb0870017a8a294.mockapi.io/api/pages/1

def request_youtube(session, url):
    start = time.time()
    # url = "https://60f496853cb0870017a8a294.mockapi.io/api/pages/" + id
    with session.get(url, headers={
        #'Host': 'real-youtube-simple',
        # "x-access-token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI1YWIyODdiZmVmYmM2YzA0YzhlYzBjYWMifQ.8YvGhKiM9Ayehal2zod5pdHL3VGA-BXINkwZfoehD40",
        'accept': 'application/json'}) as response:
        data = response.text
        end = time.time()
        elapsed_time = end - start
        completed_at = "{:5.2f}s".format(elapsed_time)
        body = json.dumps(response.json())
        detected = "false"
        if 'IdlReasoner' in body:
            detected = "true"
        print(completed_at+","+str(detected)+","+str(response.status_code)+","+url+","+"'"+body+"'")
        return data


async def start_async_process():
    print("{0:<30} {1:>20} {2:>20}".format("Iccid", "Completed at", "Http Code"))
    list_to_process = read_csv()

    with ThreadPoolExecutor(max_workers=200) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    request_youtube,
                    *(session, i)
                )
                for i in list_to_process
            ]
            for response in await asyncio.gather(*tasks):
                pass
                print(response)


def start_sync_process():
    list_to_process = read_csv()
    count = 0
    with requests.Session() as session:
        for i in list_to_process:
            request_youtube(session, i)


if __name__ == "__main__":
    # loop = asyncio.get_event_loop(

    # future = asyncio.ensure_future(start_async_process())
    # loop.run_until_complete(future)
    start_sync_process()
