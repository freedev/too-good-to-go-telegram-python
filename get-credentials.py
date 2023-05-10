from tgtg import TgtgClient
from user_data import UserData
from constants import CREDENTIALS_FNAME, USERS
from common import get_credentials_fname
import asyncio
import json
import os

async def main():
  for user in USERS:
    credentials_fname = get_credentials_fname(user)
    if not os.path.isfile(credentials_fname):
      client = TgtgClient(email=user.email)
      credentials = client.get_credentials()
      with open(credentials_fname, 'w') as f:
        f.write(json.dumps(credentials))

if __name__ ==  '__main__':
    asyncio.run(main())