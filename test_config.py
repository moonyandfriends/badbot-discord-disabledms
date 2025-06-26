#!/usr/bin/env python3
"""
Configuration Test Script

This script helps verify that your Discord bot configuration is correct
before running the main DM disabler script.

Usage: python test_config.py
"""

import os
import sys
from typing import List, Dict

from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


def test_bot_token() -> bool:
    """Test if the bot token is valid by making a simple API call."""
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not bot_token:
        print("❌ DISCORD_BOT_TOKEN is not set")
        return False
    
    if bot_token == 'your_bot_token_here':
        print("❌ DISCORD_BOT_TOKEN is still set to the example value")
        return False
    
    # Test the bot token by getting bot information
    headers = {
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot token is valid - Bot: {bot_info.get('username', 'Unknown')}#{bot_info.get('discriminator', '0000')}")
            return True
        else:
            print(f"❌ Bot token is invalid - Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test bot token: {str(e)}")
        return False


def test_webhook_url() -> bool:
    """Test if the webhook URL is valid."""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL is not set")
        return False
    
    if webhook_url == 'your_webhook_url_here':
        print("❌ DISCORD_WEBHOOK_URL is still set to the example value")
        return False
    
    # Test the webhook by sending a test message
    test_data = {
        "content": "🔧 Configuration test - If you see this message, your webhook is working correctly!",
        "embeds": [{
            "title": "Configuration Test",
            "description": "This is a test message to verify your webhook configuration.",
            "color": 0x00ff00,
            "footer": {"text": "Discord DM Disabler - Test"}
        }]
    }
    
    try:
        response = requests.post(webhook_url, json=test_data, timeout=10)
        
        if response.status_code in [200, 204]:
            print("✅ Webhook URL is valid - Test message sent successfully")
            return True
        else:
            print(f"❌ Webhook URL is invalid - Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test webhook URL: {str(e)}")
        return False


def test_server_configuration() -> bool:
    """Test if server configuration is properly set up."""
    servers = []
    
    # First, try to load from single SERVERS variable
    servers_var = os.getenv('SERVERS')
    if servers_var:
        if servers_var == 'guild_id1:name1,guild_id2:name2,guild_id3:name3':
            print("❌ SERVERS is still set to the example value")
            return False
            
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
            print(f"✅ Found {len(servers)} server(s) configured in SERVERS variable:")
            for i, server in enumerate(servers, 1):
                print(f"   {i}. {server['name']} (ID: {server['guild_id']})")
            return True
    
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
    
    if not servers:
        print("❌ No servers configured. Please set either SERVERS or SERVER_1, SERVER_2, etc. environment variables.")
        return False
    
    print(f"✅ Found {len(servers)} server(s) configured in SERVER_N variables:")
    for i, server in enumerate(servers, 1):
        print(f"   {i}. {server['name']} (ID: {server['guild_id']})")
    
    return True


def main():
    """Run all configuration tests."""
    print("🔧 Discord DM Disabler - Configuration Test")
    print("=" * 50)
    
    tests = [
        ("Bot Token", test_bot_token),
        ("Webhook URL", test_webhook_url),
        ("Server Configuration", test_server_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your configuration is ready.")
        print("You can now run: python main.py")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the main script.")
        sys.exit(1)


if __name__ == "__main__":
    main() 