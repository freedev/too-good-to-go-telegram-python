class UserData:
  def __init__(self, email, chat_id, lat, lon, radius):
    self.loggedin = False
    self.email = email
    self.chat_id = chat_id
    self.lat = lat
    self.lon = lon
    self.radius = radius

class Offer:
  def __init__(self, offer_id, description, availability):
    self.offer_id = offer_id
    self.description = description
    self.availability = availability
    self.is_new = False