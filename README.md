# Twitter Utils

A collection of Python utility scripts for Twitter/X API operations. This repository provides various tools for analyzing and working with Twitter data using the X API v2.

## Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd twitter-utils
./setup.sh

# 2. Configure your API credentials
cp env.example .env
# Edit .env with your Twitter API credentials

# 3. Run a utility
python main.py help                    # See available utilities
python main.py fetch_followers         # Run fetch followers utility
```

**⚠️ Note:** The fetch followers utility requires Enterprise access (paid tier) to the Twitter API.

## Available Utilities

### 🐦 Fetch Followers (`fetch_followers`)
Fetches a list of Twitter followers and sorts them by follower count.

**⚠️ Important Note:** This utility requires **Enterprise access** (paid tier) to the Twitter API. The free Essential/Elevated tiers do not include access to follower data.

**Features:**
- 🔐 Secure authentication using environment variables
- 📊 Fetches followers with their follower counts
- 🏆 Sorts followers by follower count (highest first)
- 💾 Saves results in both TXT and JSON formats
- ⚡ Built-in rate limiting to respect Twitter API limits
- 🎯 Progress tracking and error handling
- 🔧 Configurable maximum follower limit

## Repository Structure

```
twitter-utils/
├── main.py                 # Main launcher script
├── fetch_followers.py      # Fetch followers utility script
├── lib/                    # Shared library code
│   ├── __init__.py        # Package initialization
│   └── twitter_client.py   # Common Twitter API functionality
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── setup.sh              # Automated setup script
└── README.md             # This file
```

### Shared Library

The `lib/` directory contains shared functionality used across multiple utilities:

- **`twitter_client.py`** - Common Twitter API operations including:
  - Authentication (Bearer Token and OAuth 2.0 PKCE)
  - Error handling for API responses
  - Rate limiting and retry logic
  - User lookup and data fetching utilities

This shared approach ensures:
- Consistent authentication across all utilities
- Centralized error handling and user feedback
- Easy maintenance and updates
- Code reusability for future utilities

## Prerequisites

1. **Python 3.6+** installed on your system
2. **Twitter Developer Account** with API access
3. **Twitter API credentials** (Bearer Token, Client ID, Client Secret)

## Setup

### Option 1: Quick Setup (Recommended)

Run the automated setup script:

```bash
git clone <repository-url>
cd twitter-utils
./setup.sh
```

This script will:
- Create a Python virtual environment
- Install all dependencies
- Create a `.env` file from the template
- Verify Python version compatibility

### Option 2: Manual Setup

#### 1. Clone or Download

```bash
git clone <repository-url>
cd twitter-utils
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 4. Get X API v2 Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a Twitter Developer Account (if you don't have one)
3. Create a new project and app
4. **Important**: Note that follower data requires Enterprise access (paid tier). The free Essential/Elevated tiers do not include access to follower data.

#### **Bearer Token (for basic operations)**
- Generate a Bearer Token from your app settings
- Used for basic read operations

#### **OAuth 2.0 PKCE (Required for followers)**

**Step 1: Complete the App Info Form**

When creating your app, you'll see an "App info" form. Fill it out as follows:

**Required Fields:**
- **Callback URI / Redirect URL**: `http://localhost:8080/callback`
- **Website URL**: `https://github.com/yourusername/twitter-utils` (or your project URL)

**Optional Fields (Recommended):**
- **Organization name**: `Twitter Utils` (or your name)
- **Organization URL**: Same as Website URL
- **Terms of Service**: Leave blank (optional)
- **Privacy Policy**: Leave blank (optional)

**Step 2: Generate OAuth 2.0 Credentials**

After saving the app info:
1. Navigate to your app's "Keys and Tokens" section
2. Look for "OAuth 2.0 Client ID and Client Secret"
3. Generate these credentials
4. Copy them to your `.env` file

**Important**: The followers endpoint specifically requires OAuth 2.0 PKCE authentication with the following scopes:
- `tweet.read`
- `users.read` 
- `follows.read`

### 5. Configure Environment Variables

Copy the example environment file and add your credentials:

```bash
cp env.example .env
```

Edit the `.env` file and add your actual Twitter API credentials:

```env
# Bearer Token (for basic operations)
TWITTER_BEARER_TOKEN=your_actual_bearer_token

# OAuth 2.0 PKCE (required for followers)
TWITTER_CLIENT_ID=your_actual_client_id
TWITTER_CLIENT_SECRET=your_actual_client_secret
```

**Important:** Never commit your `.env` file to version control!

## Usage

### Activate Virtual Environment

Before running any utility, make sure to activate the virtual environment:

```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Run Utilities

#### Using the Main Launcher (Recommended)

The main launcher provides a unified interface for all utilities:

```bash
# Show available utilities and help
python main.py help

# Run the fetch followers utility
python main.py fetch_followers

# Run without arguments (shows help)
python main.py
```

**Benefits of using the main launcher:**
- Unified command interface for all utilities
- Built-in help system to discover available tools
- Consistent error handling across all utilities
- Easy to add new utilities without changing user workflow

#### Running Utilities Directly

You can also run utility scripts directly:

```bash
# Run fetch followers directly
python fetch_followers.py
```

**When to use direct execution:**
- Quick testing or debugging
- When you know exactly which script you want to run
- For automation or scripting purposes

### Deactivate Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

### Fetch Followers Utility

The fetch followers utility will prompt you for:
1. **Twitter username** (without @) - the account whose followers you want to analyze
2. **Maximum followers** (optional) - limit the number of followers to fetch
3. **Output format** - choose between txt, json, or both

### Example Session

```
🐦 Twitter Followers Fetcher and Sorter
==================================================
Enter Twitter username (without @): elonmusk
Enter maximum number of followers to fetch (press Enter for all): 1000
Output format (txt/json/both) [both]: both
ℹ️  Using default format: both

🔧 Initializing Twitter API client...
✅ Successfully authenticated with X API v2 (Bearer Token)
ℹ️  Note: OAuth 2.0 PKCE will be used for follower data access
Fetching followers for @elonmusk...
🔐 Setting up OAuth 2.0 PKCE authentication for followers...
[OAuth flow continues...]
✅ Successfully fetched 1000 followers

🏆 Top 20 followers by follower count:
------------------------------------------------------------
 1. @SpaceX                    - 15,234,567 followers
 2. @Tesla                     - 12,345,678 followers
 3. @NASA                      - 8,765,432 followers
...
```

## Output Files

The script generates timestamped output files:

- **`followers_username_YYYYMMDD_HHMMSS.txt`** - Human-readable text format
- **`followers_username_YYYYMMDD_HHMMSS.json`** - Machine-readable JSON format

### Text Format Example

```
Followers of @elonmusk sorted by follower count
Generated on: 2024-01-15 14:30:25
Total followers: 1000
--------------------------------------------------

   1. @SpaceX                    - 15,234,567 followers
   2. @Tesla                     - 12,345,678 followers
   3. @NASA                      - 8,765,432 followers
   ...
```

### JSON Format Example

```json
{
  "screen_name": "elonmusk",
  "generated_at": "2024-01-15T14:30:25.123456",
  "total_followers": 1000,
  "followers": [
    {
      "username": "SpaceX",
      "follower_count": 15234567,
      "rank": 1
    },
    {
      "username": "Tesla",
      "follower_count": 12345678,
      "rank": 2
    }
  ]
}
```

## Rate Limiting

The script includes built-in rate limiting to respect Twitter's API limits:
- Automatic retry on rate limit exceeded
- Small delays between requests
- Progress indicators for long-running operations

## Error Handling

The script handles common errors gracefully:
- Missing or invalid API credentials
- Network connectivity issues
- Rate limit exceeded (automatic retry)
- Invalid usernames
- API errors

## Troubleshooting

### Common Issues

1. **"Missing Twitter API credentials"**
   - Make sure your `.env` file exists and contains all required variables
   - Verify your credentials are correct

2. **"Error authenticating with Twitter API"**
   - Check that your API credentials are valid
   - Ensure your Twitter Developer Account has the necessary permissions

3. **"Rate limit exceeded"**
   - The script will automatically wait and retry
   - Consider reducing the maximum followers limit

4. **"No followers found"**
   - Check that the username is correct
   - Verify the account is public
   - Ensure the account has followers

5. **"python: command not found" or "python3: command not found"**
   - Make sure Python 3.6+ is installed on your system
   - Try using `python3 main.py` instead of `python main.py`

6. **"403 Forbidden" or "Client Forbidden" or "client-not-enrolled"**
   - This means your Twitter API access level doesn't include follower data
   - The followers endpoint requires **Enterprise access** (paid tier)
   - Essential/Elevated access does NOT include follower data
   - You need to upgrade to Enterprise access or use alternative data sources
   - Reference: https://docs.x.com/x-api/users/follows/introduction

7. **"401 Unauthorized" when fetching followers**
   - This means your app doesn't have the required permissions for the followers endpoint
   - The followers endpoint requires **Enterprise access** (paid tier)
   - Check your app permissions in the [Developer Portal](https://developer.twitter.com/)
   - Ensure your app has "Read" permissions with `follows.read` scope
   - Essential/Elevated access does NOT include follower data access

8. **"OAuth 2.0 PKCE requires TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET"**
   - You need to complete the OAuth 2.0 setup in the Twitter Developer Portal
   - Follow the "OAuth 2.0 PKCE" instructions above
   - Make sure you've generated OAuth 2.0 credentials (not just Bearer Token)
   - Add the credentials to your `.env` file

9. **"Error: No authorization code found in redirect URL"**
   - Make sure you copied the **complete URL** from your browser after authorization
   - The URL should contain `?code=...` parameter
   - Don't just copy the domain, copy the entire URL including query parameters
   - If the redirect fails, try the authorization process again

10. **"Error during OAuth 2.0 PKCE flow"**
    - Check that your Callback URI in the app settings matches `http://localhost:8080/callback`
    - Verify your Client ID and Client Secret are correct
    - Ensure your app has the required scopes: `tweet.read`, `users.read`, `follows.read`
    - Try regenerating your OAuth 2.0 credentials

### Getting Help

If you encounter issues:
1. Check the error messages for specific guidance
2. Verify your Twitter API credentials
3. Ensure you have the necessary permissions
4. Check Twitter's API status page for outages

## Virtual Environment Benefits

Using a virtual environment provides several advantages:

- **Isolation**: Dependencies are isolated from your system Python
- **Reproducibility**: Ensures consistent package versions across different environments
- **Clean System**: Prevents conflicts with other Python projects
- **Easy Cleanup**: Simply delete the `venv` folder to remove all dependencies
- **Security**: Prevents system-wide package conflicts and security issues

## Security Notes

- Never share your API credentials
- Keep your `.env` file secure and never commit it to version control
- Use environment variables in production environments
- Regularly rotate your API keys
- The `.gitignore` file excludes sensitive files and virtual environment

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Adding New Utilities

To add a new utility script to this repository:

1. **Create the script** in the root directory (e.g., `analyze_tweets.py`)
2. **Use the shared library** by importing from `lib.twitter_client`
3. **Add to main launcher** by updating `main.py`:
   - Add import: `from your_script import main as your_script_main`
   - Add function: `def run_your_script(): your_script_main()`
   - Add to utilities dict: `'your_script': run_your_script`
4. **Update documentation** in this README.md
5. **Test thoroughly** with various scenarios

### Example New Utility Structure

```python
#!/usr/bin/env python3
"""
Your New Utility Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.twitter_client import TwitterAPIClient

def main():
    """Main function for your utility."""
    # Your utility logic here
    pass

if __name__ == "__main__":
    main()
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Include error handling and user feedback
- Test with both success and error scenarios
