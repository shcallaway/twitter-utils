#!/usr/bin/env python3
"""
Twitter Followers Fetcher and Sorter

This script fetches a list of Twitter followers and sorts them by follower count.
It uses the X API v2 with Tweepy library for authentication and data retrieval.

Requirements:
- Twitter Developer Account with API credentials
- Python 3.6+
- Required packages: tweepy, python-dotenv

Usage:
    python utils/fetch_followers.py
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Tuple, Optional

# Add the current directory to the path so we can import from lib
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.twitter_client import TwitterAPIClient


class TwitterFollowersFetcher:
    """A class to handle Twitter followers fetching and sorting operations."""
    
    def __init__(self):
        """Initialize the Twitter API client."""
        self.api_client = TwitterAPIClient()
    
    def get_followers_sorted_by_follower_count(self, screen_name: str, max_followers: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Fetch followers and sort them by follower count in descending order.
        
        Args:
            screen_name: Twitter username (without @)
            max_followers: Maximum number of followers to fetch (None for all)
            
        Returns:
            List of tuples containing (username, follower_count) sorted by follower count
        """
        followers = []
        fetched_count = 0
        
        print(f"Fetching followers for @{screen_name}...")
        
        # Set up OAuth 2.0 PKCE for followers endpoint
        if not self.api_client.oauth2_client:
            print("🔐 Setting up OAuth 2.0 PKCE authentication for followers...")
            try:
                self.api_client.oauth2_client = self.api_client.setup_oauth2_pkce()
            except Exception as e:
                print(f"❌ Failed to set up OAuth 2.0 PKCE: {e}")
                return []
        
        try:
            # First, get the user ID from the username using OAuth 2.0
            user_url = f"https://api.twitter.com/2/users/by/username/{screen_name}"
            user_response = self.api_client.oauth2_client.get(user_url, params={'user.fields': 'id,username'})
            
            if user_response.status_code != 200:
                self.api_client._handle_user_lookup_error(user_response, screen_name)
                return []
            
            user_data = user_response.json()
            if 'data' not in user_data:
                print(f"❌ Error: User @{screen_name} not found")
                return []
            
            user_id = user_data['data']['id']
            print(f"✅ Found user ID: {user_id}")
            
            # Use pagination to fetch followers using OAuth 2.0
            followers_url = f"https://api.twitter.com/2/users/{user_id}/followers"
            pagination_token = None
            
            while True:
                # Prepare parameters for the API request
                params = {
                    'max_results': 100,  # Maximum per request for v2
                    'user.fields': 'username,public_metrics'
                }
                
                if pagination_token:
                    params['pagination_token'] = pagination_token
                
                # Fetch followers using OAuth 2.0
                response = self.api_client.oauth2_client.get(followers_url, params=params)
                
                if response.status_code != 200:
                    self.api_client._handle_followers_api_error(response)
                    break
                
                data = response.json()
                
                if 'data' not in data or not data['data']:
                    break
                
                # Process the followers
                for follower in data['data']:
                    # Get follower count from public_metrics
                    follower_count = 0
                    if 'public_metrics' in follower and follower['public_metrics']:
                        follower_count = follower['public_metrics'].get('followers_count', 0)
                    
                    followers.append((follower['username'], follower_count))
                    fetched_count += 1
                    
                    # Progress indicator
                    if fetched_count % 100 == 0:
                        print(f"📊 Fetched {fetched_count} followers...")
                    
                    # Check if we've reached the maximum
                    if max_followers and fetched_count >= max_followers:
                        print(f"🛑 Reached maximum of {max_followers} followers")
                        break
                
                # Check if we've reached the maximum
                if max_followers and fetched_count >= max_followers:
                    break
                
                # Check if there are more pages
                if 'meta' not in data or 'next_token' not in data['meta']:
                    break
                
                pagination_token = data['meta']['next_token']
                
                # Small delay to be respectful to the API
                import time
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Unexpected error fetching followers: {e}")
            if "Rate limit exceeded" in str(e):
                print("⏰ Rate limit exceeded. The script will wait and retry automatically.")
            elif "401 Unauthorized" in str(e) or "Unauthorized" in str(e):
                print("\n🔒 This error indicates that your Twitter API access level doesn't include follower data.")
                print("📋 To fix this:")
                print("   1. Go to https://developer.twitter.com/")
                print("   2. Check your app permissions")
                print("   3. Apply for elevated access or upgrade to a paid plan")
                print("   4. Ensure your app has 'Read' permissions with 'follows.read' scope")
            return followers
        
        print(f"✅ Successfully fetched {len(followers)} followers")
        
        # Sort followers by follower count in descending order
        followers_sorted = sorted(followers, key=lambda x: x[1], reverse=True)
        
        return followers_sorted
    
    def save_results(self, followers: List[Tuple[str, int]], screen_name: str, output_format: str = 'both') -> None:
        """
        Save the results to file(s).
        
        Args:
            followers: List of (username, follower_count) tuples
            screen_name: Twitter username
            output_format: 'txt', 'json', or 'both'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format in ['txt', 'both']:
            txt_filename = f"followers_{screen_name}_{timestamp}.txt"
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(f"Followers of @{screen_name} sorted by follower count\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total followers: {len(followers)}\n")
                f.write("-" * 50 + "\n\n")
                
                for i, (username, count) in enumerate(followers, 1):
                    f.write(f"{i:4d}. @{username:<20} - {count:,} followers\n")
            
            print(f"✓ Results saved to {txt_filename}")
        
        if output_format in ['json', 'both']:
            json_filename = f"followers_{screen_name}_{timestamp}.json"
            data = {
                'screen_name': screen_name,
                'generated_at': datetime.now().isoformat(),
                'total_followers': len(followers),
                'followers': [
                    {'username': username, 'follower_count': count, 'rank': i+1}
                    for i, (username, count) in enumerate(followers)
                ]
            }
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Results saved to {json_filename}")
    
    def print_top_followers(self, followers: List[Tuple[str, int]], top_n: int = 20) -> None:
        """
        Print the top N followers by follower count.
        
        Args:
            followers: List of (username, follower_count) tuples
            top_n: Number of top followers to display
        """
        print(f"\n🏆 Top {min(top_n, len(followers))} followers by follower count:")
        print("-" * 60)
        
        for i, (username, count) in enumerate(followers[:top_n], 1):
            print(f"{i:2d}. @{username:<25} - {count:,} followers")


def main():
    """Main function to run the Twitter followers fetcher."""
    print("🐦 Twitter Followers Fetcher and Sorter")
    print("=" * 50)
    
    try:
        # Get Twitter username from user input
        screen_name = input("Enter Twitter username (without @): ").strip()
        if not screen_name:
            print("❌ Error: Username cannot be empty")
            return
        
        # Validate username format
        if screen_name.startswith('@'):
            screen_name = screen_name[1:]
            print(f"ℹ️  Removed @ symbol. Using: {screen_name}")
        
        # Get maximum followers limit
        max_followers_input = input("Enter maximum number of followers to fetch (press Enter for all): ").strip()
        max_followers = None
        if max_followers_input:
            try:
                max_followers = int(max_followers_input)
                if max_followers <= 0:
                    print("❌ Error: Maximum followers must be a positive number")
                    return
                if max_followers > 10000:
                    print("⚠️  Warning: Large follower counts may take a long time and hit rate limits")
            except ValueError:
                print("❌ Error: Please enter a valid number")
                return
        
        # Get output format preference
        output_format = input("Output format (txt/json/both) [both]: ").strip().lower()
        if output_format not in ['txt', 'json', 'both']:
            output_format = 'both'
            print("ℹ️  Using default format: both")
        
        # Initialize the fetcher
        print("\n🔧 Initializing Twitter API client...")
        fetcher = TwitterFollowersFetcher()
        
        # Fetch and sort followers
        followers = fetcher.get_followers_sorted_by_follower_count(screen_name, max_followers)
        
        if not followers:
            print("\n❌ No followers found or error occurred.")
            print("\n💡 Possible reasons:")
            print("• User has no followers")
            print("• API access level insufficient (requires Enterprise)")
            print("• Authentication issues")
            print("• User account is private or suspended")
            return
        
        # Display top followers
        fetcher.print_top_followers(followers)
        
        # Save results
        print(f"\n💾 Saving results...")
        fetcher.save_results(followers, screen_name, output_format)
        
        print(f"\n✅ Successfully processed {len(followers)} followers!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
    except FileNotFoundError as e:
        print(f"\n❌ File error: {e}")
        print("💡 Make sure you're running the script from the correct directory")
    except PermissionError as e:
        print(f"\n❌ Permission error: {e}")
        print("💡 Check file permissions in the current directory")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\n🔧 General troubleshooting:")
        print("• Check your internet connection")
        print("• Verify your .env file has correct credentials")
        print("• Ensure you have the required API access level")
        print("• Try running the script again")


if __name__ == "__main__":
    main()
