#!/usr/bin/env python3
"""
Import issues from CSV to GitHub Issues.
Usage:
  GITHUB_TOKEN=ghp_xxx python .github/issue-import/import_issues.py --repo owner/repo

CSV format expected: title,body,labels,assignees,milestone
labels: comma-separated labels
assignees: comma-separated GitHub usernames (optional)
milestone: milestone title (optional) - script will try to match existing milestones

This script uses only Python stdlib (urllib) and requires Python 3.8+.
"""

import os
import sys
import csv
import json
import time
import argparse
from urllib import request, parse, error

API_BASE = 'https://api.github.com'


def api_request(method, path, token, data=None, params=None):
    url = API_BASE + path
    if params:
        url += '?' + parse.urlencode(params)
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'musicverse-issue-import-script'
    }
    if token:
        headers['Authorization'] = f'token {token}'
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        body = None
    req = request.Request(url, data=body, headers=headers, method=method)
    try:
        with request.urlopen(req) as resp:
            raw = resp.read().decode('utf-8')
            if raw:
                return json.loads(raw)
            return None
    except error.HTTPError as e:
        try:
            msg = e.read().decode('utf-8')
            payload = json.loads(msg)
            print(f'HTTP {e.code} {e.reason}: {payload}', file=sys.stderr)
        except Exception:
            print(f'HTTP {e.code} {e.reason}', file=sys.stderr)
        return None
    except Exception as e:
        print('Request failed:', e, file=sys.stderr)
        return None


def find_milestone_number(owner_repo, token, milestone_title):
    if not milestone_title:
        return None
    owner, repo = owner_repo.split('/')
    # list milestones (all)
    path = f'/repos/{owner}/{repo}/milestones'
    page = 1
    while True:
        res = api_request('GET', path, token, params={'state': 'all', 'page': page, 'per_page': 100})
        if not res:
            break
        for m in res:
            if m.get('title') == milestone_title:
                return m.get('number')
        if len(res) < 100:
            break
        page += 1
    return None


def create_issue(owner_repo, token, title, body, labels=None, assignees=None, milestone=None):
    owner, repo = owner_repo.split('/')
    path = f'/repos/{owner}/{repo}/issues'
    payload = {'title': title}
    if body:
        payload['body'] = body
    if labels:
        # split and strip
        payload['labels'] = [l.strip() for l in labels.split(',') if l.strip()]
    if assignees:
        payload['assignees'] = [a.strip() for a in assignees.split(',') if a.strip()]
    if milestone:
        payload['milestone'] = milestone
    return api_request('POST', path, token, data=payload)


def main():
    parser = argparse.ArgumentParser(description='Import issues from CSV into GitHub repository')
    parser.add_argument('--repo', required=True, help='GitHub repo in owner/repo format')
    parser.add_argument('--csv', default='.github/issue-import/tasks_issues.csv', help='Path to CSV file')
    parser.add_argument('--dry-run', action='store_true', help='Do not create issues, just print what would be created')
    parser.add_argument('--sleep', type=float, default=0.5, help='Delay between API calls (seconds)')
    args = parser.parse_args()

    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        print('Error: GITHUB_TOKEN environment variable is required', file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.csv):
        print(f'CSV file not found: {args.csv}', file=sys.stderr)
        sys.exit(1)

    to_create = []
    with open(args.csv, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            title = row.get('title') or ''
            body = row.get('body') or ''
            labels = row.get('labels') or ''
            assignees = row.get('assignees') or ''
            milestone_name = row.get('milestone') or ''
            to_create.append((title.strip(), body.strip(), labels.strip(), assignees.strip(), milestone_name.strip()))

    print(f'Preparing to create {len(to_create)} issues in {args.repo}')

    for idx, (title, body, labels, assignees, milestone_name) in enumerate(to_create, start=1):
        print(f'[{idx}/{len(to_create)}] {title}')
        milestone_number = None
        if milestone_name:
            milestone_number = find_milestone_number(args.repo, token, milestone_name)
            if milestone_number is None:
                print(f'  Milestone "{milestone_name}" not found in repo; issue will be created without milestone')
        if args.dry_run:
            print('  DRY RUN: would create issue with', {'title': title, 'labels': labels, 'assignees': assignees, 'milestone': milestone_number})
        else:
            res = create_issue(args.repo, token, title, body, labels=labels, assignees=assignees, milestone=milestone_number)
            if res and res.get('number'):
                print(f'  Created issue #{res.get("number")}')
            else:
                print('  Failed to create issue; see errors above', file=sys.stderr)
            time.sleep(args.sleep)

    print('Done')

if __name__ == '__main__':
    main()
