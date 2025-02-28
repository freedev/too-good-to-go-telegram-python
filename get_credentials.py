from tgtg import TgtgClient
from constants import USERS
from common import get_credentials_fname
import asyncio
import json
import os

def save_credentials_from_client(client, credentials_fname):
    credentials = client.get_credentials()
    with open(credentials_fname, 'w') as f:
      f.write(json.dumps(credentials))

def get_credentials_from_user(user):
    credentials_fname = get_credentials_fname(user)
    if not os.path.isfile(credentials_fname):
      client = TgtgClient(email=user.email)
      save_credentials_from_client(client, credentials_fname)

async def main():
  for user in USERS:
    get_credentials_from_user(user)

if __name__ ==  '__main__':
    asyncio.run(main())