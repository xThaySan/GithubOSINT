import requests
from urllib.parse import urljoin


class GithubAPI:
  __BASE_URL = 'https://api.github.com'
  __INSTANCE = None
  
  @staticmethod
  def with_token() -> bool:
    return GithubAPI.__INSTANCE.with_token
  
  @staticmethod
  def token_is_valid() -> bool:
    return GithubAPI.__INSTANCE.token_is_valid 
  
  @staticmethod
  def init(token: str = None):
    GithubAPI.__INSTANCE = GithubAPI(token)
  
  def __init__(self, token: str = None):
    self.headers = {}
    self.with_token = False
    self.token_is_valid = False
    if token:
      self.with_token = True
      auth_headers = {'Authorization': f'Bearer {token}'}
      if self.__get('/user', headers=auth_headers) is not None:
        self.token_is_valid = True
        self.headers.update(auth_headers)
  
  @staticmethod
  def get(path: str, headers: dict = {}) -> any:
    if GithubAPI.__INSTANCE is None:
      raise RuntimeError('Github API not initialized.')
    return GithubAPI.__INSTANCE.__get(path, headers)

  @staticmethod
  def get_all(path: str, headers: dict = {}) -> any:
    data = []
    page = 1
    per_page = 100
    while True:
      page_path = path + f'?per_page={per_page}&page={page}'
      new_data = GithubAPI.get(page_path, headers)
      if new_data is None:
        raise Exception(f'Fetch failed on {page_path}')
      if type(new_data) is not list:
        raise Exception(f'Fetched data type of {type(new_data).__name__}, expected list')
      data.extend(new_data)
      if len(new_data) != per_page:
        break
      page += 1
    return data
  
  def __get(self, path: str, headers: dict = {}) -> any:
    _headers = {**self.headers, **headers}
    response = requests.get(urljoin(GithubAPI.__BASE_URL, path), headers=_headers)
    if response.status_code != 200:
      return None
    return response.json()
