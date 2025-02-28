from tgtg import TgtgClient, TgtgAPIError, TgtgLoginError, TgtgPollingError
import asyncio 
import json
import os
import datetime
from user_data import UserData, Offer, EMPTY_OFFER
from constants import USERS, OFFERS_HASH_FNAME, TELEGRAM_TOKEN
from get_credentials import save_credentials_from_client

from constants import TELEGRAM_TOKEN, TEMP_DIR
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
    filename = normalize_filename(OFFERS_HASH_FNAME % (user.email, offer.description, offer.availability))
    return os.path.join(TEMP_DIR, filename)

def user_has_newer_offers(offers: list[Offer], user: UserData) -> bool:
  has_new_offers=False
  for offer in offers:
    # offer.availability = 0
    hash_fname = get_filename_by_user_and_offer(user, offer)
    if offer.availability > 0:      
      if os.path.isfile(hash_fname):
        old_offer = read_offer_from_file(hash_fname)
      else:
        old_offer:Offer = EMPTY_OFFER.clone()
      if old_offer.hash_offer != offer.hash_offer:
        # with open(hash_fname, 'w') as f:
        #   f.write(offer.toJSON())
        offer.is_new=True
        has_new_offers=True
  print(f'offers len: {len(offers)} has_new_offers: {has_new_offers}')
  return has_new_offers

async def send_message(user, msg):
  bot = Bot(TELEGRAM_TOKEN)
  message = await bot.send_message(chat_id=user.user_telegram_id, text=msg)
  print(f'sending to user {user.email} message_id {message.message_id} msg {msg}')
  return message

async def delete_message(user, msg_id):
  bot = Bot(TELEGRAM_TOKEN)
  try:
    await bot.delete_message(chat_id=user.user_telegram_id, message_id=msg_id)
    print(f'delete to user {user.email} message_id {msg_id}')
  except:
    print(f'unable to delete the message')

async def get_tgtg_client_by_user(user):
  credentials_fname = get_credentials_fname(user)
  if os.path.isfile(credentials_fname):
    last_modify_time = datetime.datetime.fromtimestamp(os.path.getmtime(credentials_fname))
    with open(credentials_fname, 'r') as f:
      print(f'opened file {credentials_fname}')
      credentials = json.load(f)
    try:
      client = TgtgClient(access_token=credentials['access_token'], refresh_token=credentials['refresh_token'], cookie=credentials['cookie'], last_time_token_refreshed=last_modify_time)
      if (datetime.datetime.now() - last_modify_time).seconds <= (3600 * 4):      
        client.login()
      else:
        save_credentials_from_client(client, credentials_fname)
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
  if os.path.isfile(hash_fname):
    old_offer:Offer = read_offer_from_file(hash_fname=hash_fname)
    await delete_message(user, old_offer.msg_id)      
    file_remove(hash_fname)

def save_offer_with_user_and_message(offer: Offer, user: UserData, message):
  hash_fname = get_filename_by_user_and_offer(user, offer)
  if offer.availability > 0 and offer.is_new:
    print(f'save offer: {offer.description} availability {offer.availability}')
    if os.path.isfile(hash_fname):
      old_offer:Offer = read_offer_from_file(hash_fname)
    else:
      old_offer:Offer = EMPTY_OFFER.clone()
    if old_offer.hash_offer != offer.hash_offer:
        offer.msg_id = message.message_id
        offer.is_new = False
        with open(hash_fname, 'w') as f:
          f.write(offer.toJSON())

def check_old_offer_not_online(old_offer:Offer, offers:list[Offer]):
  for offer in offers:
    if old_offer.hash_offer == offer.hash_offer:
      return False
  return True

async def remove_old_offer(user:UserData, offers:list[Offer]):
  # check if existing offer has availability == 0
  for offer in offers:
    if offer.availability == 0:
      await delete_old_offer(offer, user)
  # check if saved offer does not exist anymore
  prefixed = [filename for filename in os.listdir(TEMP_DIR) if filename.startswith("hash-")]
  for filename in prefixed:
    old_offer = read_offer_from_file(os.path.join(TEMP_DIR, filename))
    if check_old_offer_not_online(old_offer, offers):
      await delete_old_offer(old_offer, user)

async def main():
  for user in USERS:
    client = await get_tgtg_client_by_user(user)
    if client != None:
      offers = get_offers(client=client, user=user)
      if user_has_newer_offers(offers=offers, user=user):
        for offer in offers:
          if offer.is_new:
            msg=f'{offer.description} - availability: {offer.availability}'
            # print(offer.description)
            message = await send_message(user, msg)
            save_offer_with_user_and_message(offer, user, message)
      await remove_old_offer(user, offers)
    else:
      print(f'user {user.email} not logged')

if __name__ ==  '__main__':
    asyncio.run(main())
