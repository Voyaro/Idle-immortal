# Cultivation Discord Bot

## Overview

This is a Discord bot that implements a cultivation/martial arts RPG game system. Players can create characters, cultivate their power, engage in PvP battles, complete dungeons, and learn cultivation techniques. The bot uses a JSON-based data persistence system with automatic backups and includes a keep-alive mechanism for continuous operation on Replit.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py**: Uses the discord.py library with the commands extension for creating slash commands and handling Discord interactions
- **Asynchronous Design**: Built on asyncio for handling multiple concurrent user interactions without blocking

### Data Persistence
- **JSON File Storage**: Player data, server statistics, and game state are stored in `data.json`
- **Automatic Backup System**: Creates timestamped backup files in the `backups/` directory to prevent data loss
- **In-Memory Caching**: Active game sessions (cultivation, battles) are stored in global dictionaries for performance

### Game State Management
- **Player Profiles**: Each player has a comprehensive profile including realm, stage, experience, qi, spirit stones, equipment, techniques, and combat statistics
- **Progression System**: Players advance through cultivation realms and stages by gaining experience and qi
- **Equipment and Techniques**: System for managing player equipment and learned cultivation techniques
- **PvP and Dungeon Systems**: Separate systems for player vs player combat and dungeon exploration

### Server Infrastructure
- **Keep-Alive System**: Flask web server runs alongside the bot to maintain uptime on Replit
- **Auto-Ping Mechanism**: Self-pinging system every 5 minutes to prevent the application from sleeping
- **Environment Configuration**: Bot token is managed through Replit's environment variables system

### Data Structure Design
- **Hierarchical Player Data**: Nested JSON structure with player IDs as keys and comprehensive game data as values
- **Server Statistics**: Global statistics tracking total PvP battles, breakthroughs, dungeons completed, and techniques learned
- **Timestamp Tracking**: All player actions and data updates include timestamp tracking for cooldowns and analytics

## External Dependencies

### Core Libraries
- **discord.py**: Discord API wrapper for bot functionality
- **flask**: Lightweight web framework for the keep-alive server
- **requests**: HTTP library for self-pinging functionality

### Platform Dependencies
- **Replit Environment**: Designed specifically for Replit hosting platform
- **Environment Variables**: Relies on Replit's secrets management for bot token storage

### File System
- **Local JSON Storage**: No external database required - uses local file system for data persistence
- **Automatic Backup Creation**: Creates periodic backups without external backup services

### Discord Platform
- **Discord Bot API**: Requires bot token and appropriate permissions for Discord server integration
- **Discord Gateway**: Real-time event handling for user commands and interactions