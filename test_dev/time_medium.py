import test_dev.data as data_collection

max_batch_sizes = []
time_commit = []
num_tran = 0
time_ = 0
num = 0
for data in data_collection.data:
    tran = data.get("num_transactions")
    time = data.get("commit_time")
    max_batch_size = data.get("max_batch_size")

    max_batch_sizes.append(max_batch_size)
    time_commit.append(time)
    num_tran += tran
    time_ += time
    num = num + 1
print("num" + str(num))
print("time medium: " + str(time_ / num))
