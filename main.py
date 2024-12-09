from tgtg import TgtgClient, TgtgAPIError, TgtgLoginError, TgtgPollingError
import asyncio 
import json
import os
from user_data import UserData, Offer, EMPTY_OFFER
from constants import CREDENTIALS_FNAME, USERS, OFFERS_HASH_FNAME, TELEGRAM_TOKEN
from urllib.parse import quote

from constants import TELEGRAM_TOKEN
from telegram import Bot

from common import file_remove, normalize_filename, get_credentials_fname

def get_offers(client: TgtgClient, user: UserData) -> list[Offer]:
  offers:list[Offer] = []
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

def read_offer_from_file(hash_fname):
    with open(hash_fname, 'r') as f:
      old_offer:Offer = EMPTY_OFFER.clone()
      json.load(f, object_hook = old_offer.fromJSON)
      return old_offer

def get_filename_by_user_and_offer(user:UserData, offer:Offer) -> str:
    return normalize_filename(OFFERS_HASH_FNAME % (user.email, offer.description))

def user_has_newer_offers(offers: list[Offer], user: UserData) -> bool:
  has_offers=False
  print(f'offers len: {len(offers)}')
  for offer in offers:
    # offer.availability = 0
    hash_fname = get_filename_by_user_and_offer(user, offer)
    if offer.availability > 0:
      print(f'offer: {offer.description} availability {offer.availability}')
      
      if os.path.isfile(hash_fname):
        old_offer = read_offer_from_file(hash_fname)
      else:
        old_offer:Offer = EMPTY_OFFER.clone()
      if old_offer.hash_offer != offer.hash_offer:
        # with open(hash_fname, 'w') as f:
        #   f.write(offer.toJSON())
        offer.is_new=True
        has_offers=True
  return has_offers

async def send_message(user, msg):
  bot = Bot(TELEGRAM_TOKEN)
  message = await bot.send_message(chat_id=user.user_telegram_id, text=msg)
  print(f'sending to user {user.email} message_id {message.message_id} msg {msg}')
  return message

async def delete_message(user, msg_id):
  bot = Bot(TELEGRAM_TOKEN)
  await bot.delete_message(chat_id=user.user_telegram_id, message_id=msg_id)
  print(f'delete to user {user.email} message_id {msg_id}')

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

async def delete_old_offer(offer: Offer, user: UserData):
  hash_fname = get_filename_by_user_and_offer(user, offer)
  if offer.availability == 0:
    if os.path.isfile(hash_fname):
      old_offer:Offer = read_offer_from_file(hash_fname=hash_fname)
      await delete_message(user, old_offer.msg_id)      
      file_remove(hash_fname)

def save_offer_with_user_and_message(offer: Offer, user: UserData, message):
  hash_fname = get_filename_by_user_and_offer(user, offer)
  if offer.availability > 0 and offer.is_new:
    print(f'offer: {offer.description} availability {offer.availability}')
    if os.path.isfile(hash_fname):
      old_offer:Offer = read_offer_from_file(hash_fname)
    else:
      old_offer:Offer = EMPTY_OFFER.clone()
    if old_offer.hash_offer != offer.hash_offer:
        offer.msg_id = message.message_id
        offer.is_new = False
        with open(hash_fname, 'w') as f:
          f.write(offer.toJSON())
  # else:
  #   old_offer = read_offer_from_file(hash_fname)
  #   delete_message(user, old_offer.msg_id)      
  #   file_remove(hash_fname)

async def main():
  for user in USERS:
    client = await get_tgtg_client_by_user(user)
    if client != None:
      offers = get_offers(client=client, user=user)
      if user_has_newer_offers(offers=offers, user=user):
        for offer in offers:
          if offer.is_new:
            msg=f'{offer.description} - availability: {offer.availability}'
            print(offer.description)
            message = await send_message(user, msg)
            save_offer_with_user_and_message(offer, user, message)
      for offer in offers:
        await delete_old_offer(offer, user)
    else:
      print(f'user {user.email} not logged')

if __name__ ==  '__main__':
    asyncio.run(main())
