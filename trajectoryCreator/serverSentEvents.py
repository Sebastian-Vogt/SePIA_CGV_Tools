import queue

'''
Class to manage the server sent events
'''
class SSEManager:

    def __init__(self):
        self.listeners = []

    '''
    register method
    '''
    def listen(self):
        q = queue.Queue()
        self.listeners.append(q)
        return q

    '''
    notifies listeners
    '''
    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]

'''
formats the server sent events to f'event: ...\ndata:...\n\n'
'''
def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg