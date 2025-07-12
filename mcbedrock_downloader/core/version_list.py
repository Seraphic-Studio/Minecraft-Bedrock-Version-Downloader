import json
import aiohttp
from typing import List, Dict, Optional


class VersionList:
    
    def __init__(self, versions_api: str = "https://raw.githubusercontent.com/ddf8196/mc-w10-versiondb-auto-update/refs/heads/master/versions.json.min"):
        self.versions_api = versions_api
        self.versions = []
        
    async def download_list(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.versions_api) as response:
                response.raise_for_status()
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    data = await response.json()
                else:
                    text = await response.text()
                    data = json.loads(text)
                
        self.versions = []
        for item in data:
            if len(item) >= 3:
                name, uuid, version_type = item[0], item[1], item[2]
                self.versions.append({
                    'name': name,
                    'uuid': uuid,
                    'version_type': version_type,
                    'type_name': self.get_version_type_name(version_type)
                })
                
        return self.versions
        
    def get_version_type_name(self, version_type: int) -> str:
        type_names = {
            0: "Release",
            1: "Beta", 
            2: "Preview"
        }
        return type_names.get(version_type, "Unknown")
        
    def get_versions_by_type(self, version_type: int) -> List[Dict]:
        return [v for v in self.versions if v['version_type'] == version_type]
        
    def search_versions(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        return [v for v in self.versions if query_lower in v['name'].lower()]
        
    def get_version_by_uuid(self, uuid: str) -> Optional[Dict]:
        for version in self.versions:
            if version['uuid'] == uuid:
                return version
        return None
        
    def get_version_by_name(self, name: str) -> Optional[Dict]:
        for version in self.versions:
            if version['name'] == name:
                return version
        return None
        
    def sort_versions(self, reverse: bool = True) -> List[Dict]:
        return sorted(self.versions, key=lambda x: x['name'], reverse=reverse)
