import logging
import sys
from bot.core.loop import BotLoop

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def main():
    setup_logging()
    bot = BotLoop()
    bot.start()

if __name__ == "__main__":
    main()

