#!/usr/bin/env python3
"""
Twitter Utils - Main Launcher

A collection of Twitter utility scripts for various tasks.
This script serves as the main entry point to launch different utilities.

Usage:
    python main.py [utility_name]
    
Available utilities:
    fetch_followers    - Fetch and sort Twitter followers by follower count
    scrape_followers   - Scrape Twitter followers using Stagehand browser automation
    help              - Show this help message
"""

import sys
import os
from typing import Dict, Callable


def show_help():
    """Display help information for available utilities."""
    print("🐦 Twitter Utils - Available Scripts")
    print("=" * 50)
    print()
    print("Usage: python main.py [utility_name]")
    print()
    print("Available utilities:")
    print()
    print("  fetch_followers    - Fetch and sort Twitter followers by follower count")
    print("                      Fetches followers for a given Twitter account and")
    print("                      sorts them by their follower count in descending order.")
    print("                      Supports both TXT and JSON output formats.")
    print()
    print("  scrape_followers   - Scrape Twitter followers using Stagehand browser automation")
    print("                      Uses AI-powered browser automation to scrape follower data")
    print("                      from Twitter profiles. Requires Browserbase and AI model API keys.")
    print("                      Supports both TXT and JSON output formats.")
    print()
    print("  help              - Show this help message")
    print()
    print("Examples:")
    print("  python main.py fetch_followers")
    print("  python main.py scrape_followers")
    print("  python main.py help")
    print()
    print("For more detailed information about each utility, run it directly:")
    print("  python fetch_followers.py")
    print("  python scrape_followers.py")


def run_fetch_followers():
    """Run the fetch followers utility."""
    try:
        # Import and run the fetch followers script
        from fetch_followers import main as fetch_followers_main
        fetch_followers_main()
    except ImportError as e:
        print(f"❌ Error importing fetch_followers utility: {e}")
        print("💡 Make sure you're running from the correct directory")
    except Exception as e:
        print(f"❌ Error running fetch_followers utility: {e}")


def run_scrape_followers():
    """Run the scrape followers utility."""
    try:
        # Import and run the scrape followers script
        from scrape_followers import main as scrape_followers_main
        import asyncio
        asyncio.run(scrape_followers_main())
    except ImportError as e:
        print(f"❌ Error importing scrape_followers utility: {e}")
        print("💡 Make sure you're running from the correct directory")
    except Exception as e:
        print(f"❌ Error running scrape_followers utility: {e}")


def main():
    """Main launcher function."""
    # Available utilities
    utilities: Dict[str, Callable] = {
        'fetch_followers': run_fetch_followers,
        'scrape_followers': run_scrape_followers,
        'help': show_help,
    }
    
    # Get the utility name from command line arguments
    if len(sys.argv) < 2:
        utility_name = 'help'
    else:
        utility_name = sys.argv[1].lower()
    
    # Check if the utility exists
    if utility_name not in utilities:
        print(f"❌ Unknown utility: {utility_name}")
        print()
        show_help()
        sys.exit(1)
    
    # Run the selected utility
    try:
        utilities[utility_name]()
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Try running the utility directly for more detailed error information")


if __name__ == "__main__":
    main()