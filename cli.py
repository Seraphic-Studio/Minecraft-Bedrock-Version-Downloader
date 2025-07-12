import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcbedrock_downloader.cli import cli_main

if __name__ == "__main__":
    cli_main()
