#!/bin/env python3

from collections import defaultdict, OrderedDict
from itertools import groupby
from operator import itemgetter
from subprocess import run
from typing import Iterator
import argparse as ap
import git
import matplotlib.pyplot as plt
import sys
import numpy as np

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('--repo', help='Path to the root git directory')

    args = parser.parse_args()

    try:
        repo = git.Repo(args.repo)
    except git.exc.InvalidGitRepositoryError as e:
        parser.error(f'invalid git repostory: {e.args[0]}')
    except git.exc.NoSuchPathError as e:
        parser.error(f'no such path: {e.args[0]}')

    author_to_member = {
        ('Scover', 'thediscover22450@gmail.com'): 'Raphaël',
        ('Soladoc', 'romaingrandchamppro@gmail.com'): 'Romain',
        ('marius', 'icelos@yahoo.com'): 'Marius',
        ('BakaTech', '101347606+Baka-Nekoz@users.noreply.github.com'): 'Maël',
        ('Xx-Nasank-xX', 'maelanpotier05@gmail.com'): 'Maëlan',
        ('Benjamin', 'benjamin.dumontgirard@gmail.com'): 'Benjamin',
        ('5cover', 'thediscover22450@gmail.com'): 'Raphaël',
        ('mariuschartier', 'icelos@yahoo.com'): 'Marius',
        ('Soladoc', '143883201+Soladoc@users.noreply.github.com'): 'Romain',
        ('Xx-Nasank-xX', '125129998+Xx-Nasank-xX@users.noreply.github.com'): 'Maëlan',
    }

    def member_name(author: git.Actor) -> str:
        return author_to_member.get((author.name, author.email), 'inconnu')

    fig, ax = plt.subplots(figsize=(10,5))

    def hour_members(commits: Iterator[git.Commit], ax: plt.Axes):
        """ X ticks per hour and bars per member """
        hours = np.arange(24)
        results: defaultdict[str, list[int]] = defaultdict(lambda: np.zeros(len(hours)))

        for c in commits:
            results[member_name(c.author)][c.authored_datetime.hour] += 1
       

        bottom = np.zeros(len(hours))
        for author, commit_counts in sorted(results.items(), key=lambda kv: sum(kv[1]), reverse=True):
            ax.bar(hours, commit_counts, width=1, label=author, bottom=bottom)
            ax.set_xticks(range(len(hours)))
            bottom += commit_counts

        ax.set_xlabel('Heure de la journée')
        ax.set_ylabel('Nombre de commits')

    def member_hours(commits: Iterator[git.Commit], ax: plt.Axes):
        """ X ticks per members and bars per hour """
        authors = tuple(set(author_to_member.values()))
        results: defaultdict[int, dict[str, int]] = defaultdict(lambda: {name: 0 for name in authors})
        for c in commits:
            results[c.authored_datetime.hour][member_name(c.author)] += 1
        #for hour, commit_counts in sorted(results.items(), key=lambda kv: sum(kv[1].values()), reverse=True):
        #    print(hour, authors, commit_counts.values())   
        #exit()

        bottom = np.zeros(len(authors))
        for hour, commit_counts in sorted(results.items(), key=lambda kv: sum(kv[1].values()), reverse=True):
            ax.bar(authors, commit_counts.values(), width=1, label=hour, bottom=bottom)
            #ax.set_xticks(authors)
            bottom += tuple(commit_counts.values())
        
    hour_members(repo.iter_commits(), ax)

    ax.legend()
    fig.savefig(sys.stdout)  # png
