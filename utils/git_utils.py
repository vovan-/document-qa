import requests
import random
import json

class GitHubPRCreator:
    def __init__(self, github_token, owner, repo, base_branch, new_branch, changes):
        self.github_token = github_token
        self.owner = owner
        self.repo = repo
        self.base_branch = base_branch
        self.new_branch = new_branch
        self.changes = changes
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_latest_sha(self, branch):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/ref/heads/{branch}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["object"]["sha"]

    def create_branch(self, latest_sha):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs"
        payload = {
            "ref": f"refs/heads/{self.new_branch}",
            "sha": latest_sha
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        print("Branch created:", self.new_branch)
        return response.json()["object"]["sha"]

    def update_and_commit_files(self, main_latest_sha):
        tree = []
        changes = self.changes["suggestedCodeChanges"]
        # print(changes)
        for update in changes:
            tree.append({"path": update["sourceFile"], "mode": "100644", "type": "blob", "content": update["sourceUpdate"]})

        branch_latest_sha = self.create_branch(main_latest_sha)

        commit_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/commits/{branch_latest_sha}"
        response = requests.get(commit_url, headers=self.headers)
        base_tree_sha = response.json()["tree"]["sha"]

        tree_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees"
        tree_data = {
            "base_tree": base_tree_sha,
            "tree": tree
        }
        response = requests.post(tree_url, headers=self.headers, json=tree_data)
        new_tree_sha = response.json()["sha"]

        commit_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/commits"
        commit_data = {
            "message": "Update multiple files in one commit",
            "parents": [branch_latest_sha],
            "tree": new_tree_sha
        }

        response = requests.post(commit_url, headers=self.headers, json=commit_data)
        new_commit_sha = response.json()["sha"]

        update_ref_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/refs/heads/{self.new_branch}"
        ref_data = {
            "sha": new_commit_sha
        }
        response = requests.patch(update_ref_url, headers=self.headers, json=ref_data)

        if response.status_code == 200:
            print("Successfully committed multiple files.")
        else:
            print("Failed to update reference:", response.json())

    def create_draft_pr(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls"
        payload = {
            "title": "Draft PR: Apply Git Diff Changes",
            "head": self.new_branch,
            "base": self.base_branch,
            "body": "This PR applies the suggested code changes based on git diff.\n\nSuggested Action: fix_code",
            "draft": True
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        pr_url = response.json()["html_url"]
        print("Draft PR created:", pr_url)
        return pr_url

    def create_pr_with_changes(self):
        try:
            main_latest_sha = self.get_latest_sha(self.base_branch)
            self.update_and_commit_files(main_latest_sha)
            result = self.create_draft_pr()
            return result
        except requests.exceptions.HTTPError as err:
            print(f"Error: {err}")


# Usage
# json_data = {
#     "issueLevel": "Spark_Job_or_ETL_script_issue",
#     "suggestedAction": "fix_code",
#     "suggestedCodeChanges": [
#         {
#             "sourceFile": "demo_project/demo_1_sql/preprocess.hql",
#             "gitDiff": "- create_at,\n+ created_at,",
#             "sourceUpdate": 'select\n  id,\n  name,\n  created_at,\n  picture_url,\n  owners,\n  users,\n  CURRENT_TIMESTAMP AS dp_create_timestamp,\n  CURRENT_TIMESTAMP AS dp_update_timestamp\nFROM\n  ${extractedData}'
#         }
#     ]
# }
#
# with open("../config.json", "r") as config_file:
#     config = json.load(config_file)
# GitHubPRCreator(config["github_token"], config["owner"], config["repo"], config["base_branch"], f"test-{random.randint(1, 100)}",
#                 json_data).create_pr_with_changes()
