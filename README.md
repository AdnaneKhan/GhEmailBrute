# GhEmailBrute
A tool to link any email with a GitHub account, even if the email is private.

## Use Cases

The best use case for this tool is to enumerate a set of GitHub accounts that are linked to an employer by running a large number of emails gathered via OSINT through the tool.

## Installation

The tool is a simple Python script. The only dependencies are `requests` and `beautifulsoup4`.

## How does it work?

GitHub exposes an API endpoint as part of the signup flow that determines if an email address is in use or not. If it is in use, the endpoint will return a status code of 422. If it is not, then it will return a status code of 200. This endpoint does not enforce any captcha or human detection requirement. It does enforce a rate limit, and this tool will sleep in order to re-try if it detects a response code of `429` (too many requests).

The second component is that commits made with an email address associated with an account will be linked to that account. GitHub has a feature to enable email privacy, _and_ a feature that blocks commits if they contain a user's email. This feature only works for that account, however. Another user can use that email to make a commit and it will not be blocked. GitHub will happily associate that "private" email with the account it is attached to. 

Both of these features are not considered security issues by GitHub. This POC along with details was sent to GitHub as a report and GitHub indicated that it was known behavior and that they have accepted the risk in favor of usability. Since it is a feature, this tool exists to leverages that feature.

## Execution

In order to execute the script, you must set `ENUM_TOKEN` to a GitHub personal access token with the `repo` and `delete_repo` scopes. This is necessary because the tool creates a temporary private repository in order to link email addresses to accounts. The repository is deleted after the enumeration process.

```
python3 ghemailbrute.py --emails emails.txt
```

The tool will print all detected links in the following format:

```
GITHUB_USERNAME:some_email@domain.com
```

If a link is not printed, then there is currently no GitHub account linked to that email address.

