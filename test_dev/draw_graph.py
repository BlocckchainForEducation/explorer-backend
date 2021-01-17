import matplotlib.pyplot as plt
import test_dev.data as data_collection

trans = []
time_commit = []
num_tran = 0
time_ = 0
mb = 500
for data in data_collection.data:
    tran = data.get("num_transactions")
    time = data.get("commit_time")
    max_batch_size = data.get("max_batch_size")
    if time < 0.5 or max_batch_size != mb:
        continue
    trans.append(tran)
    time_commit.append(time)
    num_tran += tran
    time_ += time

plt.plot(trans, time_commit)

# naming the x axis
plt.xlabel('Số lượng giao dịch')
# naming the y axis
plt.ylabel('thời gian hoàn thành(s)')

# giving a title to my graph
# plt.title('Kích thước lô = ' + str(data_collection.data[0].get("max_batch_size")) +
#           '; giá trị trung bình :' + str(round(num_tran / time_, 2)) + " giao dịch/s")
plt.title('Kích thước lô = ' + str(mb) +
          '; giá trị trung bình :' + str(round(num_tran / time_, 2)) + " giao dịch/s")

# function to show the plot
plt.show()
