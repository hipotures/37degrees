#!/usr/bin/env python3
"""
Simple script to list all 37d agents with their metadata as JSON.
Usage: python scripts/list-agents.py
"""
import json
import os
import re
from pathlib import Path

def extract_agent_metadata():
    agents = []
    agents_dir = Path('.claude/agents')
    
    if not agents_dir.exists():
        return agents
    
    for agent_file in agents_dir.glob('37d-*.md'):
        agent_name = agent_file.stem
        
        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    yaml_content = content[3:yaml_end]
                    
                    # Extract fields with regex
                    execution_order = re.search(r'^execution_order:\s*(\d+)', yaml_content, re.MULTILINE)
                    todo_list = re.search(r'^todo_list:\s*(true|false)', yaml_content, re.MULTILINE | re.IGNORECASE)
                    min_tasks = re.search(r'^min_tasks:\s*(\d+)', yaml_content, re.MULTILINE)
                    max_tasks = re.search(r'^max_tasks:\s*(\d+)', yaml_content, re.MULTILINE)
                    
                    agent_data = {
                        'name': agent_name,
                        'execution_order': int(execution_order.group(1)) if execution_order else None,
                        'todo_list': todo_list.group(1).lower() == 'true' if todo_list else True,
                        'min_tasks': int(min_tasks.group(1)) if min_tasks else None,
                        'max_tasks': int(max_tasks.group(1)) if max_tasks else None
                    }
                    
                    agents.append(agent_data)
        
        except Exception as e:
            print(f"Error processing {agent_file}: {e}", file=sys.stderr)
            continue
    
    # Sort by name
    agents.sort(key=lambda x: x['name'])
    return agents

if __name__ == '__main__':
    import sys
    agents = extract_agent_metadata()
    
    # Create agent_list (just names)
    agent_list = [agent['name'] for agent in agents]
    
    # Create grouped_agents (by execution_order)
    grouped_agents = {}
    for agent in agents:
        order = agent['execution_order']
        if order is not None:
            if order not in grouped_agents:
                grouped_agents[order] = []
            grouped_agents[order].append(agent['name'])
    
    # Sort groups by execution_order
    grouped_agents = dict(sorted(grouped_agents.items()))
    
    # Output all data
    result = {
        "agents": agents,
        "agent_list": agent_list,
        "grouped_agents": grouped_agents
    }
    
    print(json.dumps(result, indent=2))