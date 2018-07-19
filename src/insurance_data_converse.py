'''
@author: xusheng
'''

from multiprocessing import Process, Queue
import os, time, random

class SourceObject(object):
    @property
    def insurance_name(self):
        return self._insurance_name
        
    @insurance_name.setter
    def insurance_name(self, value):
        self._insurance_name = value
    

class VProcess(Process):
    @property
    def should_be_stopped(self):
        return self._should_be_stopped
        
    @should_be_stopped.setter
    def should_be_stopped(self, value):
        self._should_be_stopped = value

    def __init__(self, name, queue):
        Process.__init__(self, name=name)
        self._queue = queue
        self._should_be_stopped = False

class QueueWriteProcess(VProcess):
    def run(self):
        print('Process [%s]: %s' % (self.name, os.getpid()))

        count = 0
        while not self.should_be_stopped:
            obj = SourceObject()
            obj.insurance_name = str(random.randint(0, 1000))
            print('Put %s to queue...' % obj.insurance_name)
            if count > 10:
                self.should_be_stopped = True
            
            count += 1
            self._queue.put(obj)
            time.sleep(random.random())

class QueueReadProcess(VProcess):
    def run(self):
        print('Process [%s]: %s' % (self.name, os.getpid()))
        while not self._queue.empty() or not self.should_be_stopped:
            print('%s or %s' % (not self._queue.empty(), not self.should_be_stopped))
            obj = self._queue.get(True)
            
            print('Get %s from queue...' % obj.insurance_name)
            time.sleep(2 * random.random())

class BatchProcessManager(object):
    def __init__(self):
        self._queue = Queue()
        self._writer = QueueWriteProcess('Writer', self._queue)
        self._reader = QueueReadProcess('Reader', self._queue)
        self._should_be_stopped = False
    
    def run(self):
        self._writer.start()
        self._reader.start()
    
        self._writer.join()
        print('==============')
        self._reader.should_be_stopped = True
        print('+++++++++++++++')
        self._reader.join()
        print('$$$$$$$$$$$$$$')
        
        
if __name__=='__main__':
    manager = BatchProcessManager()
    manager.run()