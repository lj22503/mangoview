#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SearXNG 数据源 - 新闻/政策搜索"""

import json
import subprocess
import os

SEARXNG_SCRIPT = os.path.join(
    os.path.dirname(__file__), '..', '..', 'skills', 'searxng', 'scripts', 'searxng.py'
)

def search(query, count=5):
    """搜索新闻/政策
    
    Args:
        query: 搜索关键词
        count: 返回结果数量
    
    Returns:
        list: [{title, url, snippet}, ...]
    """
    try:
        result = subprocess.run(
            ['uv', 'run', SEARXNG_SCRIPT, 'search', query, '--format', 'json', '-n', str(count)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=15,
            cwd=os.path.join(os.path.dirname(__file__), '..', '..')
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout.decode('utf-8'))
            return [
                {
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'snippet': r.get('content', ''),
                }
                for r in data.get('results', [])
            ]
    except Exception as e:
        print(f"SearXNG 搜索失败: {e}")
    return []


def search_news(topic):
    """搜索财经新闻
    
    Args:
        topic: 主题关键词
    
    Returns:
        list: [{title, url, snippet}, ...]
    """
    return search(f"{topic} 财经新闻 今日", count=5)


def search_policy(topic):
    """搜索政策信息
    
    Args:
        topic: 政策关键词
    
    Returns:
        list: [{title, url, snippet}, ...]
    """
    return search(f"{topic} 政策 发布", count=5)


if __name__ == '__main__':
    results = search_news('央行 利率')
    for r in results:
        print(f"- {r['title']}")
        print(f"  {r['url']}")
        print()
