#!/bin/env python3

from collections import defaultdict
from collections.abc import Iterator
from matplotlib.axes import Axes
from tempfile import TemporaryDirectory
import argparse as ap
import git
import matplotlib.pyplot as plt
import numpy as np
import sys
import validators


def member_name(author: git.Actor) -> str:
    return f'{author.name}'


def hour_members(commits: Iterator[git.Commit], ax: Axes):
    """ X ticks per hour and bars per member """
    hours = np.arange(24)
    results = defaultdict(lambda: np.zeros(len(hours)))

    for c in commits:
        results[member_name(c.author)][c.authored_datetime.hour] += 1

    bottom = np.zeros(len(hours))
    for member, commit_counts in sorted(results.items(), key=lambda kv: sum(kv[1]), reverse=True):
        ax.bar(hours, commit_counts, width=1, label=member, bottom=bottom)
        ax.set_xticks(range(len(hours)))
        bottom += commit_counts

    ax.set_xlabel('Time of day')
    ax.set_ylabel('Commit count')


def member_hours(commits: Iterator[git.Commit], ax: Axes):
    """ X ticks per members and bars per hour """
    results: defaultdict[int, defaultdict[str, int]] = defaultdict(lambda: defaultdict(lambda: 0))
    for c in commits:
        results[c.authored_datetime.hour][member_name(c.author)] += 1

    for hour, commit_counts in sorted(results.items(), key=lambda kv: sum(kv[1].values()), reverse=True):
        ax.bar(list(commit_counts.keys()), list(commit_counts.values()), width=1, label=hour)
        # ax.set_xticks(authors)


def run(repo: git.Repo):
    fig, ax = plt.subplots(figsize=(10, 5))

    hour_members(repo.iter_commits(), ax)

    ax.legend()
    fig.savefig(sys.stdout)  # png


def progress(op_code, cur_count, max_count=None, message=''):
    print(f'Cloning... {float(cur_count) / float(max_count or 100.0):.2%}',
          message or None,
          file=sys.stderr)


if __name__ == '__main__':
    p = ap.ArgumentParser()
    p.add_argument('path', help='Path to the Git directory. Can be an URL, in which case the repository is cloned to a temporary directory.')
    path = p.parse_args().path

    try:
        if validators.url(path):
            with TemporaryDirectory() as tmpdirname:
                run(git.Repo.clone_from(path, tmpdirname, progres=progress, multi_options=['--bare']))
        else:
            run(git.Repo(path))
    except git.InvalidGitRepositoryError as e:
        p.error(f'invalid git repostory: {e.args[0]}')
    except git.NoSuchPathError as e:
        p.error(f'no such path: {e.args[0]}')
