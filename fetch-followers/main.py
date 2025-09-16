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
    python main.py
"""

import tweepy
import time
import os
import sys
import webbrowser
import urllib.parse
import base64
import hashlib
import secrets
from typing import List, Tuple, Optional
from dotenv import load_dotenv
import json
from datetime import datetime
from requests_oauthlib import OAuth2Session

# Load environment variables from .env file
load_dotenv()

class TwitterFollowersFetcher:
    """A class to handle Twitter followers fetching and sorting operations."""
    
    def __init__(self):
        """Initialize the X API v2 client with credentials from environment variables."""
        self.client = None
        self.oauth2_client = None
        self.authenticate()
    
    def authenticate(self) -> None:
        """Authenticate with X API v2 using Bearer Token for basic operations."""
        # Get Bearer Token from environment variables
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Check if Bearer Token is provided
        if not bearer_token:
            print("❌ Error: Missing Twitter API Bearer Token.")
            print("📋 Please set TWITTER_BEARER_TOKEN in your .env file.")
            print("🔗 You can get this from your Twitter Developer Portal app settings.")
            print("\n💡 To fix this:")
            print("1. Copy your .env.example to .env")
            print("2. Add your Bearer Token to the .env file")
            print("3. Make sure the .env file is in the same directory as main.py")
            sys.exit(1)
        
        try:
            # Use Bearer Token authentication for basic operations
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                wait_on_rate_limit=True
            )
            print("✅ Successfully authenticated with X API v2 (Bearer Token)")
            print("ℹ️  Note: OAuth 2.0 PKCE will be used for follower data access")
            
        except tweepy.TweepyException as e:
            print(f"❌ Error authenticating with X API v2: {e}")
            print("\n🔧 Troubleshooting tips:")
            print("• Check if your Bearer Token is valid")
            print("• Ensure your app is properly configured in the developer portal")
            print("• Verify your app has the required permissions")
            print("• Try regenerating your Bearer Token")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected authentication error: {e}")
            print("💡 Check your internet connection and try again")
            sys.exit(1)
    
    def generate_pkce_pair(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and code challenge."""
        # Generate code verifier (43-128 characters, URL-safe)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge (SHA256 hash of code verifier, base64url encoded)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def setup_oauth2_pkce(self) -> OAuth2Session:
        """Set up OAuth 2.0 PKCE session for followers endpoint."""
        client_id = os.getenv('TWITTER_CLIENT_ID')
        client_secret = os.getenv('TWITTER_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("Error: OAuth 2.0 PKCE requires TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET")
            print("Please set these environment variables in your .env file")
            sys.exit(1)
        
        # Generate PKCE pair
        code_verifier, code_challenge = self.generate_pkce_pair()
        
        # OAuth 2.0 endpoints
        authorization_base_url = 'https://twitter.com/i/oauth2/authorize'
        token_url = 'https://api.twitter.com/2/oauth2/token'
        
        # Required scopes for followers endpoint
        scope = ['tweet.read', 'users.read', 'follows.read']
        
        # Create OAuth2Session
        oauth = OAuth2Session(
            client_id=client_id,
            scope=scope,
            redirect_uri='http://localhost:8080/callback'
        )
        
        # Generate authorization URL
        authorization_url, state = oauth.authorization_url(
            authorization_base_url,
            code_challenge=code_challenge,
            code_challenge_method='S256'
        )
        
        print("🔐 OAuth 2.0 PKCE Authentication Required")
        print("=" * 50)
        print("To access follower data, you need to authorize this app.")
        print(f"Opening browser to: {authorization_url}")
        print("\nAfter authorization, you'll be redirected to a localhost page.")
        print("Copy the ENTIRE URL from your browser and paste it below.")
        
        # Open browser for authorization
        webbrowser.open(authorization_url)
        
        # Get authorization response from user
        redirect_response = input("\nPaste the full redirect URL here: ").strip()
        
        if not redirect_response:
            print("Error: No redirect URL provided")
            sys.exit(1)
        
        try:
            # Parse the redirect URL to get the authorization code
            parsed_url = urllib.parse.urlparse(redirect_response)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            if 'code' not in query_params:
                print("Error: No authorization code found in redirect URL")
                print("Make sure you copied the complete URL after authorization")
                sys.exit(1)
            
            authorization_code = query_params['code'][0]
            
            # Exchange authorization code for access token
            print("🔄 Exchanging authorization code for access token...")
            
            token = oauth.fetch_token(
                token_url,
                code=authorization_code,
                code_verifier=code_verifier,
                client_secret=client_secret
            )
            
            print("✅ Successfully authenticated with OAuth 2.0 PKCE!")
            return oauth
            
        except Exception as e:
            print(f"❌ Error during OAuth 2.0 PKCE flow: {e}")
            print("\n🔧 Troubleshooting tips:")
            print("• Check your TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET")
            print("• Ensure your app is properly configured in the developer portal")
            print("• Verify the callback URL matches: http://localhost:8080/callback")
            print("• Make sure you have the required OAuth 2.0 scopes enabled")
            sys.exit(1)
    
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
        if not self.oauth2_client:
            print("🔐 Setting up OAuth 2.0 PKCE authentication for followers...")
            try:
                self.oauth2_client = self.setup_oauth2_pkce()
            except Exception as e:
                print(f"❌ Failed to set up OAuth 2.0 PKCE: {e}")
                return []
        
        try:
            # First, get the user ID from the username using OAuth 2.0
            user_url = f"https://api.twitter.com/2/users/by/username/{screen_name}"
            user_response = self.oauth2_client.get(user_url, params={'user.fields': 'id,username'})
            
            if user_response.status_code != 200:
                self._handle_user_lookup_error(user_response, screen_name)
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
                response = self.oauth2_client.get(followers_url, params=params)
                
                if response.status_code != 200:
                    self._handle_followers_api_error(response)
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
    
    def _handle_user_lookup_error(self, response, screen_name: str) -> None:
        """Handle errors when looking up a user."""
        print(f"❌ Error looking up user @{screen_name}: {response.status_code}")
        
        if response.status_code == 404:
            print(f"   User @{screen_name} not found. Please check the username.")
        elif response.status_code == 401:
            print("   Authentication failed. Please check your API credentials.")
        elif response.status_code == 403:
            print("   Access forbidden. Your app may not have the required permissions.")
        else:
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"   Details: {error_data['detail']}")
            except:
                print(f"   Response: {response.text}")
    
    def _handle_followers_api_error(self, response) -> None:
        """Handle errors when fetching followers."""
        print(f"❌ Error fetching followers: {response.status_code}")
        
        try:
            error_data = response.json()
            print(f"   Response: {response.text}")
            
            # Handle specific error cases
            if response.status_code == 403:
                if 'reason' in error_data and error_data['reason'] == 'client-not-enrolled':
                    print("\n🚫 CRITICAL ERROR: Follower data requires Enterprise access!")
                    print("=" * 60)
                    print("The GET /2/users/id/followers endpoint is only available with:")
                    print("• Enterprise access (paid tier)")
                    print("• Essential/Elevated access does NOT include follower data")
                    print("\n📋 Your options:")
                    print("1. Upgrade to Enterprise access (expensive)")
                    print("2. Use alternative data sources")
                    print("3. Modify script to use available endpoints")
                    print("4. Use third-party services for follower data")
                    print("\n🔗 Reference: https://docs.x.com/x-api/users/follows/introduction")
                    print("=" * 60)
                elif 'title' in error_data and 'Client Forbidden' in error_data['title']:
                    print("\n🔒 Access Forbidden:")
                    print("• Your app may not be properly attached to a project")
                    print("• Check your API access level in the developer portal")
                    print("• Ensure you have the required permissions")
                else:
                    print(f"   Title: {error_data.get('title', 'Unknown error')}")
                    print(f"   Detail: {error_data.get('detail', 'No details available')}")
            
            elif response.status_code == 401:
                print("🔐 Authentication Error:")
                print("• Your access token may have expired")
                print("• Check your OAuth 2.0 credentials")
                print("• Try re-authenticating")
            
            elif response.status_code == 429:
                print("⏰ Rate Limit Exceeded:")
                print("• You've hit the API rate limit")
                print("• Wait before making more requests")
                print("• Consider implementing exponential backoff")
            
            elif response.status_code == 400:
                print("❌ Bad Request:")
                print("• Check your request parameters")
                print("• Ensure the user ID is valid")
                print("• Verify your query parameters")
            
        except Exception as e:
            print(f"   Could not parse error response: {e}")
            print(f"   Raw response: {response.text}")
    
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
