import os
import httpx
from git import Repo, InvalidGitRepositoryError, GitCommandError

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.git_schema import GitInput, GitOutput

class GitTool(BaseTool):
    """Executes Git and GitHub operations."""
    input_schema = GitInput
    output_schema = GitOutput

    def __init__(self):
        super().__init__(
            name="git_operation",
            description="Performs atomic Git operations and GitHub API calls (commit, push, create_pr, create_branch).",
            permission_level="ENTROPY_CHECKED"
        )

    async def execute(self, params: GitInput) -> GitOutput:
        try:
            repo = Repo(params.repo_path)
            
            if params.operation == "commit":
                # Atomic commit: stage all -> commit
                repo.git.add('.')
                commit = repo.index.commit(params.message)
                return GitOutput(success=True, commit_sha=commit.hexsha)

            elif params.operation == "push":
                origin = repo.remotes.origin
                info_list = origin.push()
                # Check for push errors
                for info in info_list:
                    if info.flags & info.ERROR:
                        return GitOutput(success=False, error_message=f"Push failed: {info.summary}")
                return GitOutput(success=True)

            elif params.operation == "create_branch":
                new_branch = repo.create_head(params.branch_name)
                repo.head.reference = new_branch
                repo.head.reset(index=True, working_tree=True)
                return GitOutput(success=True)

            elif params.operation == "create_pr":
                github_token = os.getenv("GITHUB_TOKEN")
                if not github_token:
                    return GitOutput(success=False, error_message="GITHUB_TOKEN environment variable is missing.")
                
                # Assume origin url is github and extract owner/repo
                origin_url = next(repo.remote().urls)
                # Naive parsing for simplicity
                parts = origin_url.replace('.git', '').split('/')
                owner_repo = f"{parts[-2]}/{parts[-1]}"
                
                api_url = f"https://api.github.com/repos/{owner_repo}/pulls"
                headers = {
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                payload = {
                    "title": params.message,
                    "head": params.branch_name,
                    "base": "main", # Default base branch
                    "body": params.message
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(api_url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    
                return GitOutput(success=True, url=data.get('html_url', ''))

            else:
                return GitOutput(success=False, error_message=f"Unknown operation: {params.operation}")
                
        except (InvalidGitRepositoryError, GitCommandError) as e:
            return GitOutput(success=False, error_message=f"Git Error: {str(e)}")
        except Exception as e:
            return GitOutput(success=False, error_message=f"Error: {str(e)}")
