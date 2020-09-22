import sys
import random

sys.path.insert(0, '/opt/eva/lib')

from eva.client.apiclient import APIClientLocal

api = APIClientLocal('uc')
code, result = api.call('test')
assert code == 0

code, result = api.call('login', dict(u='test', p='123'))
assert code == 0

token = result['token']

api.set_key(token)

email = f'some{random.randint(1, 100000)}@domain'

code, result = api.call('x_userinfo_set_field', dict(n='email', v=email))
assert code == 0

code, result = api.call('x_userinfo_get_field', dict(n='email'))
assert code == 0

assert result['email'] == email

print('OK')
