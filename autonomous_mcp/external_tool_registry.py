# 🔧 External Tool Registry for MCP Ecosystem Integration
# Defines proxy tools that forward to external MCP servers in Claude Desktop

EXTERNAL_TOOL_REGISTRY = {
    # Web Search Tools (3)
    'brave_web_search': {
        'server': 'brave_search',
        'description': 'Search the web using Brave Search API for general queries, news, and articles',
        'parameters': {
            'query': 'string',
            'count': 'number',
            'offset': 'number'
        },
        'category': 'web_interaction',
        'subcategory': 'search'
    },
    
    'brave_local_search': {
        'server': 'brave_search', 
        'description': 'Search for local businesses and places using Brave Local Search',
        'parameters': {
            'query': 'string',
            'count': 'number'
        },
        'category': 'web_interaction',
        'subcategory': 'local_search'
    },
    
    'duckduckgo_web_search': {
        'server': 'duckduckgo',
        'description': 'Search the web using DuckDuckGo for privacy-focused results',
        'parameters': {
            'query': 'string',
            'count': 'number',
            'safeSearch': 'string'
        },
        'category': 'web_interaction',
        'subcategory': 'search'
    },
    
    # Memory & Knowledge Graph Tools (5)
    'create_entities': {
        'server': 'memory_server',
        'description': 'Create entities in the knowledge graph for information storage',
        'parameters': {
            'entities': 'array'
        },
        'category': 'memory_knowledge',
        'subcategory': 'entity_creation'
    },    
    'create_relations': {
        'server': 'memory_server',
        'description': 'Create relationships between entities in the knowledge graph',
        'parameters': {
            'relations': 'array'
        },
        'category': 'memory_knowledge',
        'subcategory': 'relationship_management'
    },
    
    'add_observations': {
        'server': 'memory_server',
        'description': 'Add observations to existing entities in the knowledge graph',
        'parameters': {
            'observations': 'array'
        },
        'category': 'memory_knowledge',
        'subcategory': 'data_enrichment'
    },
    
    'search_nodes': {
        'server': 'memory_server',
        'description': 'Search for nodes in the knowledge graph based on query',
        'parameters': {
            'query': 'string'
        },
        'category': 'memory_knowledge',
        'subcategory': 'information_retrieval'
    },
    
    'read_graph': {
        'server': 'memory_server',
        'description': 'Read the entire knowledge graph structure',
        'parameters': {},
        'category': 'memory_knowledge',
        'subcategory': 'data_access'
    },
    
    # GitHub Development Tools (10)
    'search_repositories': {
        'server': 'github_mcp',
        'description': 'Search for GitHub repositories using GitHub search API',
        'parameters': {
            'query': 'string',
            'page': 'number',
            'perPage': 'number'
        },
        'category': 'code_development',
        'subcategory': 'repository_management'
    },
    
    'create_repository': {
        'server': 'github_mcp',
        'description': 'Create a new GitHub repository in your account',        'parameters': {
            'name': 'string',
            'description': 'string',
            'private': 'boolean',
            'autoInit': 'boolean'
        },
        'category': 'code_development',
        'subcategory': 'repository_management'
    },
    
    'get_file_contents': {
        'server': 'github_mcp',
        'description': 'Get the contents of a file from a GitHub repository',
        'parameters': {
            'owner': 'string',
            'repo': 'string',
            'path': 'string',
            'branch': 'string'
        },
        'category': 'code_development',
        'subcategory': 'file_operations'
    },
    
    'create_or_update_file': {
        'server': 'github_mcp',
        'description': 'Create or update a file in a GitHub repository',
        'parameters': {
            'owner': 'string',
            'repo': 'string',
            'path': 'string',
            'content': 'string',
            'message': 'string',
            'branch': 'string'
        },
        'category': 'code_development',
        'subcategory': 'file_operations'
    },
    
    'create_issue': {
        'server': 'github_mcp',
        'description': 'Create a new issue in a GitHub repository',
        'parameters': {
            'owner': 'string',
            'repo': 'string',
            'title': 'string',
            'body': 'string',
            'labels': 'array'
        },
        'category': 'code_development',
        'subcategory': 'issue_management'
    },
    
    'create_pull_request': {
        'server': 'github_mcp',
        'description': 'Create a new pull request in a GitHub repository',        'parameters': {
            'owner': 'string',
            'repo': 'string',
            'title': 'string',
            'head': 'string',
            'base': 'string',
            'body': 'string'
        },
        'category': 'code_development',
        'subcategory': 'collaboration'
    },
    
    # File System Tools (5 most essential)
    'read_file': {
        'server': 'desktop_commander',
        'description': 'Read file contents from the local file system',
        'parameters': {
            'path': 'string',
            'offset': 'number',
            'length': 'number'
        },
        'category': 'file_system',
        'subcategory': 'file_operations'
    },
    
    'write_file': {
        'server': 'desktop_commander',
        'description': 'Write or append content to a file',
        'parameters': {
            'path': 'string',
            'content': 'string',
            'mode': 'string'
        },
        'category': 'file_system',
        'subcategory': 'file_operations'
    },
    
    'list_directory': {
        'server': 'desktop_commander',
        'description': 'List contents of a directory',
        'parameters': {
            'path': 'string'
        },
        'category': 'file_system',
        'subcategory': 'directory_operations'
    },
    
    'search_files': {
        'server': 'desktop_commander',
        'description': 'Search for files by name pattern',        'parameters': {
            'path': 'string',
            'pattern': 'string'
        },
        'category': 'file_system',
        'subcategory': 'search'
    },
    
    'execute_command': {
        'server': 'desktop_commander',
        'description': 'Execute terminal commands with timeout',
        'parameters': {
            'command': 'string',
            'timeout_ms': 'number'
        },
        'category': 'file_system',
        'subcategory': 'command_execution'
    }
}

# Tool Categories for organization
TOOL_CATEGORIES = {
    'web_interaction': 'Web Search and Information Retrieval',
    'memory_knowledge': 'Knowledge Graph and Memory Management', 
    'code_development': 'Software Development and Version Control',
    'file_system': 'File System and Command Line Operations',
    'api_testing': 'API Development and Testing',
    'task_management': 'Project Task Management and Planning',
    'browser_automation': 'Web Browser Automation and Testing',
    'content_processing': 'Content Extraction and Processing',
    'project_management': 'Project Board and Collaboration'
}

# Server information for reference
MCP_SERVERS = {
    'brave_search': 'Brave Web Search API integration',
    'duckduckgo': 'DuckDuckGo privacy-focused search',
    'memory_server': 'Knowledge graph and entity storage',
    'github_mcp': 'GitHub API integration for development',
    'desktop_commander': 'Local file system and command execution',
    'postman': 'API testing and development platform',
    'taskmaster': 'Project task management and planning',
    'puppeteer': 'Browser automation and web testing',
    'youtube': 'YouTube content processing',
    'firecrawl': 'Advanced web scraping and content extraction',
    'trello': 'Project board and team collaboration'
}
