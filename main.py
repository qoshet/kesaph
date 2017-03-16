import praw, time, sched

scheduler = sched.scheduler(time.time, time.sleep)

EXIT = ['exit', 'e']
ENABLE = ['enable', 'en']
MIN_ADD = 9

def action(arg):
    print 'hello: ' + str(arg)

def post(subreddit, title, url):
    reddit = praw.Reddit()
    subreddit = reddit.subreddit(subreddit)
    try:
        subreddit.submit(title, url=url, send_replies=False)
    except praw.exceptions.APIException as err:
        # TODO add back to queue
        print err

def queue(future_time, subreddit, title, url):
    scheduler.enterabs(future_time, 0, post, [subreddit, title, url])

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
    print string
    quotes = string.split('#')
    return (quotes[1].strip(), quotes[2].strip())

def list_queue():
    for q in scheduler.queue:
        print q

def user_mode():
    while True:
        cmd = raw_input('> ').split()
        if len(cmd) > 0:
            c = cmd[0]
            if c in EXIT:
                exit(1)
            elif c in ENABLE:
                enable_mode()
            elif c == 'list':
                list_queue()
            elif c == 'time':
                print time.strftime('%m-%d-%Y %H:%M:%S')

def enable_mode():
    while True:
        cmd = raw_input('# ').split()
        if len(cmd) > 0:
            c = cmd[0]
            if c in EXIT:
                return
            if c == 'add':
                add_mode()

def add_mode():
    while True:
        cmd = raw_input('add# ').split()
        if len(cmd) > 0:
            c = cmd[0]
            if c in EXIT:
                return
            elif c == 'queue':
                # command, month, day, year, hour, minute, subreddit, title, url
                if len(cmd) < MIN_ADD:
                    print 'Invalid number of arguments'
                    continue
                timestamp = cmd[1:6]
                subreddit = cmd[6]
                (title, url) = parse_title_url(cmd[7:])
                queue(create_timestamp(timestamp), subreddit, title, url)
            # TODO let scheduler run in background, instead of blocking
            elif c == 'run':
                print 'Scheduler is running...'
                scheduler.run()
                print 'All scheduled events have been processed'

user_mode()
