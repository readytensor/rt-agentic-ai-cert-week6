"""
Stdio wrapper for the MCP Entity Extraction Server
This version uses stdio transport for Claude Desktop compatibility.
"""

import asyncio
from typing import List
from mcp.server import FastMCP
import logging

# Import the actual extraction functions
from tools import (
    extract_entities_llm,
    extract_entities_spacy,
    extract_entities_gazetteer,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp = FastMCP("entity-extraction")


@mcp.tool()
async def extract_entities_llm_mcp(text: str, entity_types: List[str]) -> str:
    return extract_entities_llm(text, entity_types)


@mcp.tool()
async def extract_entities_spacy_mcp(text: str) -> str:
    return extract_entities_spacy(text)


@mcp.tool()
async def extract_entities_gazetteer_mcp(text: str) -> str:
    return extract_entities_gazetteer(text)


if __name__ == "__main__":
    asyncio.run(mcp.run("stdio"))
