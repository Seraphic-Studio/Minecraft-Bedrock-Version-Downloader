import re
from typing import Optional, Tuple


def format_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_version(version_string: str) -> bool:
    pattern = r'^\d+\.\d+\.\d+(\.\d+)?$'
    return bool(re.match(pattern, version_string))


def parse_version_string(version_string: str) -> Optional[Tuple[int, int, int, int]]:
    if not validate_version(version_string):
        return None
        
    parts = version_string.split('.')
    if len(parts) == 3:
        parts.append('0')
        
    try:
        return tuple(int(part) for part in parts)
    except ValueError:
        return None


def compare_versions(v1: str, v2: str) -> int:
    parsed_v1 = parse_version_string(v1)
    parsed_v2 = parse_version_string(v2)
    
    if parsed_v1 is None or parsed_v2 is None:
        return 0
        
    if parsed_v1 < parsed_v2:
        return -1
    elif parsed_v1 > parsed_v2:
        return 1
    else:
        return 0


def progress_callback(downloaded: int, total: int):
    if total > 0:
        percentage = (downloaded / total) * 100
        print(f"\rProgress: {format_size(downloaded)} / {format_size(total)} ({percentage:.1f}%)", end='', flush=True)
    else:
        print(f"\rDownloaded: {format_size(downloaded)}", end='', flush=True)
    
    if total > 0 and downloaded >= total:
        print()


def get_default_filename(version_name: str, version_type: str) -> str:
    if version_type == "Preview":
        return f"Minecraft-Preview-{version_name}.appx"
    else:
        return f"Minecraft-{version_name}.appx"


def sanitize_filename(filename: str) -> str:
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    filename = filename.strip(' .')
    
    return filename
