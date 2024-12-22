import click
import git
from pathlib import Path
import logging
from datetime import datetime
import sys
from fnmatch import fnmatch
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint
from rich.theme import Theme
from rich.table import Table
from rich.markdown import Markdown

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green",
})

console = Console(theme=custom_theme)

def setup_logging():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = Path.home() / f'git_update_{timestamp}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.FileHandler(log_file),
            RichHandler(console=console, rich_tracebacks=True)
        ]
    )
    return log_file

def update_repository(repo_path, progress, aggressive=False):
    try:
        repo = git.Repo(repo_path)

        if repo.is_dirty():
            progress.print(f"[yellow]⚠️  Uncommitted changes in {repo_path}, skipping...[/]")
            return False

        default_branch = repo.active_branch
        origin = repo.remotes.origin

        progress.print(f"[blue]📡 Fetching updates for {repo_path}[/]")
        origin.fetch()

        commits_behind = list(repo.iter_commits(f'{default_branch}..origin/{default_branch}'))
        if commits_behind:
            progress.print(f"[yellow]⏳ Repository is behind by {len(commits_behind)} commits[/]")

            if aggressive:
                progress.print("[yellow]🔄 Using aggressive mode (reset + rebase)[/]")
                repo.git.reset('--hard', f'origin/{default_branch}')
                repo.git.pull('--rebase')
            else:
                progress.print("[green]🛡️  Using safe mode (simple pull)[/]")
                origin.pull()

            progress.print(f"[green]✅ Successfully updated {repo_path}[/]")
        else:
            progress.print(f"[green]✨ Repository is up to date[/]")

        return True
    except git.exc.InvalidGitRepositoryError:
        progress.print(f"[red]❌ {repo_path} is not a valid git repository[/]")
        return False
    except Exception as e:
        progress.print(f"[red]❌ Error processing {repo_path}: {str(e)}[/]")
        return False

class RichGroup(click.Group):
    def format_help(self, ctx, formatter):
        console.print(Panel.fit(
            "[bold blue]Git Repository Update Tool[/]\n",
            title="🔄 Overview",
            border_style="blue"
        ))

        console.print(Markdown("## Description"))
        console.print("Automatically update multiple git repositories in the specified directory.\n")

        console.print(Markdown("## Options"))
        table = Table(show_header=True, header_style="bold magenta", border_style="blue")
        table.add_column("Option", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Default", style="yellow")

        table.add_row("-d, --directory", "Directory containing git repositories", "~/git")
        table.add_row("-r, --recursive", "Recursively search for repositories", "True")
        table.add_row("-v, --verbose", "Increase output verbosity", "False")
        table.add_row("-e, --exclude", "Exclude patterns (e.g., 'temp-*')", "None")
        table.add_row("--aggressive/--safe", "Use aggressive (reset+rebase) or safe (pull) update", "safe")

        console.print(table)

        console.print(Markdown("\n## Examples"))
        examples = Panel(
            "\n".join([
                "[cyan]# Update all repos in safe mode (default)[/]",
                "[green]$ update_repos.py[/]",
                "",
                "[cyan]# Update repos in aggressive mode (reset + rebase)[/]",
                "[green]$ update_repos.py --aggressive[/]",
                "",
                "[cyan]# Update specific directory in safe mode[/]",
                "[green]$ update_repos.py -d /path/to/repos --safe[/]",
                "",
                "[cyan]# Exclude patterns with aggressive update[/]",
                "[green]$ update_repos.py -e 'temp-*' --aggressive[/]",
            ]),
            title="Usage Examples",
            border_style="blue"
        )
        console.print(examples)

@click.command(cls=RichGroup, context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--directory', '-d',
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              default=str(Path.home() / 'git'),
              help='Directory containing git repositories')
@click.option('--recursive/--no-recursive', '-r',
              default=True,
              help='Recursively search for git repositories')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Increase output verbosity')
@click.option('--exclude', '-e',
              multiple=True,
              help='Exclude repositories matching these patterns (e.g., "temp-*", "test/*")')
@click.option('--aggressive/--safe',
              default=False,
              help='Aggressive mode uses reset --hard and rebase, safe mode uses simple pull')
def update_repos(directory, recursive, verbose, exclude, aggressive):
    """🔄 Update all git repositories in the specified directory.

    Update Modes:
    --safe (default): Uses simple git pull, preserves local changes
    --aggressive: Uses hard reset and rebase, forces alignment with remote

    This tool helps you keep multiple git repositories up to date by:
    - Scanning for git repositories in the specified directory
    - Checking for and pulling updates
    - Handling errors and conflicts gracefully
    - Providing detailed logging
    """
    log_file = setup_logging()
    root_path = Path(directory)

    rprint(Panel.fit(
        f"[bold blue]Git Repository Update Tool[/]\n"
        f"[cyan]Directory:[/] {root_path}\n"
        f"[cyan]Recursive:[/] {'Yes' if recursive else 'No'}\n"
        f"[cyan]Exclude patterns:[/] {', '.join(exclude) if exclude else 'None'}"
    ))

    pattern = '**/.git' if recursive else '.git'
    git_dirs = list(root_path.glob(pattern))

    updated = failed = skipped = 0

    with Progress(
        "[progress.description]{task.description}",
        SpinnerColumn(),
        TextColumn("[blue]{task.fields[repo]}[/]"),
        console=console
    ) as progress:
        total_task = progress.add_task(
            "[cyan]Scanning repositories...",
            total=len(git_dirs)
        )

        for git_dir in git_dirs:
            repo_path = git_dir.parent
            relative_path = repo_path.relative_to(root_path)

            progress.update(
                total_task,
                advance=1,
                repo=str(relative_path)
            )

            if any(fnmatch(str(relative_path), pat) for pat in exclude):
                console.print(f"[yellow]⏭️  Skipping:[/] {repo_path}")
                skipped += 1
                continue

            with console.status(
                f"[blue]📂 Processing {repo_path}[/] ({'aggressive' if aggressive else 'safe'} mode)",
                spinner="dots"
            ):
                if update_repository(repo_path, console, aggressive):
                    updated += 1
                else:
                    failed += 1

    summary = Table.grid(padding=1)
    summary.add_row("[bold green]✅ Updated[/]", f"[green]{updated}[/]")
    summary.add_row("[bold red]❌ Failed[/]", f"[red]{failed}[/]")
    summary.add_row("[bold yellow]⏭️  Skipped[/]", f"[yellow]{skipped}[/]")

    console.print(Panel(
        summary,
        title="[bold]Summary",
        border_style="green"
    ))
    console.print(f"\n[blue]📝 Log file:[/] {log_file}")

if __name__ == '__main__':
    update_repos()
