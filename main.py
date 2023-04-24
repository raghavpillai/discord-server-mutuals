import os
import random
import discord
import pandas as pd
import streamlit as st

from collections import defaultdict
from discord.ext import commands
from dotenv import load_dotenv
from pyvis.network import Network

load_dotenv()

def get_token():
    token = os.getenv("TOKEN")
    if token is None:
        token = st.text_input("Enter your token:")

    if token is None:
        st.write("No token provided. Please enter a token in the text box above.")
        return None
    return token

icons = {}
avatars = {}

#@st.cache_resource
async def check_mutual_guilds(_guilds, _bot):
    guilds = _guilds
    bot = _bot
    users = defaultdict(set)
    guild_to_member_map = {} # dict[guild_name] = list(members)
    my_bar = st.progress(0, text="Processing guilds..")
    for idx, guild in enumerate(guilds):
        my_bar.progress(idx/len(guilds), text=f"Processing guild {guild.name} [{idx + 1}/{len(guilds)}]...")
        icons[guild.name] = guild.icon or None
        try:
            await guild.chunk()

            # guild_to_member_map[guild.name] = {member.name for member in guild.members if not member.bot and member.name != bot.user.name}
            guild_to_member_map[guild.name] = set()
            for member in guild.members:
                if not member.bot and member.name != bot.user.name:
                    guild_to_member_map[guild.name].add(member.name + "#" + member.discriminator)
                    avatars[member.name + "#" + member.discriminator] = member.avatar
            
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

def create_dataframe(users):
    df = pd.DataFrame.from_dict(users, orient='index')
    df = df.fillna(0)
    df = df.loc[:, (df != 0).any(axis=0)]
    df['num_mutual_guilds'] = df.astype(bool).sum(axis=1)
    df = df[['num_mutual_guilds']].sort_values(by='num_mutual_guilds', ascending=False)
    return df

def get_selected_guilds(users):
    return st.multiselect(
        "Select guilds to show:",
        sorted(list({guild for user in users for guild in users[user]})),
        default=sorted(
            list({guild for user in users for guild in users[user]})
        ),
        key='guilds_to_show',
    )

def create_network(users, guild_to_member_map, guilds_to_show):
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=True) # add notebook since newest pyvis broke it
    net.barnes_hut()

    # Compute the number of users in each guild
    guild_to_num_users = defaultdict(int)
    for guild, members in guild_to_member_map.items():
        guild_to_num_users[guild] = len(members)

    # Assign unique colors to each guild
    colors = {}
    for guild in guild_to_num_users:
        colors[guild] = '#' + ''.join(
            [random.choice('0123456789ABCDEF') for _ in range(6)]
        )

    # Add nodes and edges to the network for selected guilds
    guild_to_users_map = defaultdict(set)
    for user, guilds in users.items():
        net.add_node(user, title=user, color='blue', shape='circularImage', font={'face':'Arial', 'size':int(150*len(users))}, image=str(avatars.get(user)))
        for guild in guilds:
            guild_to_users_map[guild].add(user)
            if guild in guilds_to_show:
                net.add_node(guild, title=guild, color=colors[guild], shape='circularImage', size=int(105*( guild_to_num_users[guild]) **(1/10)), label=guild, font={'size':int(250*len(users)), 'face': 'Arial', 'bold': True}, image=str(icons.get(guild)))
                net.add_edge(user, guild, color=colors[guild])

    return net

def display_network(net):
    net.show("example.html", notebook=True)
    html_file = open('example.html', 'r')
    html_content = html_file.read()
    st.components.v1.html(html_content, height=800)

def main():
    bot = commands.Bot(command_prefix="!", self_bot=True, fetch_offline_members=True)
    token = get_token()

    @bot.event
    async def on_ready():
        st.set_page_config(layout="wide")
        st.title("Mutual Guilds")
        st.write("Logged in as", bot.user.name)

        guilds = bot.guilds
        st.write(f"Checking mutual guilds for {len(guilds)} guilds")

        users, guild_to_member_map = await check_mutual_guilds(guilds, bot)
        df = create_dataframe(users)
        st.write(df)

        guilds_to_show = get_selected_guilds(users)

        net = create_network(users, guild_to_member_map, guilds_to_show)
        display_network(net)

    bot.run(token)
    

if __name__ == "__main__":
    main()