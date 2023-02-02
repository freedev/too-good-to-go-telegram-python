from tgtg import TgtgClient
from asyncio import get_event_loop
from user_data import UserData
from constants import CREDENTIALS_FNAME, USERS
from common import get_credentials_fname
import json
import os

loop = get_event_loop()

async def main():
  for user in USERS:
    credentials_fname = get_credentials_fname(user)
    if not os.path.isfile(credentials_fname):
      client = TgtgClient(email=user.email)
      credentials = client.get_credentials()
      with open(credentials_fname, 'w') as f:
        f.write(json.dumps(credentials))

if __name__ ==  '__main__':
    loop.run_until_complete(main())
