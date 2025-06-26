# Discord Server DM Disabler

A Python script that disables Direct Messages (DMs) for multiple Discord servers for 24 hours. The script processes servers sequentially with delays and sends webhook notifications about the success/failure of each operation.

## Features

- ✅ Disables DMs for multiple Discord servers for 24 hours
- ✅ Processes servers sequentially with configurable delays
- ✅ Sends detailed webhook notifications for each operation
- ✅ Comprehensive logging and error handling
- ✅ Railway deployment ready
- ✅ Environment variable configuration
- ✅ Type-safe Python code with proper annotations

## Prerequisites

- Python 3.8+
- Discord Bot Token with appropriate permissions
- Discord Webhook URL for notifications
- Railway account (for deployment)

## Discord Bot Setup

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a bot for your application
3. Copy the bot token
4. Invite the bot to your servers with the following permissions:
   - `Manage Guild` (to modify server settings)
   - `Send Messages` (for webhook notifications)

## Environment Variables

The following environment variables are required:

### Required Variables

- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `DISCORD_WEBHOOK_URL`: Discord webhook URL for notifications

### Server Configuration

You can configure servers using either of these two formats:

#### Option 1: Single SERVERS Variable (Recommended for Multiple Servers)

```
SERVERS=guild_id1:name1,guild_id2:name2,guild_id3:name3
```

**Examples:**
```
SERVERS=988945059783278602:My Gaming Server,123456789012345678:Community Hub,876543210987654321:Test Server
```

#### Option 2: Individual SERVER_N Variables

```
SERVER_1=guild_id:server_name
SERVER_2=guild_id:server_name
SERVER_3=guild_id:server_name
```

**Examples:**
```
SERVER_1=988945059783278602:My Gaming Server
SERVER_2=123456789012345678:Community Hub
SERVER_3=876543210987654321:Test Server
```

**Note:** 
- If you don't provide a server name, it will default to "Server 1", "Server 2", etc.
- The `SERVERS` variable takes precedence over `SERVER_N` variables if both are set.
- For 10+ servers, the single `SERVERS` variable is much more convenient to manage.

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/badbot-discord-disabledms.git
cd badbot-discord-disabledms
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```env
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_WEBHOOK_URL=your_webhook_url_here
SERVER_1=988945059783278602:My Gaming Server
SERVER_2=123456789012345678:Community Hub
```

4. Run the script:
```bash
python main.py
```

## Railway Deployment

### Automatic Deployment

1. Fork this repository to your GitHub account
2. Connect your Railway account to GitHub
3. Create a new Railway project from your GitHub repository
4. Add the required environment variables in Railway dashboard:
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_WEBHOOK_URL`
   - `SERVERS` (recommended) or `SERVER_1`, `SERVER_2`, etc.

### Manual Deployment

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Initialize and deploy:
```bash
railway init
railway up
```

4. Set environment variables:
```bash
railway variables set DISCORD_BOT_TOKEN=your_bot_token
railway variables set DISCORD_WEBHOOK_URL=your_webhook_url
railway variables set SERVERS=988945059783278602:My Gaming Server,123456789012345678:Community Hub
```

## Usage as Cron Job

Since this script is designed to run once and terminate, it's perfect for Railway's cron job functionality:

1. Deploy the application to Railway
2. In Railway dashboard, go to your project settings
3. Add a cron job with your desired schedule (e.g., daily at 2 AM UTC):
```
0 2 * * *
```

## How It Works

1. **Initialization**: The script validates environment variables and loads server configuration
2. **Sequential Processing**: For each server:
   - Disables DMs for 24 hours using Discord's API
   - Sends a webhook notification with the result
   - Waits 10 seconds before processing the next server
3. **Completion**: The script terminates after processing all servers

## Webhook Notifications

The script sends detailed Discord webhook notifications for each operation:

- **Success**: Green embed with server details and success message
- **Failure**: Red embed with error details and status code

Each notification includes:
- Server name and Guild ID
- Operation status (Success/Failed)
- Status code from Discord API
- Timestamp of the operation

## Logging

The script provides comprehensive logging:
- Console output for real-time monitoring
- Log file (`discord_dm_disabler.log`) for persistent records
- Different log levels (INFO, WARNING, ERROR)

## Error Handling

The script includes robust error handling:
- Network request timeouts (30 seconds)
- Invalid server configurations
- Missing environment variables
- Discord API errors
- Webhook notification failures

## Configuration Options

You can modify the following constants in `main.py`:

- `DEFAULT_DISABLE_HOURS`: Duration to disable DMs (default: 24 hours)
- `DELAY_BETWEEN_SERVERS`: Delay between processing servers (default: 10 seconds)
- `DISCORD_API_BASE_URL`: Discord API base URL (default: v9)

## Security Considerations

- Never commit your bot token or webhook URL to version control
- Use environment variables for all sensitive configuration
- Regularly rotate your bot token
- Monitor webhook notifications for unauthorized access attempts

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure all required environment variables are set
   - Check for typos in variable names

2. **"Failed to disable DMs"**
   - Verify bot has `Manage Guild` permission
   - Check if bot is in the target server
   - Ensure guild ID is correct

3. **"Failed to send webhook notification"**
   - Verify webhook URL is correct and active
   - Check webhook permissions

4. **Script exits immediately**
   - Check logs for error messages
   - Verify server configuration format

### Debug Mode

To enable debug logging, modify the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue on GitHub with detailed information

## Changelog

### Version 1.0.0
- Initial release
- Multi-server DM disabling functionality
- Webhook notifications
- Railway deployment support
- Comprehensive error handling and logging
