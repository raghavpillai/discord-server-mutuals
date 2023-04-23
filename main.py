import os
import random
import discord
import pandas as pd
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import streamlit.components.v1 as stc

from collections import defaultdict
from discord.ext import commands
from dotenv import load_dotenv
from pyvis.network import Network



load_dotenv()

TOKEN = os.getenv("TOKEN")


bot = commands.Bot(command_prefix="!", self_bot=True, fetch_offline_members=True)

st.set_page_config(layout="wide")
if TOKEN is None:
    TOKEN = st.text_input("Enter your token:")
    if TOKEN is None:
        st.write("No token provided. Please enter a token in the text box above.")
        st.stop()

@bot.event
async def on_ready():
    st.title("Mutual Guilds")
    st.write("Logged in as", bot.user.name)

    guilds = bot.guilds
    st.write(f"Checking mutual guilds for {len(guilds)} guilds")

    users = defaultdict(set)
    for idx, guild in enumerate(guilds):
        if len(users) >= 10:
            break

        st.write(f"Processing mutual guilds for {guild.name} [{idx + 1}/{len(guilds)}]")
        try:
            await guild.chunk()
            for member in guild.members:
                # If member is a bot or self, skip
                if member.bot or member == bot.user:
                    continue

                if member.name in users:
                    continue

                mutual_guilds = [g.name for g in bot.guilds if member in g.members]

                if len(mutual_guilds) <= 1:
                    continue

                st.write(f"**[{member.name}] [Shares {len(mutual_guilds)} guilds]:**")
                st.write(', '.join(mutual_guilds))
                users[member.name].update(mutual_guilds)
        except discord.errors.HTTPException:
            st.write(f"This guild cannot be chunked: {guild.name}")
        except discord.errors.Forbidden:
            st.write(f"Access denied to guild: {guild.name}")
        except Exception as e:
            st.write(f"Error occurred while checking guild {guild.name}: {e}")

    # Write the users dict in descending order of number of mutual guilds (value) to streamlit
    df = pd.DataFrame.from_dict(users, orient='index')
    df = df.fillna(0)
    df = df.loc[:, (df != 0).any(axis=0)]
    df['num_mutual_guilds'] = df.astype(bool).sum(axis=1)
    df = df[['num_mutual_guilds']].sort_values(by='num_mutual_guilds', ascending=False)
    st.write(df)

    guilds_to_show = st.multiselect(
        "Select guilds to show:",
        sorted(list({guild for user in users for guild in users[user]})),
        default=sorted(
            list({guild for user in users for guild in users[user]})
        ),
        key='guilds_to_show'
    )

    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=True) # add notebook since newest pyvis broke it
    net.barnes_hut()

    # Compute the number of mutual guilds for each guild
    num_mutual_guilds = defaultdict(int)
    for user, guilds in users.items():
        for guild in guilds:
            if guild in guilds_to_show:
                num_mutual_guilds[guild] += 1

    # Assign unique colors to each guild
    colors = {}
    for user, guilds in users.items():
        for guild in guilds:
            if guild not in colors:
                colors[guild] = '#' + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])

    # Add nodes and edges to the network for selected guilds
    for user, guilds in users.items():
        net.add_node(user, title=user, color='blue', shape='roundrectangle', font={'face':'Arial', 'size':int(60*len(users)**(-1/4))})
        for guild in guilds:
            if guild in guilds_to_show:
                net.add_node(guild, title=guild, color=colors[guild], size=int(105*(num_mutual_guilds[guild]/len(users))**(1/4)), label=guild, font={'size':int(75*len(users)**(-1/4)), 'face': 'Arial', 'bold': True})
                net.add_edge(user, guild, color=colors[guild])

    net.show("example.html", notebook=True)
    html_file = open('example.html', 'r')
    html_content = html_file.read()
    st.components.v1.html(html_content, height=800)

bot.run(TOKEN)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.LoginFailure):
        st.write("Invalid token. Please enter a valid token in the text box above.")
        st.stop()