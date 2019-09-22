import multiprocessing as mp
import psutil
import os


def fork():
    procs = list()
    cpus = psutil.cpu_count()
    for cpu in range(cpus):
        affinity = [cpu]
        d = dict(affinity=affinity)
        p = mp.Process(target=runChild, kwargs=d)
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
        print('joined')

def runChild(affinity):
    proc = psutil.Process()
    print('PID: {pid}'.format(pid=proc.pid))
    proc.cpu_affinity(affinity)


def simpleFork(cpu_limit = 1):
    pids = []
    for _ in range(1, cpu_limit):
        pid = os.fork()
        if pid == 0:
            break
        pids.append(pid)

    return pids