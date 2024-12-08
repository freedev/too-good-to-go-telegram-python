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

from common import file_remove, normalize_filename, get_credentials_fname

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
      offer = Offer(item['item']['item_id'], item['display_name'], item['items_available'])
      offers.append(offer)
  return offers

def user_has_newer_offers(offers: list, user: UserData):
  has_offers=False
  print(f'offers len: {len(offers)}')
  for offer in offers:
    hash_fname = normalize_filename(OFFERS_HASH_FNAME % (user.email, offer.description))
    if offer.availability > 0:
      print(f'offer: {offer.description} availability {offer.availability}')
      hash_offer = str(hashlib.md5(offer.description.encode()).hexdigest())
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
    else:
      file_remove(hash_fname)
  return has_offers

async def send_message(user, msg):
  bot = Bot(TELEGRAM_TOKEN)
  message = await bot.send_message(chat_id=user.user_telegram_id, text=msg)
  print(f'sending to user {user.email} message_id {message.message_id} msg {msg}')

async def get_tgtg_client_by_user(user):
  credentials_fname = get_credentials_fname(user)
  if os.path.isfile(credentials_fname):
    with open(credentials_fname, 'r') as f:
      print(f'opened file {credentials_fname}')
      credentials = json.load(f)
    try:
      client = TgtgClient(access_token=credentials['access_token'], refresh_token=credentials['refresh_token'], cookie=credentials['cookie'])
      client.login()
      user.loggedin=True
      return client
    except TgtgAPIError as e:
      file_remove(credentials_fname)
      await send_message(user, f'user {user.email} TgtgAPIError')
    except TgtgLoginError as e:
      file_remove(credentials_fname)
      await send_message(user, f'user {user.email} TgtgLoginError')
    except TgtgPollingError as e:
      file_remove(credentials_fname)
      await send_message(user, f'user {user.email} TgtgPollingError')
  else:
    print(f'file {credentials_fname} not found')
  return None

async def main():
  for user in USERS:
    client = await get_tgtg_client_by_user(user)
    if client != None:
      offers = get_offers(client=client, user=user)
      if user_has_newer_offers(offers=offers, user=user):
        for offer in offers:
          if offer.is_new:
            msg=offer.description
            print(offer.description)
            await send_message(user, msg)
    else:
      print(f'user {user.email} not logged')

if __name__ ==  '__main__':
    asyncio.run(main())
