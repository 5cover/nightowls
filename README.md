# NightOwls

A CLI tool for your Git repos that analyzes commit frequency per time of day.

## Example

## MVP

- Python
- Git only
- Pass repo directory (default current dir)
- Get all commits
- output json
- output bar graph (x axis: hour of day, y axis: commit count. Stacked bars per user)
- Time zones options
  - local: keep local timezone (consider the user's local time zone)
  - utc: convert all to utc

## Roadmap

### Get list of commiters

Username + optional PFP

### Get list of commits in repository

Either all commits or commits in the specified timespan

### Get results
