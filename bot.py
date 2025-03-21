"""
Discord Bot - Core functionality
This module contains the core bot implementation
"""
from discord.ext import commands

# Custom check for admin/owner/moderator permissions
def is_admin_owner_mod():
    async def predicate(ctx):
        # Check if user is server owner
        if ctx.author.id == ctx.guild.owner_id:
            return True
        
        # Check if user has administrator permissions
        if ctx.author.guild_permissions.administrator:
            return True
        
        # Check if user has a role named "Moderator"
        return any(role.name.lower() == "moderator" for role in ctx.author.roles)
    
    return commands.check(predicate)

import os
import logging
import discord
from discord.ext import commands
import asyncio
from config import CONFIG

logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """
    Main Discord bot class that extends discord.py's commands.Bot
    """
    
    def __init__(self, command_prefix, intents, **kwargs):
        super().__init__(command_prefix=command_prefix, intents=intents, **kwargs)
        self.token = os.environ.get("DISCORD_TOKEN")
        if not self.token:
            logger.error("No Discord token found in environment variables")
            raise ValueError("DISCORD_TOKEN not set in environment variables")
    
    async def setup_hook(self):
        """
        Hook that is called when the bot is starting up
        Used to load cogs and perform other initialization tasks
        """
        await self.load_cogs()
        logger.info("Bot setup complete")
    
    async def load_cogs(self):
        """
        Load all cog modules from the cogs directory
        """
        try:
            for cog in CONFIG["COGS"]:
                await self.load_extension(f"cogs.{cog}")
                logger.info(f"Loaded cog: {cog}")
        except Exception as e:
            logger.error(f"Error loading cogs: {e}")
            raise
    
    async def on_ready(self):
        """
        Event handler that's called when the bot is ready
        """
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, 
                name=f"{CONFIG['PREFIX']}help"
            )
        )
    
    def run(self):
        """
        Run the bot with the token from environment variables
        """
        try:
            super().run(self.token, reconnect=True)
        except discord.errors.LoginFailure:
            logger.error("Invalid Discord token. Please check your environment variables.")
        except Exception as e:
            logger.error(f"Error running bot: {e}")

def initialize_bot():
    """
    Initialize the bot with proper intents and configuration
    Returns an instance of the DiscordBot class
    """
    # Set up intents
    intents = discord.Intents.default()
    intents.message_content = True  # Needed to read message content for commands
    intents.members = True  # Needed for member-related events

    # Create bot instance
    bot = DiscordBot(
        command_prefix=CONFIG["PREFIX"],
        intents=intents,
        description=CONFIG["DESCRIPTION"],
        help_command=None,  # Disable the default help command in favor of our custom one
    )
    
    return bot
