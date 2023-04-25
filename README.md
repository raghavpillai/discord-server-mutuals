# Discord Server Mutuals

## Introduction

Discord Server Mutuals is a web application that visualizes your Discord server mutuals. It uses Python, Streamlit, Pyvis, and Pandas to generate an interactive graph that displays users who share servers with you.

## Installation

To use the application, you need to install the dependencies listed in the requirements.txt file. To do this, run the following command in your terminal:

```sh
pip install -r requirements.txt
```

Next, create a new file named `.env` in the root directory of the project and add the following line:
TOKEN=DISCORD_USER_TOKEN

Replace `DISCORD_USER_TOKEN` with your own Discord user token. To get your Discord user token, follow these steps:
1. Open Discord in your web browser and log in.
2. Open the Developer Tools by pressing Ctrl+Shift+I on your keyboard.
3. Click on the Network tab.
4. Send a message in any channel or direct message.
5. In the Network tab, find the request that starts with messages and click on it.
6. In the Headers tab of the request details, scroll down to the Request Headers section and find the Authorization header.
7. The value of the Authorization header is your Discord user token. Copy this value (do not share this with anyone).
8. Paste the token into the .env file, replacing DISCORD_USER_TOKEN.
Note: Do not share your Discord user token with anyone. Keep it safe and secure.

## How to Run
After installing the dependencies, you can start the app by running the following command:
```
streamlit run main.py
```
This will launch the app in your default web browser.

## How to Use
Once the app is running, allow it to scrape all your Discords for users. Larger servers may not be able to be processed due to the raw amount of users (a limitation of discord.py). The app will generate a dataframe that displays the users with the most amount of mutuals. You can also interact with the generated network graph. At the current moment, adding or removing guilds to visualize causes the entire app to reload, and forces rescraping of guild data. 

## Contributions
Contributions to the Discord Server Mutuals project are welcome! If you want to contribute, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT license.
