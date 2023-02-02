import os
from user_data import UserData
from constants import CREDENTIALS_FNAME, OFFERS_HASH_FNAME

def normalize_filename(fn):
    validchars = "-_.() "
    out = ""
    for c in fn:
      if str.isalpha(c) or str.isdigit(c) or (c in validchars):
        out += c
      else:
        out += str(ord(c))
    return out    

def file_remove(fn: str):
  filename = normalize_filename(fn)
  if os.path.exists(filename): 
    print(f'removing filename {filename}')
    os.remove(filename) 
  else:
    print(f'filename does not exist {filename}')

def get_credentials_fname(user: UserData):
    credentials_fname = CREDENTIALS_FNAME % user.email
