import json, copy
import hashlib

class UserData:
  def __init__(self, email, user_telegram_id, lat = None, lon = None, radius = None):
    self.loggedin = False
    self.email = email
    self.user_telegram_id = user_telegram_id
    self.lat = lat
    self.lon = lon
    self.radius = radius

class Offer:
  def __init__(self, offer_id, description, availability, hash_offer = '', msg_id = ''):
    self.offer_id = offer_id
    self.description = description
    self.availability = availability
    self.is_new = False
    self.hash_offer = self.getHash()
    self.msg_id = msg_id
  def getHash(self) -> str:
    return str(hashlib.md5(self.description.encode()).hexdigest())
  def fromJSON(self, otherdict):
    self.__dict__.update(otherdict)
  def toJSON(self):
      return json.dumps(
          self,
          default=lambda o: o.__dict__, 
          sort_keys=True,
          indent=4)
  def clone(self):
    return copy.deepcopy(self)

EMPTY_OFFER = Offer(offer_id=None, description='', availability=None, hash_offer='')
