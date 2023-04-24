from dotenv import load_dotenv
from src.selfbot import SelfBot

load_dotenv()

if __name__ == "__main__":
    SelfBot.run()