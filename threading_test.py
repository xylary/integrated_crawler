import threading
import time
import random


jobs = ['1', '2', '3', '4', '5']


def test_job(id):
    print("Job {} start.".format(id))
    t = int(id)
    for i in range(100):
        t *= 2
        print('Job ' + id + ' result: ' + str(t))
        time.sleep(1)
    print("Job {} finish.".format(id))


def main():
    threads = []
    for i in range(len(jobs)):
        thread = threading.Thread(target=test_job, args=(jobs[i], ))  # 添加线程
        thread.start()
        threads.append(thread)

    for i in range(5):
        thread.join()

    print('All jobs done.')


if __name__ == "__main__":
    main()
