from tgtg import TgtgClient, TgtgAPIError, TgtgLoginError, TgtgPollingError
import asyncio 
import pprint
import time
import hashlib
import json
import os
from user_data import UserData
from constants import CREDENTIALS_FNAME, USERS, OFFERS_HASH_FNAME

loop = asyncio.get_event_loop()

def get_offers(client: TgtgClient, user: UserData):
  offers = []
  if user.loggedin:
    items = client.get_items(
        # favorites_only=True,
        # latitude=user.lat,
        # longitude=user.lon,
        # radius=user.radius,
    )
    for item in items:
      if item['items_available'] > 0:
        offers.append(f"{item['display_name']} {item['items_available']}")
  return offers

def user_has_newer_offers(offers, user: UserData):
  hash_offers = ''
  for offer in offers:
    hash_offers += str(hashlib.md5(offer.encode()).hexdigest())
  hash_fname = OFFERS_HASH_FNAME % user.email
  if os.path.isfile(hash_fname):
    with open(hash_fname, 'r') as f:
      old_hash_offers = json.load(f)
  else:
    old_hash_offers = ''
  if old_hash_offers != hash_offers:
    with open(hash_fname, 'w') as f:
      f.write(json.dumps(hash_offers))
    return True
  return False

def main():
  for user in USERS:
    credentials_fname = CREDENTIALS_FNAME % user.email
    if os.path.isfile(credentials_fname):
      with open(credentials_fname, 'r') as f:
        credentials = json.load(f)
      try:
        client = TgtgClient(access_token=credentials['access_token'], refresh_token=credentials['refresh_token'], user_id=credentials['user_id'], cookie=credentials['cookie'])
        client.login()
        user.loggedin=True
        offers = get_offers(client=client, user=user)
        if user_has_newer_offers(offers=offers, user=user):
          print(offers)
      except TgtgAPIError as e:
        os.remove(credentials_fname)
      except TgtgLoginError as e:
        os.remove(credentials_fname)
      except TgtgPollingError as e:
        os.remove(credentials_fname)

    # print(items)

if __name__ ==  '__main__':
    # loop.run_until_complete(main())
    main()
