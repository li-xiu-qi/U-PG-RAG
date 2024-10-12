import hashlib
import json
import os
from urllib.parse import urlparse

import diskcache as dc


class SiteFilter:
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.cache = dc.Cache(cache_dir)

    def _hash_url(self, url: str) -> str:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return hashlib.md5(base_url.encode('utf-8')).hexdigest()

    def add_url(self, url: str):
        url_hash = self._hash_url(url)
        self.cache[url_hash] = url

    def check_url(self, url: str):
        url_hash = self._hash_url(url)
        return self.cache.get(url_hash, None)

    def export_to_json(self, file_path: str):
        if not file_path.endswith('.json'):
            raise ValueError("File path must have a .json extension")
        cache_dict = {key: self.cache[key] for key in self.cache}
        with open(file_path, 'w') as f:
            json.dump(cache_dict, f)


if __name__ == "__main__":
    filter = SiteFilter('./z_test_cache')
    filter.add_url('https://example.com')
    print(filter.check_url('https://example.com'))
    filter.export_to_json('./export.json')
