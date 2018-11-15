

'''
Source: https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
Handles storing output into a queue for later reading
'''
def enqueue_output(pipeOut, queue):
    for line in iter(pipeOut.readline, b''):
        queue.put(line)
    pipeOut.close()
