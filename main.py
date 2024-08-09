import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import NEBULA.nebula as nebula

if __name__ == "__main__":
    nebula.bot_run()