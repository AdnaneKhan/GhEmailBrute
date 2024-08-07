#!/usr/bin/python3
import argparse
import time
import requests
import json
import os
import binascii
from bs4 import BeautifulSoup

TEST_PAT = f'Bearer {os.environ.get("ENUM_TOKEN")}'

def create_repo():
    """Create repository for testing.
    """

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": TEST_PAT
    }

    repo_name = binascii.b2a_hex(os.urandom(15)).decode()
    params = {
        "name": repo_name,
        "private": "true"
    }

    resp = requests.post(f'https://api.github.com/user/repos', json=params, headers=headers)

    if resp.status_code == 201:
        return repo_name

def get_user():
    """Get auth user.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": TEST_PAT
    }

    resp = requests.get(f'https://api.github.com/user', headers = headers)

    return resp.json()['login']

def push_email_commits(emails, repo_name):
    """Push commits, 1 dummy file per email.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": TEST_PAT
    }

    for email in emails:
        rand_file = binascii.b2a_hex(os.urandom(15)).decode()
        params = {
            "committer": {"name":"TestUser", "email": f"{email}"},
            "content": "SGF4b3I=",
            "message": "Test"
        }

        res = requests.put(f'https://api.github.com/repos/{repo_name}/contents/{rand_file}', json=params, headers=headers)

def delete_repo(test_repo):
    """Deletes repo after testing.
    """

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": TEST_PAT
    }

    resp = requests.delete(f'https://api.github.com/repos/{test_repo}', headers=headers)


def get_contribs(test_branch, test_repo):
    """Get contributors from test branch.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": TEST_PAT
    }

    time.sleep(10)
    commits = requests.get(f'https://api.github.com/repos/{test_repo}/commits?sha={test_branch}',headers=headers)
    list_commits = commits.json()

    for commit in list_commits:
        print(commit['author']['login']+":"+ commit['commit']['author']['email'])


def check_email(session, email, csrf_token):
    """Checks if the email is associated with a GitHub account or not.
    """
    params = {
        "authenticity_token": csrf_token,
        "value": email
    }
    res = session.post('https://github.com/email_validity_checks', data=params)

    return res.status_code

def establish_session():
    """Validate whether emails are currently used or not.
    """
    sess = requests.Session()

    page = sess.get('https://github.com/join')
    soup = BeautifulSoup(page.content, 'html.parser')

    auth_tok = soup.find_all('auto-check', {"src":"/email_validity_checks"})
    tok = auth_tok[0].find('input', {"type":"hidden"})

    csrf_token = tok.get('value')

    return sess, csrf_token


def get_email_status(email_list):
    """Gets status of an email.
    """

    session, csrf_token = establish_session()
    sanity = check_email(session, f"{binascii.b2a_hex(os.urandom(15)).decode()}@foobar.com", csrf_token)

    if sanity == 200:
        print('Sanity check email returned 200, email query endpoint is good.')
        for email in email_list:
            while True:
                checked = False
                while not checked:
                    code = check_email(session, email, csrf_token)
                    if code == 429:
                        print("Rate limited, sleeping!")
                        time.sleep(120)
                    else:
                        checked = True    
                if code == 422:
                    print(f"Email exists: {email}")
                    yield(email)
                    break
                else:
                    break
    else:
        print("Sanity check returned non-200, maybe the endpoint was updated!")

email_list = []

with open('email_list.txt', 'r') as infile:
    email_list = [line.rstrip() for line in infile]

emails = [email for email in get_email_status(email_list)]

if len (emails) == 0:
    exit(0)

repo_name = create_repo()
if repo_name:
    user = get_user()
    push_email_commits(emails, user + "/" + repo_name)
    get_contribs("main", user + "/" + repo_name)
    delete_repo(repo_name)
