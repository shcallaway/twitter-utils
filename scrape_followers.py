#!/usr/bin/env python3
"""
Twitter Followers Scraper using Stagehand

This script uses the Stagehand library to scrape Twitter followers by automating
a web browser to navigate to Twitter profiles and extract follower information.

Requirements:
- Browserbase account and API credentials
- AI model API key (OpenAI, Anthropic, etc.)
- Python 3.6+
- Required packages: stagehand, python-dotenv, pydantic

Usage:
    python scrape_followers.py
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Add the current directory to the path so we can import from lib
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from stagehand import StagehandConfig, Stagehand


class TwitterUser(BaseModel):
    """Pydantic model for Twitter user data."""
    username: str = Field(..., description="Twitter username without @")
    display_name: str = Field(..., description="Display name of the user")
    follower_count: int = Field(..., description="Number of followers")
    following_count: int = Field(..., description="Number of users they follow")
    bio: str = Field(default="", description="User bio/description")
    verified: bool = Field(default=False, description="Whether the user is verified")


class TwitterFollowersList(BaseModel):
    """Pydantic model for a list of Twitter followers."""
    followers: List[TwitterUser] = Field(..., description="List of Twitter followers")


class TwitterFollowersScraper:
    """A class to handle Twitter followers scraping using Stagehand."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the Stagehand scraper."""
        self.model_name = model_name
        self.stagehand = None
        self.session_id = None
        self.is_logged_in = False
        
    async def initialize(self) -> bool:
        """Initialize Stagehand with Browserbase configuration."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Get credentials from environment
            browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
            browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
            model_api_key = os.getenv("MODEL_API_KEY")
            
            if not all([browserbase_api_key, browserbase_project_id, model_api_key]):
                print("❌ Missing required environment variables:")
                print("   - BROWSERBASE_API_KEY")
                print("   - BROWSERBASE_PROJECT_ID") 
                print("   - MODEL_API_KEY")
                print("\n💡 Please check your .env file and ensure all credentials are set.")
                return False
            
            # Create Stagehand configuration
            config = StagehandConfig(
                env="BROWSERBASE",
                api_key=browserbase_api_key,
                project_id=browserbase_project_id,
                model_name=self.model_name,
                model_api_key=model_api_key,
            )
            
            # Initialize Stagehand
            self.stagehand = Stagehand(config)
            await self.stagehand.init()
            
            self.session_id = getattr(self.stagehand, 'session_id', None)
            if self.session_id:
                print(f"🌐 View your live browser: https://www.browserbase.com/sessions/{self.session_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Stagehand: {e}")
            return False
    
    async def login_to_twitter(self) -> bool:
        """
        Login to Twitter using provided credentials.
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.stagehand:
            print("❌ Stagehand not initialized. Call initialize() first.")
            return False
        
        page = self.stagehand.page
        
        try:
            print("🔐 Logging into Twitter...")
            
            # Navigate to Twitter login page
            await page.goto("https://twitter.com/login")
            await asyncio.sleep(3)
            
            # Check if already logged in
            current_url = page.url
            if "home" in current_url or "twitter.com" in current_url and "login" not in current_url:
                print("✅ Already logged into Twitter")
                self.is_logged_in = True
                return True
            
            # Get Twitter credentials from environment
            twitter_username = os.getenv("TWITTER_USERNAME")
            twitter_password = os.getenv("TWITTER_PASSWORD")
            
            if not twitter_username or not twitter_password:
                print("❌ Missing Twitter credentials:")
                print("   - TWITTER_USERNAME")
                print("   - TWITTER_PASSWORD")
                print("\n💡 Please add your Twitter credentials to your .env file.")
                print("   Note: This is required to access follower lists.")
                return False
            
            # Fill in username
            print("📝 Entering username...")
            await page.act(f"enter '{twitter_username}' in the username field")
            await asyncio.sleep(1)
            
            # Click Next button
            await page.act("click the Next button")
            await asyncio.sleep(2)
            
            # Fill in password
            print("🔑 Entering password...")
            await page.act(f"enter '{twitter_password}' in the password field")
            await asyncio.sleep(1)
            
            # Click Login button
            await page.act("click the Log in button")
            await asyncio.sleep(5)
            
            # Check if login was successful
            current_url = page.url
            if "home" in current_url or "twitter.com" in current_url and "login" not in current_url:
                print("✅ Successfully logged into Twitter")
                self.is_logged_in = True
                return True
            else:
                print("❌ Login failed. Please check your credentials.")
                return False
                
        except Exception as e:
            print(f"❌ Error during Twitter login: {e}")
            return False
    
    async def scrape_followers(self, target_username: str, max_followers: Optional[int] = None) -> List[TwitterUser]:
        """
        Scrape followers from a Twitter profile using Stagehand.
        
        Args:
            target_username: Twitter username to scrape followers from (without @)
            max_followers: Maximum number of followers to scrape (None for all)
            
        Returns:
            List of TwitterUser objects containing follower information
        """
        if not self.stagehand:
            print("❌ Stagehand not initialized. Call initialize() first.")
            return []
        
        # Ensure we're logged in before attempting to scrape
        if not self.is_logged_in:
            print("🔐 Twitter login required to access follower lists...")
            if not await self.login_to_twitter():
                print("❌ Cannot proceed without Twitter login")
                return []
        
        followers = []
        page = self.stagehand.page
        
        try:
            print(f"🔍 Navigating to @{target_username}'s Twitter profile...")
            
            # Navigate to the Twitter profile
            await page.goto(f"https://twitter.com/{target_username}")
            
            # Wait for the page to load
            await asyncio.sleep(3)
            
            # Check if the profile exists and is accessible
            profile_check = await page.observe("check if this is a valid Twitter profile page")
            profile_check_str = str(profile_check).lower()
            if "error" in profile_check_str or "not found" in profile_check_str:
                print(f"❌ Profile @{target_username} not found or not accessible")
                return []
            
            print(f"✅ Successfully loaded @{target_username}'s profile")
            
            # Navigate to followers page
            print("📋 Navigating to followers page...")
            await page.act("click on the 'Followers' link or button")
            await asyncio.sleep(3)
            
            # Check if we can access the followers page
            followers_check = await page.observe("check if we can see the followers list")
            followers_check_str = str(followers_check).lower()
            if "login" in followers_check_str or "sign in" in followers_check_str or "not available" in followers_check_str:
                print("❌ Cannot access followers list. This may be due to:")
                print("   • Account privacy settings")
                print("   • Twitter's anti-bot measures")
                print("   • Login session expired")
                return []
            
            print("✅ Successfully accessed followers page")
            
            # Scroll and collect followers
            print("🔄 Scrolling through followers and extracting data...")
            scroll_count = 0
            max_scrolls = 50  # Prevent infinite scrolling
            
            while scroll_count < max_scrolls:
                # Extract visible followers using structured data extraction
                try:
                    followers_data = await page.extract(
                        "Extract all visible Twitter usernames, display names, follower counts, following counts, bios, and verification status from the followers list",
                        schema=TwitterFollowersList
                    )
                    
                    if followers_data and hasattr(followers_data, 'followers') and followers_data.followers:
                        # Add new followers (avoid duplicates)
                        existing_usernames = {f.username for f in followers}
                        new_followers = [f for f in followers_data.followers if f.username not in existing_usernames]
                        followers.extend(new_followers)
                        
                        print(f"📊 Collected {len(followers)} unique followers so far...")
                        
                        # Check if we've reached the maximum
                        if max_followers and len(followers) >= max_followers:
                            followers = followers[:max_followers]
                            print(f"🛑 Reached maximum of {max_followers} followers")
                            break
                    
                except Exception as e:
                    print(f"⚠️  Error extracting followers data: {e}")
                
                # Scroll down to load more followers
                try:
                    await page.act("scroll down to load more followers")
                    await asyncio.sleep(2)
                    scroll_count += 1
                except Exception as e:
                    print(f"⚠️  Error scrolling: {e}")
                    break
                
                # Check if we've reached the end of the followers list
                end_check = await page.observe("check if we've reached the end of the followers list")
                end_check_str = str(end_check).lower()
                if "end" in end_check_str or "no more" in end_check_str:
                    print("🏁 Reached the end of the followers list")
                    break
            
            # Sort followers by follower count (descending)
            followers.sort(key=lambda x: x.follower_count, reverse=True)
            
            print(f"✅ Successfully scraped {len(followers)} followers")
            return followers
            
        except Exception as e:
            print(f"❌ Error scraping followers: {e}")
            return followers
    
    async def save_results(self, followers: List[TwitterUser], target_username: str, output_format: str = 'both') -> None:
        """
        Save the scraped followers to file(s).
        
        Args:
            followers: List of TwitterUser objects
            target_username: Target Twitter username
            output_format: 'txt', 'json', or 'both'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format in ['txt', 'both']:
            txt_filename = f"scraped_followers_{target_username}_{timestamp}.txt"
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(f"Scraped Followers of @{target_username}\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total followers: {len(followers)}\n")
                f.write("-" * 80 + "\n\n")
                
                for i, user in enumerate(followers, 1):
                    verified_mark = "✓" if user.verified else ""
                    f.write(f"{i:4d}. @{user.username:<20} {verified_mark}\n")
                    f.write(f"     Name: {user.display_name}\n")
                    f.write(f"     Followers: {user.follower_count:,} | Following: {user.following_count:,}\n")
                    if user.bio:
                        f.write(f"     Bio: {user.bio[:100]}{'...' if len(user.bio) > 100 else ''}\n")
                    f.write("\n")
            
            print(f"✓ Results saved to {txt_filename}")
        
        if output_format in ['json', 'both']:
            json_filename = f"scraped_followers_{target_username}_{timestamp}.json"
            data = {
                'target_username': target_username,
                'generated_at': datetime.now().isoformat(),
                'total_followers': len(followers),
                'followers': [
                    {
                        'username': user.username,
                        'display_name': user.display_name,
                        'follower_count': user.follower_count,
                        'following_count': user.following_count,
                        'bio': user.bio,
                        'verified': user.verified,
                        'rank': i+1
                    }
                    for i, user in enumerate(followers)
                ]
            }
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Results saved to {json_filename}")
    
    def print_top_followers(self, followers: List[TwitterUser], top_n: int = 20) -> None:
        """
        Print the top N followers by follower count.
        
        Args:
            followers: List of TwitterUser objects
            top_n: Number of top followers to display
        """
        print(f"\n🏆 Top {min(top_n, len(followers))} followers by follower count:")
        print("-" * 80)
        
        for i, user in enumerate(followers[:top_n], 1):
            verified_mark = "✓" if user.verified else ""
            print(f"{i:2d}. @{user.username:<20} {verified_mark}")
            print(f"    {user.display_name}")
            print(f"    Followers: {user.follower_count:,} | Following: {user.following_count:,}")
            if user.bio:
                bio_preview = user.bio[:60] + "..." if len(user.bio) > 60 else user.bio
                print(f"    Bio: {bio_preview}")
            print()
    
    async def close(self) -> None:
        """Close the Stagehand session."""
        if self.stagehand:
            print("\n🤘 Closing Stagehand...")
            await self.stagehand.close()


async def main():
    """Main function to run the Twitter followers scraper."""
    print("🤖 Twitter Followers Scraper using Stagehand")
    print("=" * 60)
    
    try:
        # Get target username from user input
        target_username = input("Enter Twitter username to scrape followers from (without @): ").strip()
        if not target_username:
            print("❌ Error: Username cannot be empty")
            return
        
        # Validate username format
        if target_username.startswith('@'):
            target_username = target_username[1:]
            print(f"ℹ️  Removed @ symbol. Using: {target_username}")
        
        # Get maximum followers limit
        max_followers_input = input("Enter maximum number of followers to scrape (press Enter for all): ").strip()
        max_followers = None
        if max_followers_input:
            try:
                max_followers = int(max_followers_input)
                if max_followers <= 0:
                    print("❌ Error: Maximum followers must be a positive number")
                    return
                if max_followers > 1000:
                    print("⚠️  Warning: Large follower counts may take a long time")
            except ValueError:
                print("❌ Error: Please enter a valid number")
                return
        
        # Get output format preference
        output_format = input("Output format (txt/json/both) [both]: ").strip().lower()
        if output_format not in ['txt', 'json', 'both']:
            output_format = 'both'
            print("ℹ️  Using default format: both")
        
        # Initialize the scraper
        print("\n🔧 Initializing Stagehand...")
        scraper = TwitterFollowersScraper()
        
        if not await scraper.initialize():
            print("❌ Failed to initialize Stagehand. Please check your credentials.")
            return
        
        # Scrape followers
        print(f"\n🕷️  Starting to scrape followers from @{target_username}...")
        followers = await scraper.scrape_followers(target_username, max_followers)
        
        if not followers:
            print("\n❌ No followers found or error occurred.")
            print("\n💡 Possible reasons:")
            print("• User has no followers")
            print("• Profile is private or protected")
            print("• Twitter's anti-bot measures")
            print("• Network or authentication issues")
            print("• Missing Twitter login credentials")
            return
        
        # Display top followers
        scraper.print_top_followers(followers)
        
        # Save results
        print(f"\n💾 Saving results...")
        await scraper.save_results(followers, target_username, output_format)
        
        print(f"\n✅ Successfully scraped {len(followers)} followers!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\n🔧 General troubleshooting:")
        print("• Check your internet connection")
        print("• Verify your .env file has correct credentials")
        print("• Ensure Browserbase account is active")
        print("• Verify Twitter login credentials")
        print("• Try running the script again")
    finally:
        # Clean up
        if 'scraper' in locals():
            await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
