"""Stack tracer for multi-threaded applications.

Usage:

import stacktracer
stacktracer.start_trace("trace.html",interval=5,auto=True) # Set auto flag to always update file!
....
stacktracer.stop_trace()
"""

import sys
import traceback
 

# Taken from http://bzimmer.ziclix.com/2008/12/17/python-thread-dumps/
# translated by http://outofmemory.cn/ 

def stacktraces():
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append('\n#ThreadID: %s' % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            mylinemsg=''
            if line:
                mylinemsg = '  %s' % (line.strip())
            code.append('   File: "%s", line %d, in %s, %s' % (filename, lineno, name, mylinemsg))
    mystr = '\n'.join(code)
    return "====Stack Trace====\n%s \n" % (mystr)

# This part was made by nagylzs
import os
import time
import threading

class TraceDumper(threading.Thread):
    """Dump stack traces into a given file periodically."""
    def __init__(self,fpath,interval,auto):
        """
        @param fpath: File path to output HTML (stack trace file)
        @param auto: Set flag (True) to update trace continuously.
            Clear flag (False) to update only if file not exists.
            (Then delete the file to force update.)
        @param interval: In seconds: how often to update the trace file.
        """
        assert(interval>0.1)
        self.auto = auto
        self.interval = interval
        self.fpath = os.path.abspath(fpath)
        self.stop_requested = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        while not self.stop_requested.isSet():
            time.sleep(self.interval)
            if self.auto or not os.path.isfile(self.fpath):
                self.stacktraces()

    def stop(self):
        self.stop_requested.set()
        self.join()
        try:
            if os.path.isfile(self.fpath):
                os.unlink(self.fpath)
        except:
            pass

    def stacktraces(self, mystr, threadlist):
        fout = file(self.fpath,"wb+")
        try:
            fout.write('====Thread List====\n%s\n\n' % threadlist)
            fout.write('====Thread Device====\n%s\n\n' % mystr)
            fout.write(stacktraces())
        finally:
            fout.close()

_tracer = None
def trace_start(fpath, mystr, threadlist, interval=5,auto=True):
    """Start tracing into the given file."""
    global _tracer

    _tracer = TraceDumper(fpath,interval,auto)
    #_tracer.setDaemon(True)"%s \n" % (code)
    _tracer.stacktraces(mystr, threadlist)



def trace_stop():
    """Stop tracing."""
    global _tracer
    if _tracer is None:
        raise Exception("Not tracing, cannot stop.")
    else:
        _tracer.stop()
        _tracer = None
        
if __name__ == '__main__':

    trace_start("trace.html", 'sf sdf\n sdf' ,'iiii\neeee')
