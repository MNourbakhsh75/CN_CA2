import json

with open('config.json') as json_file:
    data = json.load(json_file)

PORT = data['port']
MAXCON = 2
# users = []
logging_enable = data['logging']['enable']
logging_logFile = data['logging']['logFile']
caching_enable = data['caching']['enable']
caching_size = data['caching']['size']
privacy_enable = data['privacy']['enable']
privacy_userAgent = data['privacy']['userAgent']
restriction_enable = data['restriction']['enable']
restriction_targets = data['restriction']['targets']
accounting_users = data['accounting']['users']
HTTPInjection_enable = data['HTTPInjection']['enable']
HTTPInjection_body = data['HTTPInjection']['post']['body']

# for u in accounting_users:
#     users.append(u) //80000000
