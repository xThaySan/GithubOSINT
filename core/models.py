from .api import GithubAPI


class Repository:  
  def __init__(self, fullname: str):
    self.fullname = fullname
    self.__branches = None
  
  @property
  def branches(self) -> list['Branche']:
    if self.__branches is None:
      raw_branches = GithubAPI.get_all(f'/repos/{self.fullname}/branches')
      if raw_branches is not None:
        self.__branches = [Branche(raw, self) for raw in raw_branches]
    return self.__branches
  
  def __repr__(self):
    return f'Repository<{self.fullname}>'


class Branche:
  def __init__(self, raw: any, repository: Repository):
    self.name = raw['name']
    self.repository = repository
    self.__commits = None
  
  @property
  def commits(self) -> list['Commit']:
    if self.__commits is None:
      raw_commits = GithubAPI.get_all(f'/repos/{self.repository.fullname}/commits')
      if raw_commits is not None:
        self.__commits = [Commit(raw) for raw in raw_commits]
    return self.__commits
  
  def __repr__(self):
    return f'Branche<{self.name}>'


class Commit:  
  def __init__(self, raw: any):
    self.sha = raw['sha']
    
    login = raw['author']['login'] if type(raw['author']) is dict and 'login' in raw['author'] else '<Deleted_User>'
    emails = [str(raw['commit'][e]['email']) for e in ('author', 'committer')]
    emails = [email for email in emails if not any([email.endswith(d) for d in ('@github.com', '@users.noreply.github.com')])]
    usernames = [str(raw['commit'][e]['name']) for e in ('author', 'committer')]
    usernames = [name for name in usernames if name not in ('GitHub',)]
    self.author = Author.create(login=login, usernames=usernames, emails=emails)
  
  def __repr__(self):
    return f'Commit<{self.sha}>'


class Author:
  INSTANCES: dict[str, 'Author'] = {}
  
  @staticmethod
  def from_repository(fullname: str) -> 'Author':
    repo = GithubAPI.get(f'/repos/{fullname}')
    if repo is None:
        raise ValueError('Repo not found')
      
    author = Author.create(repo['owner']['login'])
    author.__repositories = [Repository(fullname)]
    return author
  
  @staticmethod
  def create(login: str = None, usernames: list = [], emails: list = [], verify=False) -> 'Author':
    if verify:
      user = GithubAPI.get(f'/users/{login}')
      if user is None:
        raise ValueError('User not found')
      
    if login not in Author.INSTANCES:
      Author.INSTANCES[login] = Author(login=login)
    Author.INSTANCES[login].usernames.update(usernames)
    Author.INSTANCES[login].emails.update(emails)
    return Author.INSTANCES[login]
  
  def __init__(self, login: str = None):
    self.login = login
    self.usernames = set()
    self.emails = set()
    self.__repositories = None
  
  def repositories(self, with_fork=False) -> list['Repository']:
    if self.__repositories is None:
      repos = GithubAPI.get_all(f'/users/{self.login}/repos')
      if repos is not None:
        self.__repositories = [Repository(repo['full_name']) for repo in repos if repo['fork'] is False or with_fork]
    return self.__repositories
  
  def __eq__(self, value):
    if isinstance(value, Author):
      return self.login == value.login
    return False
  
  def __hash__(self):
    return hash(self.login)
  
  def __repr__(self):
    return f'Author<{self.login}>'
