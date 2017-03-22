import praw, time, sched, uuid, readline

scheduler = sched.scheduler(time.time, time.sleep)

EXIT = ['exit', 'e']
ENABLE = ['enable', 'en']
QUEUE_LIMIT = 1600
ADD_LENGTH = 9
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
    event_handler = scheduler.enterabs(future_time, 0, post, [event_key, subreddit, title, url])

    event_value = TimeEvent(event_handler, future_time, title, url, subreddit)
    print '[' + str(event_key) + '] ' + str(event_value)

    events_queue[event_key] = event_value

def cancel_event(event_key):
    if event_key not in events_queue:
        print 'Invalid ID supplied'
        return
    event = events_queue[event_key]
    scheduler.cancel(event.event_handler)

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
    elif c == 'time':
        print time.strftime('%m-%d-%Y %H:%M:%S')
    elif c == 'quit':
        exit(1)
    else:
        print 'Unknown command'

def user_mode():
    print time.asctime(time.localtime())
    while True:
        cmd = raw_input('> ').split()
        if len(cmd) > 0:
            c = cmd[0]
            if c in EXIT:
                exit(1)
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
                # month, day, year, hour, minute, title, url, subreddit
                if len(cmd) != ADD_LENGTH:
                    print 'Invalid number of arguments: month day year hour minute %title% url subreddit'
                    continue
                if len(events_queue) >= QUEUE_LIMIT:
                    print 'Not enough space for additional queues'
                    continue
                timestamp = cmd[1:6]
                (title, url) = parse_title_url(cmd[6:8])
                subreddit = cmd[8]
                queue(create_timestamp(timestamp), subreddit, title, url)
            elif c == 'delete':
                if len(cmd) < MIN_DELETE:
                    print 'Invalid number of arguments'
                    continue
                event_key = cmd[1]
                cancel_event(event_key)
                delete_event(event_key)
            # TODO let scheduler run in background, instead of blocking
            elif c == 'run':
                print 'Scheduler is running...'
                scheduler.run()
                print 'All scheduled events have been processed'
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
