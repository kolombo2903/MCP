#!/usr/bin/env python3
"""
WordPress MCP SSE Server for OpenAI and ChatGPT
Provides WordPress post management through Model Context Protocol over SSE
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server import Server
from mcp.types import Tool, TextContent
from sse_starlette.sse import EventSourceResponse

# ============================================================================
# CONFIGURATION - CHANGE THESE VALUES
# ============================================================================

WORDPRESS_URL = "https://your-wordpress-site.com/"  # Your WordPress site URL (with trailing slash)
WORDPRESS_USERNAME = "your-username"  # Your WordPress username
WORDPRESS_PASSWORD = "your-password"  # Your WordPress application password

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# WordPress MCP Client
# ============================================================================

class WordPressMCP:
    """WordPress MCP client for managing posts via REST API"""
    
    def __init__(self, url: str, username: str, password: str):
        """Initialize WordPress client with Basic Auth"""
        self.url = url.rstrip('/') + '/wp-json/wp/v2'
        self.client = httpx.AsyncClient(
            auth=(username, password),
            timeout=30.0,
            headers={'Content-Type': 'application/json'}
        )
        logger.info(f"WordPress MCP client initialized for {url}")
    
    async def create_post(
        self, 
        title: str, 
        content: str, 
        excerpt: str = "", 
        status: str = "publish"
    ) -> Dict[str, Any]:
        """
        Create a new WordPress post
        
        Args:
            title: Post title
            content: Post content (HTML)
            excerpt: Post excerpt
            status: Post status (publish, draft, private)
            
        Returns:
            Dict with success, post_id, url, message
        """
        try:
            logger.info(f"Creating post: {title}")
            
            data = {
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "status": status
            }
            
            response = await self.client.post(f"{self.url}/posts", json=data)
            response.raise_for_status()
            
            post = response.json()
            post_id = post.get('id')
            post_url = post.get('link')
            
            logger.info(f"Post created successfully: ID={post_id}, URL={post_url}")
            
            return {
                "success": True,
                "post_id": post_id,
                "url": post_url,
                "message": f"Post '{title}' created successfully!"
            }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error creating post: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "post_id": None,
                "url": None,
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Error creating post: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "post_id": None,
                "url": None,
                "message": error_msg
            }
    
    async def update_post(
        self,
        post_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        excerpt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing WordPress post
        
        Args:
            post_id: Post ID to update
            title: New title (optional)
            content: New content (optional)
            excerpt: New excerpt (optional)
            
        Returns:
            Dict with success, post_id, url, message
        """
        try:
            logger.info(f"Updating post ID: {post_id}")
            
            data = {}
            if title is not None:
                data["title"] = title
            if content is not None:
                data["content"] = content
            if excerpt is not None:
                data["excerpt"] = excerpt
            
            if not data:
                return {
                    "success": False,
                    "post_id": post_id,
                    "url": None,
                    "message": "No fields to update"
                }
            
            response = await self.client.post(f"{self.url}/posts/{post_id}", json=data)
            response.raise_for_status()
            
            post = response.json()
            post_url = post.get('link')
            
            logger.info(f"Post updated successfully: ID={post_id}, URL={post_url}")
            
            return {
                "success": True,
                "post_id": post_id,
                "url": post_url,
                "message": f"Post ID {post_id} updated successfully!"
            }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error updating post: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "post_id": post_id,
                "url": None,
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Error updating post: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "post_id": post_id,
                "url": None,
                "message": error_msg
            }
    
    async def get_posts(self, per_page: int = 10, page: int = 1) -> Dict[str, Any]:
        """
        Get list of WordPress posts
        
        Args:
            per_page: Number of posts per page (1-100)
            page: Page number
            
        Returns:
            Dict with success, posts, count, message
        """
        try:
            logger.info(f"Getting posts: per_page={per_page}, page={page}")
            
            params = {
                "per_page": min(max(per_page, 1), 100),
                "page": max(page, 1)
            }
            
            response = await self.client.get(f"{self.url}/posts", params=params)
            response.raise_for_status()
            
            posts = response.json()
            
            # Extract relevant post information
            post_list = [
                {
                    "id": post.get('id'),
                    "title": post.get('title', {}).get('rendered', ''),
                    "excerpt": post.get('excerpt', {}).get('rendered', ''),
                    "url": post.get('link'),
                    "status": post.get('status'),
                    "date": post.get('date')
                }
                for post in posts
            ]
            
            logger.info(f"Retrieved {len(post_list)} posts")
            
            return {
                "success": True,
                "posts": post_list,
                "count": len(post_list),
                "message": f"Retrieved {len(post_list)} posts"
            }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error getting posts: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "posts": [],
                "count": 0,
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Error getting posts: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "posts": [],
                "count": 0,
                "message": error_msg
            }
    
    async def delete_post(self, post_id: int) -> Dict[str, Any]:
        """
        Delete a WordPress post
        
        Args:
            post_id: Post ID to delete
            
        Returns:
            Dict with success, post_id, message
        """
        try:
            logger.info(f"Deleting post ID: {post_id}")
            
            response = await self.client.delete(f"{self.url}/posts/{post_id}")
            response.raise_for_status()
            
            logger.info(f"Post deleted successfully: ID={post_id}")
            
            return {
                "success": True,
                "post_id": post_id,
                "message": f"Post ID {post_id} deleted successfully!"
            }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error deleting post: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "post_id": post_id,
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Error deleting post: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "post_id": post_id,
                "message": error_msg
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        logger.info("WordPress MCP client closed")

# ============================================================================
# MCP Server Setup
# ============================================================================

# Global WordPress client instance
wp_client: Optional[WordPressMCP] = None

# Create MCP server
mcp_server = Server("wordpress-mcp-server")

@mcp_server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools"""
    return [
        Tool(
            name="create_post",
            description="Create a new WordPress post on your site",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Post title"
                    },
                    "content": {
                        "type": "string",
                        "description": "Post content in HTML"
                    },
                    "excerpt": {
                        "type": "string",
                        "description": "Post excerpt (optional)",
                        "default": ""
                    },
                    "status": {
                        "type": "string",
                        "enum": ["publish", "draft", "private"],
                        "description": "Post status",
                        "default": "publish"
                    }
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="update_post",
            description="Update an existing WordPress post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "integer",
                        "description": "Post ID to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New post title (optional)"
                    },
                    "content": {
                        "type": "string",
                        "description": "New post content in HTML (optional)"
                    },
                    "excerpt": {
                        "type": "string",
                        "description": "New post excerpt (optional)"
                    }
                },
                "required": ["post_id"]
            }
        ),
        Tool(
            name="get_posts",
            description="Get list of WordPress posts",
            inputSchema={
                "type": "object",
                "properties": {
                    "per_page": {
                        "type": "integer",
                        "description": "Number of posts per page (1-100)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number",
                        "default": 1,
                        "minimum": 1
                    }
                }
            }
        ),
        Tool(
            name="delete_post",
            description="Delete a WordPress post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {
                        "type": "integer",
                        "description": "Post ID to delete"
                    }
                },
                "required": ["post_id"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle MCP tool calls"""
    global wp_client
    
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    if wp_client is None:
        error_result = {
            "success": False,
            "message": "WordPress client not initialized"
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    try:
        if name == "create_post":
            result = await wp_client.create_post(
                title=arguments["title"],
                content=arguments["content"],
                excerpt=arguments.get("excerpt", ""),
                status=arguments.get("status", "publish")
            )
        elif name == "update_post":
            result = await wp_client.update_post(
                post_id=arguments["post_id"],
                title=arguments.get("title"),
                content=arguments.get("content"),
                excerpt=arguments.get("excerpt")
            )
        elif name == "get_posts":
            result = await wp_client.get_posts(
                per_page=arguments.get("per_page", 10),
                page=arguments.get("page", 1)
            )
        elif name == "delete_post":
            result = await wp_client.delete_post(
                post_id=arguments["post_id"]
            )
        else:
            result = {
                "success": False,
                "message": f"Unknown tool: {name}"
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"Error executing tool: {str(e)}"
        }
        logger.error(f"Tool execution error: {e}")
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global wp_client
    
    # Startup
    logger.info("Starting WordPress MCP SSE Server...")
    wp_client = WordPressMCP(WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD)
    logger.info("WordPress client initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down WordPress MCP SSE Server...")
    if wp_client:
        await wp_client.close()

# Create FastAPI app
app = FastAPI(
    title="WordPress MCP SSE Server",
    description="MCP server for WordPress post management via ChatGPT",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Server information endpoint"""
    tools = await list_tools()
    
    return {
        "name": "WordPress MCP SSE Server",
        "version": "1.0.0",
        "protocol": "MCP over SSE",
        "description": "Manage WordPress posts through ChatGPT using Model Context Protocol",
        "endpoints": {
            "/": "Server information",
            "/health": "Health check",
            "/sse": "SSE endpoint for ChatGPT",
            "/mcp": "MCP JSON-RPC endpoint"
        },
        "tools": [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in tools
        ],
        "wordpress_url": WORDPRESS_URL
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "wordpress-mcp-sse-server"
    }

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for ChatGPT connection"""
    
    async def event_generator():
        # Send initial endpoint event
        yield {
            "event": "endpoint",
            "data": json.dumps({"url": "http://localhost:8000/mcp"})
        }
        
        # Send heartbeat every 15 seconds
        try:
            while True:
                if await request.is_disconnected():
                    logger.info("SSE client disconnected")
                    break
                
                yield {
                    "event": "heartbeat",
                    "data": json.dumps({"status": "alive"})
                }
                
                await asyncio.sleep(15)
        except Exception as e:
            logger.error(f"SSE error: {e}")
    
    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP JSON-RPC endpoint"""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        logger.info(f"MCP request: method={method}, id={request_id}")
        
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "wordpress-mcp-server",
                    "version": "1.0.0"
                }
            }
            
        elif method == "tools/list":
            tools = await list_tools()
            result = {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools
                ]
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            content = await call_tool(tool_name, arguments)
            
            result = {
                "content": [
                    {
                        "type": content_item.type,
                        "text": content_item.text
                    }
                    for content_item in content
                ]
            }
            
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": request_id
                }
            )
        
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
        
    except Exception as e:
        logger.error(f"MCP endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": request_id if 'request_id' in locals() else None
            }
        )

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("WordPress MCP SSE Server")
    logger.info("=" * 60)
    logger.info(f"WordPress URL: {WORDPRESS_URL}")
    logger.info("Starting server on http://0.0.0.0:8000")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

