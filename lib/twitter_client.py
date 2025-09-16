#!/usr/bin/env python3
"""
Shared Twitter API client functionality for utility scripts.

This module provides common Twitter API operations that can be used
across multiple utility scripts in the twitter-utils repository.
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
from requests_oauthlib import OAuth2Session

# Load environment variables from .env file
load_dotenv()


class TwitterAPIClient:
    """A shared Twitter API client for utility scripts."""
    
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
