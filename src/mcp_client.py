"""MCP client utilities for calling TODOIT and Playwright MCP functions directly"""

from typing import Optional, Dict, Any


def call_mcp_function(function_name: str, **kwargs) -> Dict[str, Any]:
    """Call an MCP function directly through Claude Code's environment
    
    This function should directly raise an error to inform the user that this
    implementation is designed to be run within Claude Code where MCP functions
    are available as globals.
    """
    
    raise RuntimeError(
        f"MCP function '{function_name}' cannot be called directly. "
        "This module is designed to work within Claude Code environment where "
        "MCP functions are available. Please run this through Claude Code CLI."
    )


class TodoitClient:
    """TODOIT MCP client wrapper"""
    
    async def todo_get_list_property(self, params: dict):
        """Get a property value for a list"""
        return await call_mcp_function("mcp__todoit__todo_get_list_property", params)
    
    async def todo_get_next_pending(self, params: dict):
        """Get next pending item from a list"""
        return await call_mcp_function("mcp__todoit__todo_get_next_pending", params)
    
    async def todo_get_item_property(self, params: dict):
        """Get a property value for an item"""
        return await call_mcp_function("mcp__todoit__todo_get_item_property", params)
    
    async def todo_update_item_status(self, params: dict):
        """Update item status"""
        return await call_mcp_function("mcp__todoit__todo_update_item_status", params)


class PlaywrightClient:
    """Playwright MCP client wrapper"""
    
    async def browser_navigate(self, params: dict):
        """Navigate to a URL"""
        return await call_mcp_function("mcp__playwright-headless__browser_navigate", params)
    
    async def browser_snapshot(self):
        """Take a page snapshot"""
        return await call_mcp_function("mcp__playwright-headless__browser_snapshot")
    
    async def browser_wait_for(self, params: dict):
        """Wait for time or condition"""
        return await call_mcp_function("mcp__playwright-headless__browser_wait_for", params)
    
    async def browser_click(self, params: dict):
        """Click an element"""
        return await call_mcp_function("mcp__playwright-headless__browser_click", params)
    
    async def browser_close(self):
        """Close the browser"""
        return await call_mcp_function("mcp__playwright-headless__browser_close")


def get_todoit_client() -> Optional[TodoitClient]:
    """Get a TODOIT MCP client instance"""
    try:
        return TodoitClient()
    except Exception as e:
        print(f"Error connecting to TODOIT MCP server: {e}")
        return None


def get_playwright_client() -> Optional[PlaywrightClient]:
    """Get a Playwright MCP client instance"""
    try:
        return PlaywrightClient()
    except Exception as e:
        print(f"Error connecting to Playwright MCP server: {e}")
        return None