class UserData:
  def __init__(self, email, user_telegram_id, lat = None, lon = None, radius = None):
    self.loggedin = False
    self.email = email
    self.user_telegram_id = user_telegram_id
    self.lat = lat
    self.lon = lon
    self.radius = radius

class Offer:
  def __init__(self, offer_id, description, availability):
    self.offer_id = offer_id
    self.description = description
    self.availability = availability
    self.is_new = False