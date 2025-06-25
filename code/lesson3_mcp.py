"""
Stdio wrapper for the MCP Entity Extraction Server
This version uses stdio transport for Claude Desktop compatibility.
"""

import logging
import base64
import asyncio
from typing import Optional
from mcp.server import FastMCP
from github import Github


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp = FastMCP("repository-information")


@mcp.tool()
async def get_github_readme(repo_name: str, github_token: Optional[str] = None) -> str:
    """
    Fetch the README content from a GitHub repository using PyGithub.

    Args:
        repo_name (str): The repository name in format 'owner/repo'
        github_token (str, optional): GitHub personal access token for authentication.
                                    If None, uses unauthenticated requests (rate limited)

    Returns:
        str: The README content as a string

    Raises:
        Exception: If the repository is not found or README doesn't exist
    """

    # Initialize GitHub client
    if github_token:
        g = Github(github_token)
    else:
        g = Github()

    # Get the repository
    repo = g.get_repo(repo_name)

    # Try to get README file (GitHub automatically detects README files)
    readme = repo.get_readme()

    # Decode the content from base64
    content = base64.b64decode(readme.content).decode("utf-8")

    return content


@mcp.tool()
async def get_github_owner_info(
    owner_name: str, github_token: Optional[str] = None
) -> str:
    """
    Fetch public information about a GitHub user or organization.

    Args:
        owner_name (str): The GitHub username or organization name
        github_token (str, optional): GitHub personal access token for authentication.
                                    If None, uses unauthenticated requests (rate limited)

    Returns:
        str: JSON string containing public owner information

    Raises:
        Exception: If the user/organization is not found
    """
    import json

    # Initialize GitHub client
    if github_token:
        g = Github(github_token)
    else:
        g = Github()

    try:
        # Try to get user first
        user = g.get_user(owner_name)

        # Collect public information
        owner_info = {
            "login": user.login,
            "name": user.name,
            "type": user.type,
            "bio": user.bio,
            "company": user.company,
            "location": user.location,
            "email": user.email,
            "followers": user.followers,
            "following": user.following,
        }

        return json.dumps(owner_info, indent=2)

    except Exception as e:
        raise Exception(f"Error fetching owner information: {str(e)}")


if __name__ == "__main__":
    asyncio.run(mcp.run("stdio"))
