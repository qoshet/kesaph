import praw, time, uuid, readline, threading

EXIT = ['exit', 'e']
ENABLE = ['enable', 'en']
QUEUE_LIMIT = 1600
MIN_ADD = 9
MIN_DELETE = 2

events_queue = {};

def action(arg):
    print 'hello: ' + str(arg)

def post(event_key, subreddit, title, url):
    delete_event(event_key, notify=False) # delete event anyway since scheduler is cleared when failed
    reddit = praw.Reddit()
    subreddit = reddit.subreddit(subreddit)
    try:
        subreddit.submit(title, url=url, send_replies=False)
    except praw.exceptions.APIException as err:
        # TODO add back to queue
        print err

def generate_event_key():
    key = str(uuid.uuid4())[:2]
    while key in events_queue:
        key = str(uuid.uui4())[:2]
    return key

def queue(future_time, subreddit, title, url):
    event_key = generate_event_key()
    countdown = create_countdown(future_time)

    event_handler = threading.Timer(countdown, post, [event_key, subreddit, title, url])
    event_value = TimeEvent(event_handler, future_time, title, url, subreddit)
    events_queue[event_key] = event_value

    event_handler.start()
    print '[' + str(event_key) + '] ' + str(event_value)

def cancel_event(event_key):
    if event_key not in events_queue:
        print 'Invalid ID supplied'
        return
    event = events_queue[event_key]
    event.event_handler.cancel()

def delete_event(event_key, notify=True):
    if event_key not in events_queue:
        print 'Invalid ID supplied'
        return
    event = events_queue.pop(event_key)
    if notify:
        print 'Event %s removed' % event_key

def create_timestamp(commands):
    n = len(commands)
    if n != 5:
        print 'Invalid timestamp format'
        return

    string = ' '.join(commands)
    time_strp = time.strptime(string, '%m %d %Y %H %M')
    future_time = time.mktime(time_strp)
    return future_time

def create_countdown(timestamp):
    return timestamp - time.time()

def parse_title_url(cmds):
    string = ' '.join(cmds)
    quotes = string.split('%')
    return (quotes[1].strip(), quotes[2].strip())

def list_queue():
    if not events_queue:
        print 'Nothing scheduled'
    else:
        for q in events_queue:
            print '[' + str(q) + '] ' + str(events_queue[q])

def all_mode(c):
    if c == 'list':
        list_queue()
    elif c == 'threads':
        print threading.enumerate()
    elif c == 'time':
        print time.strftime('%m-%d-%Y %H:%M:%S')
    elif c == 'quit':
        exit()
    else:
        print 'Unknown command'

def user_mode():
    print time.asctime(time.localtime())
    while True:
        cmd = raw_input('> ').split()
        if len(cmd) > 0:
            c = cmd[0]
            if c in EXIT:
                exit()
            elif c in ENABLE:
                enable_mode()
            else:
                all_mode(c)

def enable_mode():
    while True:
        cmd = raw_input('# ').split()
        if len(cmd) > 0:
            c = cmd[0]
            if c in EXIT:
                return
            if c == 'add':
                add_mode()
            else:
                all_mode(c)

def add_mode():
    while True:
        cmd = raw_input('add# ').split()
        if len(cmd) > 0:
            c = cmd[0]
            if c in EXIT:
                return
            elif c == 'queue':
                # month, day, year, hour, minute, subreddit, title, url
                if len(cmd) < MIN_ADD:
                    print 'Invalid number of arguments: month day year hour minute subreddit %title% url'
                    continue
                if len(events_queue) >= QUEUE_LIMIT:
                    print 'Not enough space for additional queues'
                    continue
                timestamp = cmd[1:6]
                (title, url) = parse_title_url(cmd[7:])
                subreddit = cmd[6]
                queue(create_timestamp(timestamp), subreddit, title, url)
            elif c == 'delete':
                if len(cmd) < MIN_DELETE:
                    print 'Invalid number of arguments'
                    continue
                event_key = cmd[1]
                cancel_event(event_key)
                delete_event(event_key)
            else:
                all_mode(c)

class TimeEvent:
    def __init__(self, event_handler, timedate, title, url, subreddit):
        self.event_handler = event_handler
        self.timedate = timedate
        self.title = title
        self.url = url
        self.subreddit = subreddit

    def __str__(self):
        return str(time.asctime(time.localtime(self.timedate))) + ': ' + str(self.title) + ' <' \
                + str(self.url) + '> r/' + str(self.subreddit)

user_mode()
