import random

import pandas as pd
import streamlit as st
from pyvis.network import Network
from collections import defaultdict

from src.icons import Icons


class Graphs:
    """
    Holds the methods for creating and displaying graphs and tables
    """

    @classmethod
    def create_network(cls, users: dict, guild_to_member_map: dict, guilds_to_show: list):
        """
        Creates a network graph of mutual guilds between users
        
        :param users: Dict of users and their mutual guilds
        :param guild_to_member_map: Dict of guilds and their members
        :param guilds_to_show: List of guilds to show in the graph
        :return: pyvis network graph
        """
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
            net.add_node(user, title=user, color='blue', shape='circularImage', font={'face':'Arial', 'size':int(150*len(users))}, image=str(Icons.avatars.get(user)))
            for guild in guilds:
                guild_to_users_map[guild].add(user)
                if guild in guilds_to_show:
                    net.add_node(guild, title=guild, color=colors[guild], shape='circularImage', size=int(105*( guild_to_num_users[guild]) **(1/10)), label=guild, font={'size':int(250*len(users)), 'face': 'Arial', 'bold': True}, image=str(Icons.server_logos.get(guild)))
                    net.add_edge(user, guild, color=colors[guild])

        return net

    @classmethod
    def display_network(cls, net: Network):
        """
        Displays the network graph in a streamlit component

        :param net: Network graph to display
        """
        net.show("example.html", notebook=True)
        html_file = open('example.html', 'r')
        html_content = html_file.read()
        st.components.v1.html(html_content, height=800)

    @classmethod
    def create_dataframe(cls, users: dict):
        """
        Creates a dataframe of mutual guilds between users

        :param users: Dict of users and their mutual guilds
        :return: Pandas dataframe
        """
        df = pd.DataFrame.from_dict(users, orient='index')
        df = df.fillna(0)
        df = df.loc[:, (df != 0).any(axis=0)]
        df['num_mutual_guilds'] = df.astype(bool).sum(axis=1)
        df = df[['num_mutual_guilds']].sort_values(by='num_mutual_guilds', ascending=False)
        return df

    @classmethod
    def get_selected_guilds(cls, users: dict):
        """
        Gets the guilds to show in the graph from the user

        :param users: Dict of users and their mutual guilds
        :return: List of guilds to show in the graph
        """
        return st.multiselect(
            "Select guilds to show:",
            sorted(list({guild for user in users for guild in users[user]})),
            default=sorted(
                list({guild for user in users for guild in users[user]})
            ),
            key='guilds_to_show',
        )