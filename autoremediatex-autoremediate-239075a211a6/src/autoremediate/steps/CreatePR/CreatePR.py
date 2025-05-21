from patchwork.steps.CreatePR.CreatePR import CreatePR as PatchworkCreatePR
from atlassian import Bitbucket
from typing import Dict
import logging
import git
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth
from patchwork.step import Step, StepStatus
from git.exc import GitCommandError
from atlassian import Bitbucket

logger = logging.getLogger(__name__)

class CreatePR(PatchworkCreatePR):
    def __init__(self, inputs: dict):
        # Call the original Patchwork CreatePR constructor
        self.bitbucket_url = inputs.get("bitbucket_url", "https://api.bitbucket.org")
        self.bitbucket_key = inputs.get("bitbucket_key")
        self.bitbucket_user = inputs.get("bitbucket_user", "autoremediatex-admin")
        self.bitbucket = Bitbucket(
            url=self.bitbucket_url,
            username=self.bitbucket_user,
            password=self.bitbucket_key
        )
        super().__init__(inputs)


    def run(self) -> Dict:
        """
        Conditionally override PR creation if Bitbucket credentials are provided.
        """

        if not self.bitbucket_key:
            return super().run()
        import pdb; pdb.set_trace()
        logger.info(f"Creating Bitbucket PR from {self.base_branch} to {self.target_branch}")
        repo = git.Repo(Path.cwd(), search_parent_directories=True)
        is_push_success = self.__push(repo)
        if not is_push_success:
            self.set_status(
                StepStatus.FAILED,
                f"Failed to push to {self.original_remote_name}/{self.target_branch}. Skipping PR creation.",
            )
        logger.info(f"Creating PR from {self.base_branch} to {self.target_branch}")

        # Use the existing self.repo object in Patchwork
        original_remote_url = repo.remotes[self.original_remote_name].url
        repo_slug = self.get_slug_from_remote_url(original_remote_url).split("/")
        #
        # url = self._create_bitbucket_pr(
        #     repo_slug=repo_slug,
        #     title=self.title,
        #     body=self.pr_body,
        #     base_branch=self.target_branch,
        #     target_branch=self.base_branch
        # )
        #
        # logger.info(f"[green]Bitbucket PR created at [link={url}]{url}[/link][/]", extra={"markup": True})
        # return {"pr_url": url}

        source_project = repo_slug[0]
        source_repo = repo_slug[1]
        dest_project = repo_slug[0]
        dest_repo = repo_slug[1]
        feature_branch = self.target_branch
        main_branch = self.base_branch
        new_pr = self.bitbucket.open_pull_request(
            source_project=source_project,
            source_repo=source_repo,
            dest_project=dest_project,
            dest_repo=dest_repo,
            source_branch=feature_branch,
            destination_branch=main_branch,
            title=self.title,
            description=self.pr_body,
        )
        url = new_pr['links']['self'][0]['href']
        if new_pr:
            logger.info(f"[green]Bitbucket PR created at [link={url}]{url}[/link][/]", extra={"markup": True})
        else:
            logger.info("failed to create bitbucket pull request")
        return {"pr_url": url}



    def _create_bitbucket_pr(self, repo_slug: str, title: str, body: str, base_branch: str, target_branch: str) -> str:
        """
        Create a pull request on Bitbucket Cloud using direct HTTP requests.
        """
        workspace, repo = repo_slug.split('/')
        url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests"

        auth = HTTPBasicAuth(self.bitbucket_user, self.bitbucket_key)  # Use your Bitbucket username and App Password

        data = {
            "title": title,
            "description": body,
            "source": {
                "branch": {"name": base_branch}
            },
            "destination": {
                "branch": {"name": target_branch}
            },
            "close_source_branch": False
        }

        response = requests.post(url, json=data, auth=auth)

        if response.status_code != 201:
            raise RuntimeError(f"Failed to create Bitbucket PR: {response.status_code} - {response.text}")

        return response.json()["links"]["html"]["href"]

    @staticmethod
    def get_slug_from_remote_url(url: str) -> str:
        """
        Extract the 'workspace/repo' slug from a Bitbucket remote URL.
        """
        if url.startswith('git@'):
            return url.split(':', 1)[1].replace('.git', '')
        return url.split('bitbucket.org/')[1].replace('.git', '')
