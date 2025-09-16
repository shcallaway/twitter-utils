# Twitter Followers Fetcher and Sorter

A Python script (`main.py`) that fetches your Twitter followers and sorts them by follower count using the X API v2.

## Features

- 🔐 Secure authentication using environment variables
- 📊 Fetches followers with their follower counts
- 🏆 Sorts followers by follower count (highest first)
- 💾 Saves results in both TXT and JSON formats
- ⚡ Built-in rate limiting to respect Twitter API limits
- 🎯 Progress tracking and error handling
- 🔧 Configurable maximum follower limit

## Prerequisites

1. **Python 3.6+** installed on your system
2. **Twitter Developer Account** with API access
3. **Twitter API credentials** (Consumer Key, Consumer Secret, Access Token, Access Token Secret)

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
4. **Important**: Request access to the "Read" permission level, which includes access to follower data

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
- **Organization name**: `Twitter Followers Fetcher` (or your name)
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

Before running the script, make sure to activate the virtual environment:

```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Run the Script

```bash
python main.py
```

### Deactivate Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

The script will prompt you for:
1. **Twitter username** (without @) - the account whose followers you want to analyze
2. **Maximum followers** (optional) - limit the number of followers to fetch
3. **Output format** - choose between txt, json, or both

### Example Session

```
🐦 Twitter Followers Fetcher and Sorter
==================================================
✓ Successfully authenticated with Twitter API
Enter Twitter username (without @): elonmusk
Enter maximum number of followers to fetch (press Enter for all): 1000
Output format (txt/json/both) [both]: both

Fetching followers for @elonmusk...
Fetched 100 followers...
Fetched 200 followers...
...
Successfully fetched 1000 followers

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

6. **"403 Forbidden" or "You currently have access to a subset of X API V2 endpoints"**
   - This means your Twitter API access level doesn't include follower data
   - Apply for elevated access at [Twitter Developer Portal](https://developer.twitter.com/)
   - You may need to upgrade to a paid plan for follower data access
   - The free tier typically only includes basic read access

7. **"401 Unauthorized" when fetching followers**
   - This means your app doesn't have the required permissions for the followers endpoint
   - The followers endpoint requires **elevated access** or **paid plan**
   - Check your app permissions in the [Developer Portal](https://developer.twitter.com/)
   - Ensure your app has "Read" permissions with `follows.read` scope
   - You may need to apply for elevated access or upgrade to a paid plan
   - The free Essential tier may not include follower data access

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

## Security Notes

- Never share your API credentials
- Keep your `.env` file secure and never commit it to version control
- Use environment variables in production environments
- Regularly rotate your API keys
- The `.gitignore` file excludes sensitive files and virtual environment

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
