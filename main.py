from tgtg import TgtgClient, TgtgAPIError, TgtgLoginError, TgtgPollingError
import asyncio 
import hashlib
import json
import os
from user_data import UserData, Offer
from constants import CREDENTIALS_FNAME, USERS, OFFERS_HASH_FNAME, TELEGRAM_TOKEN
from urllib.parse import quote

from constants import TELEGRAM_TOKEN
from telegram import Bot

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
        offer = Offer(item['item']['item_id'], item['display_name'], item['items_available'])
        offers.append(offer)
  return offers

def user_has_newer_offers(offers: list, user: UserData):
  has_offers=False
  for offer in offers:
    hash_offer = str(hashlib.md5(offer.description.encode()).hexdigest())
    hash_fname = OFFERS_HASH_FNAME % (user.email, hash_offer)
    if os.path.isfile(hash_fname):
      with open(hash_fname, 'r') as f:
        old_hash_offers = json.load(f)
    else:
      old_hash_offers = ''
    if old_hash_offers != hash_offer:
      with open(hash_fname, 'w') as f:
        f.write(json.dumps(hash_offer))
        offer.is_new=True
      has_offers=True
  return has_offers

async def main():
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
          for offer in offers:
            if offer.is_new:
              msg=offer.description
              print(offer.description)
              bot = Bot(TELEGRAM_TOKEN)
              await bot.send_message(chat_id=user.chat_id, text=msg)
      except TgtgAPIError as e:
        os.remove(credentials_fname)
      except TgtgLoginError as e:
        os.remove(credentials_fname)
      except TgtgPollingError as e:
        os.remove(credentials_fname)

if __name__ ==  '__main__':
    loop.run_until_complete(main())
