# coding:utf-8

import Queue
import sys
import time
import threading
import inspect
import ctypes 
import config 
import logging 

logger = logging.getLogger("ops.threadpool") 

class SigleThread(threading.Thread):

    def __init__(self, tid, workQueue,resultQueue, timeout=600, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        
        # 线程在结束前等待任务队列多长时间
        self.tid = tid
        self.timeout = timeout
        self.setDaemon(True)
        self.workQueue = workQueue
        self.deviceid = ''
        self.runTask = False
        self.killstatus = False
        self.runtime = 0
        self.mutex = threading.Lock()
        self.killmutex = threading.Lock()

    def detecteTimeout(self):
        return (self.runtime > self.timeout)
             
    def increaseTime(self):
        with self.mutex:
            if (self.runTask == True):
                self.runtime = self.runtime + 1
                
    def resetInit(self):
        self.runTask = False
        self.deviceid = ''
        with self.mutex:
            self.runtime = 0
            
    def asyncRaise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise "invalid thread id"
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble, 
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise "PyThreadState_SetAsyncExc failed"
         
    def killRunning(self):
        with self.killmutex:
            if (self.killstatus != True):
                self.killstatus == True
            else:
                return 
        self.asyncRaise(self.ident, SystemExit)
        
    def run(self):
        
        while True:
            try:
                # get one work from Queue
                self.resetInit()
                with self.killmutex:
                    if (self.killstatus == True):
                        break;
                callablefun, self.deviceid = self.workQueue.get()
                #print 'Tid: %s run task : deviceid: %s' % (self.tid, self.deviceid)
                self.runTask = True
                res = callablefun()
                self.runTask = False
                
            except Queue.Empty:  # 任务队列空的时候结束此线程
                pass
                #print 'Work Queue is empty'
            except :
                n1 = sys.exc_info()
                logger.exception(n1[1]) 
                break
            finally:
                self.runTask = False
 
class ThreadPool:
    def __init__(self, num_of_threads=10):
        self.workQueue = Queue.Queue()
        self.resultQueue = Queue.Queue()
        self.threads = []
        self.__createThreadPool(num_of_threads)

    def __createThreadPool(self, num_of_threads):
        for i in range(num_of_threads):
            thread = self.createNewThread(i)
            self.threads.append(thread)
    
    def createNewThread(self, tid):
        thread = SigleThread(tid, self.workQueue, self.resultQueue)
        thread.start()
        return thread

    def keepAliveDaemon(self):
        breakthreads = []
        #dectect if thread is alive
        for mythread in self.threads:
            if not mythread.isAlive():
                breakthreads.append(mythread)
            else:
                mythread.increaseTime()
                
        # renew thread when it break
        for breakthread in breakthreads:
            if True:
                tid = breakthread.tid
                deviceid = breakthread.deviceid
                self.threads.remove(breakthread)
                newthread = self.createNewThread(tid)
                self.threads.append(newthread)
                logger.info ('Renew thread: tid =%s, deviceid =%s'% (tid, deviceid))
                
        # kill break task  
        for mythread in self.threads:
            if mythread.detecteTimeout() and mythread.isAlive():
                mythread.killRunning()
                
    def existTask(self, deviceid):
        for mythread in self.threads:
            if mythread.isAlive() and mythread.deviceid == deviceid:
                return True
        return False
    
    def listTask(self):
        aliveList = []
        for mythread in self.threads:
            if mythread.runTask == True:
                aliveList.append(mythread.deviceid)
        return aliveList
    
    def addJob(self, callablefun, deviceid):
        strDeviceId = str(deviceid)
        if (not self.existTask(strDeviceId)):
            self.workQueue.put((callablefun, strDeviceId))
        else:
            logger.info ('task %s alway running, escaped. '% (strDeviceId))

    
 
def test_job():
    html = ""
    waiti =2
    print 'do job ======' ,waiti

    time.sleep(waiti)
    return html

def test():
    print 'start testing'
    tp = ThreadPool(10)

    counti = 0
    while True:
        tp.keepAliveDaemon()
        time.sleep(1)
        if counti == 0 :
            for i in range(1, 18):
                tp.addJob(test_job, i)
        counti = counti+1
        if counti == 28 :
            for i in range(12, 20):
                tp.addJob(test_job, i)
        if  counti == 38 :
            for i in range(7, 90):
                tp.addJob(test_job, i)
        print '=run=%s, %s'%(counti,  tp.listTask())
    
    # 处理结果
    print 'result Queue\'s length==%d' % tp.resultQueue.qsize()
    while tp.resultQueue.qsize():
        print tp.resultQueue.get()
        
    print 'end testing'
    time.sleep(20)
    
if  __name__ == '__main__':
    test()
    
