import os
import discord

import streamlit as st
from collections import defaultdict
from discord.ext import commands

from src.graphs import Graphs
from src.icons import Icons


class SelfBot:
    """
    Creates a selfbot and handles the logic for getting discord data
    """

    @classmethod
    def get_token(cls) -> str:
        """
        Gets the token from the environment variable TOKEN or from the text box if it is not set

        :return: Token
        """
        token = os.getenv("TOKEN")
        if token is None:
            token = st.text_input("Enter your token:")

        if token is None:
            st.write("No token provided. Please enter a token in the text box above.")
            return None
        return token

    @classmethod
    async def check_mutual_guilds(cls, _guilds: dict, _bot: commands.Bot): # Private vars because st forces it for caching
        """
        Gets the mutual guilds between selfbot and other users

        :param _guilds: Dict of guilds
        :param _bot: Selfbot
        :return: Dict of users and their mutual guilds
        """
        guilds = _guilds
        bot = _bot
        users = defaultdict(set)
        guild_to_member_map = {} # dict[guild_name] = list(members)
        my_bar = st.progress(0, text="Processing guilds..")
        for idx, guild in enumerate(guilds):
            my_bar.progress(idx/len(guilds), text=f"Processing guild {guild.name} [{idx + 1}/{len(guilds)}]...")
            Icons.server_logos[guild.name] = guild.icon or None
            try:
                await guild.chunk()

                # guild_to_member_map[guild.name] = {member.name for member in guild.members if not member.bot and member.name != bot.user.name}
                guild_to_member_map[guild.name] = set()
                for member in guild.members:
                    if not member.bot and member.name != bot.user.name:
                        guild_to_member_map[guild.name].add(member.name + "#" + member.discriminator)
                        Icons.avatars[member.name + "#" + member.discriminator] = member.avatar
                
                st.write(f"<font size='2'>Successfully processed guild [{guild.name}]</font>", unsafe_allow_html=True)
            except discord.errors.HTTPException:
                st.write(f"<font size='2'>This guild cannot be chunked: [{guild.name}]</font>", unsafe_allow_html=True)
            except discord.errors.Forbidden:
                st.write(f"<font size='2'>Access denied to guild: [{guild.name}]</font>", unsafe_allow_html=True)
            except Exception as e:
                st.write(f"<font size='2'>Error occurred while checking guild [{guild.name}]: {e}</font>", unsafe_allow_html=True)
        my_bar.progress(
            100, text="Finished processing guilds. Performing post processing"
        )

        # Build the users dict in O(n^2) time
        for user in set.union(*guild_to_member_map.values()):
            mutual_guilds = [guild for guild, members in guild_to_member_map.items() if user in members]
            if len(mutual_guilds) > 1:
                # st.write(f"**[{user}] [Shares {len(mutual_guilds)} guilds]:**")
                # st.write(', '.join(mutual_guilds))
                users[user].update(mutual_guilds)

        my_bar.progress(
            100, text="Finished processing."
        )

        return users, guild_to_member_map

    @classmethod
    def run(cls):
        """
        Main function for the selfbot

        :return: None
        """
        st.set_page_config(layout="wide")
        bot = commands.Bot(command_prefix="!", self_bot=True, fetch_offline_members=True)
        token = cls.get_token()
        st.title("Mutual Guilds")
        
        @bot.event
        async def on_ready():
            st.write("Logged in as", bot.user.name)
            guilds = bot.guilds
            st.write(f"Checking mutual guilds for {len(guilds)} guilds")

            users, guild_to_member_map = await cls.check_mutual_guilds(guilds, bot)
            df = Graphs.create_dataframe(users)
            st.write(df)

            guilds_to_show = Graphs.get_selected_guilds(users)

            net = Graphs.create_network(users, guild_to_member_map, guilds_to_show)
            Graphs.display_network(net)

        bot.run(token)