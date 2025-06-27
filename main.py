#!/usr/bin/env python3
"""
Discord Server DM Disabler

This script disables DMs for multiple Discord servers for 24 hours.
It processes servers sequentially with delays and sends webhook notifications
about the success/failure of each operation.

Author: Discord DM Disabler Bot
Version: 1.0.0
"""

import asyncio
import datetime
from datetime import timezone
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('discord_dm_disabler.log')
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_DISABLE_HOURS = 24
DELAY_BETWEEN_SERVERS = 10  # seconds
DISCORD_API_BASE_URL = "https://discord.com/api/v9"


class DiscordDMDisabler:
    """Handles disabling DMs for Discord servers."""
    
    def __init__(self, bot_token: str, webhook_url: str):
        """
        Initialize the Discord DM Disabler.
        
        Args:
            bot_token: Discord bot token for authentication
            webhook_url: Discord webhook URL for notifications
        """
        self.bot_token = bot_token
        self.webhook_url = webhook_url
        self.headers = {
            'Authorization': f'Bot {bot_token}',
            'Content-Type': 'application/json'
        }
        
    def get_disable_until_timestamp(self, hours: int = DEFAULT_DISABLE_HOURS) -> str:
        """
        Calculate the timestamp for when DMs should be re-enabled.
        
        Args:
            hours: Number of hours to disable DMs for
            
        Returns:
            ISO 8601 formatted timestamp
        """
        now = datetime.datetime.now(timezone.utc)
        disable_until = now + datetime.timedelta(hours=hours)
        return disable_until.isoformat()
    
    def disable_dms_for_server(self, guild_id: str, server_name: str = "Unknown") -> Dict[str, Any]:
        """
        Disable DMs for a specific Discord server.
        
        Args:
            guild_id: Discord guild/server ID
            server_name: Human-readable server name for logging
            
        Returns:
            Dictionary containing success status and response details
        """
        try:
            url = f'{DISCORD_API_BASE_URL}/guilds/{guild_id}/incident-actions'
            payload = {
                'dms_disabled_until': self.get_disable_until_timestamp()
            }
            
            logger.info(f"Attempting to disable DMs for server: {server_name} ({guild_id})")
            
            response = requests.put(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Successfully disabled DMs for server: {server_name}")
                return {
                    'success': True,
                    'server_name': server_name,
                    'guild_id': guild_id,
                    'status_code': response.status_code,
                    'message': 'DMs disabled successfully'
                }
            else:
                error_msg = f"Failed to disable DMs for server: {server_name}"
                logger.error(f"{error_msg} - Status: {response.status_code}")
                
                try:
                    error_details = response.json()
                    logger.error(f"Error details: {error_details}")
                except json.JSONDecodeError:
                    logger.error(f"Raw response: {response.text}")
                
                return {
                    'success': False,
                    'server_name': server_name,
                    'guild_id': guild_id,
                    'status_code': response.status_code,
                    'message': f'Failed with status {response.status_code}',
                    'error_details': response.text if response.text else 'No error details'
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed for server {server_name}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'server_name': server_name,
                'guild_id': guild_id,
                'status_code': None,
                'message': f'Request failed: {str(e)}'
            }
    
    def send_webhook_notification(self, result: Dict[str, Any]) -> bool:
        """
        Send webhook notification about the DM disable operation result.
        
        Args:
            result: Dictionary containing operation result details
            
        Returns:
            True if webhook was sent successfully, False otherwise
        """
        try:
            server_name = result.get('server_name', 'Unknown Server')
            success = result.get('success', False)
            status_code = result.get('status_code')
            message = result.get('message', 'No message')
            
            # Create embed for Discord webhook
            color = 0x00ff00 if success else 0xff0000  # Green for success, red for failure
            status_text = "✅ SUCCESS" if success else "❌ FAILED"
            
            embed = {
                "title": f"Discord DM Disable Operation - {status_text}",
                "description": f"**Server:** {server_name}\n**Guild ID:** `{result.get('guild_id', 'Unknown')}`",
                "color": color,
                "fields": [
                    {
                        "name": "Status",
                        "value": message,
                        "inline": True
                    },
                    {
                        "name": "Status Code",
                        "value": str(status_code) if status_code else "N/A",
                        "inline": True
                    },
                    {
                        "name": "Timestamp",
                        "value": datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Discord DM Disabler Bot"
                }
            }
            
            webhook_data = {
                "embeds": [embed]
            }
            
            response = requests.post(self.webhook_url, json=webhook_data, timeout=30)
            
            if response.status_code in [200, 204]:
                logger.info(f"Webhook notification sent successfully for {server_name}")
                return True
            else:
                logger.error(f"Failed to send webhook notification: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
            return False
    
    def process_servers(self, servers: List[Dict[str, str]]) -> None:
        """
        Process multiple servers sequentially with delays and notifications.
        
        Args:
            servers: List of server dictionaries with 'guild_id' and 'name' keys
        """
        logger.info(f"Starting DM disable operation for {len(servers)} servers")
        
        for i, server in enumerate(servers, 1):
            guild_id = server.get('guild_id')
            server_name = server.get('name', f'Server {i}')
            
            if not guild_id:
                logger.error(f"Missing guild_id for server {server_name}")
                continue
            
            logger.info(f"Processing server {i}/{len(servers)}: {server_name}")
            
            # Disable DMs for the server
            result = self.disable_dms_for_server(guild_id, server_name)
            
            # Send webhook notification
            webhook_sent = self.send_webhook_notification(result)
            
            if not webhook_sent:
                logger.warning(f"Failed to send webhook notification for {server_name}")
            
            # Wait before processing next server (except for the last one)
            if i < len(servers):
                logger.info(f"Waiting {DELAY_BETWEEN_SERVERS} seconds before next server...")
                asyncio.run(asyncio.sleep(DELAY_BETWEEN_SERVERS))
        
        logger.info("All servers processed successfully")


def load_servers_from_env() -> List[Dict[str, str]]:
    """
    Load server configuration from environment variables.
    
    Supports two formats:
    1. Single SERVERS variable: SERVERS=guild_id1:name1,guild_id2:name2,guild_id3:name3
    2. Individual SERVER_N variables: SERVER_1=guild_id:name,SERVER_2=guild_id:name
    
    Returns:
        List of server dictionaries
    """
    servers = []
    
    # First, try to load from single SERVERS variable
    servers_var = os.getenv('SERVERS')
    if servers_var:
        # Parse format: guild_id1:name1,guild_id2:name2,guild_id3:name3
        server_entries = servers_var.split(',')
        for entry in server_entries:
            entry = entry.strip()
            if not entry:
                continue
                
            # Parse format: guild_id:server_name
            if ':' in entry:
                guild_id, server_name = entry.split(':', 1)
                servers.append({
                    'guild_id': guild_id.strip(),
                    'name': server_name.strip()
                })
            else:
                # If no name provided, use guild_id as name
                servers.append({
                    'guild_id': entry.strip(),
                    'name': f'Server {len(servers) + 1}'
                })
        
        if servers:
            logger.info(f"Loaded {len(servers)} servers from SERVERS variable")
            return servers
    
    # Fallback to individual SERVER_N variables
    i = 1
    while True:
        server_var = os.getenv(f'SERVER_{i}')
        if not server_var:
            break
            
        # Parse format: guild_id:server_name
        if ':' in server_var:
            guild_id, server_name = server_var.split(':', 1)
            servers.append({
                'guild_id': guild_id.strip(),
                'name': server_name.strip()
            })
        else:
            # If no name provided, use guild_id as name
            servers.append({
                'guild_id': server_var.strip(),
                'name': f'Server {i}'
            })
        
        i += 1
    
    if servers:
        logger.info(f"Loaded {len(servers)} servers from SERVER_N variables")
    
    return servers


def validate_environment() -> bool:
    """
    Validate that all required environment variables are set.
    
    Returns:
        True if all required variables are present, False otherwise
    """
    required_vars = ['badbot_discord_token', 'badbot_logs_webhookurl']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True


def main():
    """Main function to run the Discord DM disabler."""
    logger.info("Starting Discord DM Disabler")
    
    try:
        # Validate environment
        if not validate_environment():
            logger.error("Environment validation failed. Exiting.")
            sys.exit(1)
        
        # Load configuration
        bot_token = os.getenv('badbot_discord_token')
        webhook_url = os.getenv('badbot_logs_webhookurl')
        
        # Type checking for required environment variables
        if not bot_token or not webhook_url:
            logger.error("Required environment variables are missing or empty.")
            sys.exit(1)
        
        servers = load_servers_from_env()
        
        if not servers:
            logger.error("No servers configured. Please set either SERVERS or SERVER_1, SERVER_2, etc. environment variables.")
            sys.exit(1)
        
        logger.info(f"Loaded {len(servers)} servers for processing")
        
        # Initialize disabler
        disabler = DiscordDMDisabler(bot_token, webhook_url)
        
        # Process all servers
        disabler.process_servers(servers)
        logger.info("Discord DM Disabler completed successfully")
        
    except Exception as e:
        logger.error(f"Unexpected error during execution: {str(e)}")
        sys.exit(1)
    finally:
        # Ensure clean exit
        logger.info("Script execution finished. Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    main() 