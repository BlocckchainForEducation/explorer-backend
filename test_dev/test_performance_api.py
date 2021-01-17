import time
import requests
import json


def submit(num_tran, max_batch):
    import requests

    url = "http://139.59.125.235:8005/test_time_submit_transaction"

    payload = {"numberTransaction": num_tran,
               "maxBatchSize": max_batch}
    parsed = json.dumps(payload)
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': '<calculated when request is sent>',
        'Connection': 'keep-alive'
    }
    response = requests.request("POST", url, headers=headers, data=parsed)
    return json.loads(response.text)


def test_transcript(max_batch=200):

    for i in range(1, 30):
        num_tran = i * i
        while True:
            print("send " + str(num_tran) + " transactions")
            res = submit(num_tran, max_batch)
            print(res)
            if res.get("commitTime"):
                if res.get("commitTime") > 0.5:
                    break
            print("sleep " + str(i))
            time.sleep(i)

    print("done !check in db")


def test_same_tran_num():
    num_tran = 1000
    for i in range(1, 1001):
        max_batch = i
        while True:
            print("send " + str(num_tran) + " with max batch :" + max_batch)
            res = submit(num_tran, max_batch)
            print(res)
            if res.get("commitTime"):
                if res.get("commitTime") > 0.5:
                    break
            print("sleep " + str(i))
            time.sleep(i)


test_transcript()

# print(submit(1, 1000))
