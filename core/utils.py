from colorama import Style
from colorama.ansi import AnsiFore
import re


def colorize(s: str, color: AnsiFore):
  return f'{color + Style.BRIGHT}{s}{Style.RESET_ALL}'
  
  
def is_username(raw: str) -> bool:
  return re.match(r'^[a-zA-Z\d](?:[a-zA-Z\d]|-(?=[a-zA-Z\d])){0,38}$', raw) is not None


def is_repo(raw: str) -> bool:
  splitted = raw.split('/')
  if len(splitted) != 2:
    return False
  if not is_username(splitted[0]):
    return False
  return re.match(r'^[\w\.-]+$', splitted[1]) is not None
