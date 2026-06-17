"""
统一缓存管理

两层缓存：内存（快）+ 文件（持久）
"""

import os
import time
import json
import hashlib
from typing import Any, Optional
from datetime import datetime

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')


class CacheManager:
    """两层缓存管理器（内存 + 文件）"""

    def __init__(self, ttl: int = 300, use_file_cache: bool = True, cache_dir: str = None):
        """
        Args:
            ttl: 默认缓存有效期（秒）
            use_file_cache: 是否启用文件缓存
            cache_dir: 文件缓存目录
        """
        self.ttl = ttl
        self.use_file_cache = use_file_cache
        self.cache_dir = cache_dir or CACHE_DIR
        self._memory = {}

        if use_file_cache:
            os.makedirs(self.cache_dir, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        """获取缓存（先内存后文件）"""
        now = time.time()

        # 内存缓存
        if key in self._memory:
            entry = self._memory[key]
            if now < entry['expires']:
                return entry['data']
            del self._memory[key]

        # 文件缓存
        if self.use_file_cache:
            fpath = self._file_path(key)
            if os.path.exists(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                    if now < entry['expires']:
                        self._memory[key] = entry
                        return entry['data']
                    os.remove(fpath)
                except Exception:
                    pass

        return None

    def set(self, key: str, data: Any, ttl: int = None) -> None:
        """写入缓存"""
        ttl = ttl if ttl is not None else self.ttl
        entry = {
            'data': data,
            'expires': time.time() + ttl,
            'timestamp': datetime.now().isoformat(),
        }

        self._memory[key] = entry

        if self.use_file_cache:
            try:
                fpath = self._file_path(key)
                with open(fpath, 'w', encoding='utf-8') as f:
                    json.dump(entry, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

    def delete(self, key: str) -> bool:
        deleted = key in self._memory
        self._memory.pop(key, None)
        if self.use_file_cache:
            fpath = self._file_path(key)
            if os.path.exists(fpath):
                os.remove(fpath)
                deleted = True
        return deleted

    def clear(self) -> None:
        self._memory.clear()
        if self.use_file_cache and os.path.exists(self.cache_dir):
            for fn in os.listdir(self.cache_dir):
                try:
                    os.remove(os.path.join(self.cache_dir, fn))
                except Exception:
                    pass

    def cleanup_expired(self) -> int:
        count = 0
        now = time.time()
        expired = [k for k, v in self._memory.items() if now >= v['expires']]
        for k in expired:
            del self._memory[k]
            count += 1
        if self.use_file_cache and os.path.exists(self.cache_dir):
            for fn in os.listdir(self.cache_dir):
                fpath = os.path.join(self.cache_dir, fn)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                    if now >= entry['expires']:
                        os.remove(fpath)
                        count += 1
                except Exception:
                    try:
                        os.remove(fpath)
                        count += 1
                    except Exception:
                        pass
        return count

    def stats(self) -> dict:
        now = time.time()
        mem_total = len(self._memory)
        mem_valid = sum(1 for v in self._memory.values() if now < v['expires'])
        file_total, file_valid = 0, 0
        if self.use_file_cache and os.path.exists(self.cache_dir):
            for fn in os.listdir(self.cache_dir):
                file_total += 1
                try:
                    with open(os.path.join(self.cache_dir, fn), 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                    if now < entry['expires']:
                        file_valid += 1
                except Exception:
                    pass
        return {
            'memory': {'total': mem_total, 'valid': mem_valid},
            'file': {'total': file_total, 'valid': file_valid},
            'ttl': self.ttl,
        }

    def _file_path(self, key: str) -> str:
        h = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{h}.json")
