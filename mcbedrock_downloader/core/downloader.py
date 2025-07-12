import warnings
import sys
import asyncio
import aiohttp
from typing import Optional, Callable

from .wu_protocol import WUProtocol
from .exceptions import BadUpdateIdentityException, DownloadFailedException

if sys.platform == 'win32':
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Event loop is closed.*")


class VersionDownloader:
    
    def __init__(self):
        self.protocol = WUProtocol()
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    def enable_user_authorization(self, token: str):
        self.protocol.set_msa_user_token(token)
        
    async def post_xml_async(self, url: str, xml_data: str) -> str:
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'User-Agent': 'Windows-Update-Agent/10.0.10011.16384 Client-Protocol/1.40'
        }
        
        async with self.session.post(url, data=xml_data, headers=headers) as response:
            response.raise_for_status()
            return await response.text()
            
    async def get_download_url(self, update_identity: str, revision_number: str) -> Optional[str]:
        request_xml = self.protocol.build_download_request(update_identity, revision_number)
        
        try:
            response_xml = await self.post_xml_async(self.protocol.get_download_url(), request_xml)
            
            urls = self.protocol.extract_download_response_urls(response_xml)
            for url in urls:
                if url.startswith("http://tlu.dl.delivery.mp.microsoft.com/"):
                    return url
                    
        except Exception as e:
            print(f"Error getting download URL: {e}")
            
        return None
        
    async def download_file(self, url: str, destination: str, progress_callback: Optional[Callable] = None):
        print(f"Downloading from: {url}")
        
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                
                if progress_callback:
                    progress_callback(0, total_size)
                    
                downloaded = 0
                chunk_size = 1024 * 1024
                
                with open(destination, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress_callback(downloaded, total_size)
                            
        except Exception as e:
            raise DownloadFailedException(f"Failed to download file: {e}")
                        
    async def download(self, update_identity: str, revision_number: str, destination: str, 
                      progress_callback: Optional[Callable] = None):
        print(f"Starting download for update identity: {update_identity}")
        
        download_url = await self.get_download_url(update_identity, revision_number)
        if not download_url:
            raise BadUpdateIdentityException("Unable to get download URL")
            
        print(f"Resolved download link: {download_url}")
        await self.download_file(download_url, destination, progress_callback)
