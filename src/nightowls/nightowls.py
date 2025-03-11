#!/bin/env python3

from collections import defaultdict
from collections.abc import Iterator
import argparse as ap
from tempfile import TemporaryDirectory
from typing import TextIO
import git
import matplotlib.pyplot as plt
import sys
import validators
import numpy as np


def member_name(author: git.Actor) -> str:
    return f'{author.name}'


def hour_members(commits: Iterator[git.Commit], ax: plt.Axes):
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

    ax.set_xlabel('Heure de la journée')
    ax.set_ylabel('Nombre de commits')


def member_hours(commits: Iterator[git.Commit], ax: plt.Axes):
    """ X ticks per members and bars per hour """
    results: defaultdict[int, defaultdict[str, int]] = defaultdict(lambda: defaultdict(lambda: 0))
    for c in commits:
        results[c.authored_datetime.hour][member_name(c.author)] += 1

    for hour, commit_counts in sorted(results.items(), key=lambda kv: sum(kv[1].values()), reverse=True):
        ax.bar(commit_counts.keys(), commit_counts.values(), width=1, label=hour)
        # ax.set_xticks(authors)


def run(repo: git.Repo):
    fig, ax = plt.subplots(figsize=(10, 5))

    hour_members(repo.iter_commits(), ax)

    ax.legend()
    assert isinstance(sys.stdout, TextIO)
    fig.savefig(sys.stdout)  # png


class CloneProgressPrinter(git.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
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
                run(git.Repo.clone_from(path, tmpdirname, progress=CloneProgressPrinter(), multi_options=['--bare']))
        else:
            run(git.Repo(path))
    except git.exc.InvalidGitRepositoryError as e:
        p.error(f'invalid git repostory: {e.args[0]}')
    except git.exc.NoSuchPathError as e:
        p.error(f'no such path: {e.args[0]}')
