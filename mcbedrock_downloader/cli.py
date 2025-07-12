import argparse
import asyncio
import sys
import os

from .core.downloader import VersionDownloader
from .core.version_list import VersionList
from .core.exceptions import BadUpdateIdentityException
from .utils.helpers import format_size, progress_callback, get_default_filename


async def main():
    parser = argparse.ArgumentParser(description='Minecraft Bedrock Version Downloader')
    parser.add_argument('--list', action='store_true', help='List available versions')
    parser.add_argument('--download', metavar='UUID', help='Download version by UUID')
    parser.add_argument('--name', metavar='NAME', help='Download version by name')
    parser.add_argument('--type', choices=['release', 'beta', 'preview'], default='release', 
                       help='Version type to filter (default: release)')
    parser.add_argument('--output', '-o', metavar='PATH', help='Output file path')
    parser.add_argument('--token', metavar='TOKEN', help='MSA token for beta versions')
    parser.add_argument('--api', metavar='URL', 
                       default="https://raw.githubusercontent.com/ddf8196/mc-w10-versiondb-auto-update/refs/heads/master/versions.json.min",
                       help='Version list API URL')
    parser.add_argument('--search', metavar='QUERY', help='Search versions by name')
    
    args = parser.parse_args()
    
    print("Loading version list...")
    version_list = VersionList(args.api)
    
    try:
        await version_list.download_list()
    except Exception as e:
        print(f"Error loading version list: {e}")
        return 1
        
    print(f"Loaded {len(version_list.versions)} versions")
    
    if args.search:
        results = version_list.search_versions(args.search)
        print(f"\\nSearch results for '{args.search}':")
        print("-" * 80)
        for version in results:
            print(f"{version['name']:<30} {version['type_name']:<10} {version['uuid']}")
        return 0
    
    if args.list:
        type_filter = {'release': 0, 'beta': 1, 'preview': 2}.get(args.type, 0)
        filtered_versions = version_list.get_versions_by_type(type_filter)
        
        print(f"\\n{args.type.title()} versions:")
        print("-" * 80)
        for version in filtered_versions:
            print(f"{version['name']:<30} {version['type_name']:<10} {version['uuid']}")
        
        return 0
    
    if args.download or args.name:
        target_version = None
        
        if args.download:
            target_version = version_list.get_version_by_uuid(args.download)
        elif args.name:
            target_version = version_list.get_version_by_name(args.name)
                    
        if not target_version:
            print("Version not found!")
            return 1
            
        if args.output:
            output_path = args.output
        else:
            output_path = get_default_filename(target_version['name'], target_version['type_name'])
                
        print(f"\\nDownloading {target_version['name']} ({target_version['type_name']})")
        print(f"UUID: {target_version['uuid']}")
        print(f"Output: {output_path}")
        
        if target_version['version_type'] == 1 and not args.token:
            print("\\nWARNING: Beta versions require authentication!")
            print("Please provide an MSA token using --token parameter")
            print("You can obtain this token from the Xbox authentication process")
            return 1
            
        try:
            async with VersionDownloader() as downloader:
                if args.token:
                    downloader.enable_user_authorization(args.token)
                    
                await downloader.download(
                    target_version['uuid'], 
                    "1",
                    output_path,
                    progress_callback
                )
                
            print(f"\\nDownload completed: {output_path}")
            
        except BadUpdateIdentityException:
            print("\\nError: Unable to fetch download URL")
            if target_version['version_type'] == 1:
                print("For beta versions, make sure:")
                print("1. Your account is subscribed to the Minecraft beta program")
                print("2. You have provided a valid MSA token")
            return 1
        except Exception as e:
            print(f"\\nDownload failed: {e}")
            return 1
    
    if not any([args.list, args.download, args.name, args.search]):
        parser.print_help()
        return 0
            
    return 0


def cli_main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        if os.environ.get('PYTHONIOENCODING') is None:
            os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        if sys.platform == 'win32':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                exit_code = loop.run_until_complete(main())
                sys.exit(exit_code)
            finally:
                loop.close()
        else:
            exit_code = asyncio.run(main())
            sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
