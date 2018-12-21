from slacker import Slacker

slack = Slacker('xoxb-507380538243-507421535427-Zh8gEdFP575b8JnEHyNCa1xF')

# Send a message to #general channel
slack.chat.post_message('#general', 'Hello fellow slackers!')

# Get users list
response = slack.users.list()
users = response.body['members']

# Upload a file
slack.files.upload('hello.txt')

# If you need to proxy the requests
proxy_endpoint = 'http://myproxy:3128'
slack = Slacker('xoxb-507380538243-507421535427-Zh8gEdFP575b8JnEHyNCa1xF',
                http_proxy=proxy_endpoint,
                https_proxy=proxy_endpoint)

# Advanced: Use `request.Session` for connection pooling (reuse)
from requests.sessions import Session
with Session() as session:
    slack = Slacker(token, session=session)
    slack.chat.post_message('#general', 'All these requests')
    slack.chat.post_message('#general', 'go through')
    slack.chat.post_message('#general', 'a single https connection')