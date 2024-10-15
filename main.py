from colorama import Fore
from rich.console import Console
import click
from core.api import GithubAPI
from core.models import Author
from core.utils import colorize, is_username, is_repo

console = Console(highlight=False)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument('to_explore')
@click.option('-t', '--token', prompt='Token (optionnal)', hide_input=True, prompt_required=False, help='Token of Github API (optionnal)')
@click.option('-f', '--fork', is_flag=True, show_default=True, default=False, help='Enable exploration for forked repositories')
def explore(to_explore: str, token: str, fork: bool) -> None:
  """Retrieves usernames and e-mails from repository main branch logs.

  TO_EXPLORE: Can be either the username (all public repositories are used) or the name of a specific repository 
  """
  
  GithubAPI.init(token=token)

  # github = Github(token=token)
  if GithubAPI.with_token() and not GithubAPI.token_is_valid():
    if  not click.confirm(colorize('/!\\ Token is not valid, continue without ?', Fore.RED), default=False):
      exit()
  
  authors: set[Author] = set()
  with console.status('Exploring repositories...', spinner="moon") as status:
    if is_username(to_explore):
      try:
        user = Author.create(to_explore, verify=True)
      except:
        console.print(f'❌ {colorize("User", Fore.WHITE)} {colorize(to_explore, Fore.RED)} {colorize("does not exist", Fore.WHITE)}')
        exit()
    elif is_repo(to_explore):
      try:
        user = Author.from_repository(to_explore)
      except:
        console.print(f'❌ {colorize("Repository", Fore.WHITE)} {colorize(to_explore, Fore.RED)} {colorize("not found", Fore.WHITE)}')
        exit()
    else:
      console.print(f'❌ {colorize("TO_EXPLORE must have the pattern", Fore.WHITE)} {colorize("<username>", Fore.RED)} or {colorize("<username>/<repository>", Fore.RED)}')
      exit()
    
    repos = user.repositories(with_fork=fork)
    repos_count = len(repos)
    console.print(f'✨ {colorize("Found", Fore.WHITE)} {colorize(str(repos_count), Fore.YELLOW)} {colorize("repositories", Fore.WHITE)}')
    for i, repo in enumerate(repos):
      for branche in repo.branches:
        status.update(f'({i+1}/{repos_count}) Exploring {repo.fullname} <{branche.name}>')
        for commit in branche.commits:
          authors.add(commit.author)
  
  authors = [user] + sorted([author for author in authors if author != user], key=lambda author: author.login)  
  result_printed = False
  for author in authors:
    if len(author.emails) + len(author.usernames) == 0:
      continue
    console.print('👤 ' + colorize(author.login, Fore.GREEN))
    
    if len(author.emails) > 0:
      console.print('  📨 ' + colorize('Emails:', Fore.YELLOW))
      for email in author.emails:
        console.print(f'    {email}')
        result_printed = True
    
    if len(author.usernames) > 0:
      console.print('  🪪 ' + colorize('Usernames:', Fore.YELLOW))
      for username in author.usernames:
        console.print(f'    {username}')
        result_printed = True
    
    console.print('')
  
  if result_printed is False:
    console.print(f'👀 {colorize("No relevant information found...", Fore.WHITE)}')


if __name__ == '__main__':
  explore()
