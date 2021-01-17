import matplotlib.pyplot as plt
import test_dev.data as data_collection

max_batch_sizes = []
time_commit = []
num_tran = 0
time_ = 0
for data in data_collection.data:
    tran = data.get("num_transactions")
    time = data.get("commit_time")
    max_batch_size = data.get("max_batch_size")

    max_batch_sizes.append(max_batch_size)
    time_commit.append(time)
    num_tran += tran
    time_ += time

plt.plot(max_batch_sizes, time_commit,marker ='o', markersize = 12,)

# naming the x axis
plt.xlabel('Kích thước lô tối đa')
# naming the y axis
plt.ylabel('thời gian hoàn thành(s)')

# giving a title to my graph
# plt.title('Kích thước lô = ' + str(data_collection.data[0].get("max_batch_size")) +
#           '; giá trị trung bình :' + str(round(num_tran / time_, 2)) + " giao dịch/s")
plt.title('Gửi cố định 1000 giao dịch')

# function to show the plot
plt.show()
