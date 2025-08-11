#!/usr/bin/env python3
"""
Weekly Betting Site Updater
Run this script every Tuesday/Wednesday to update your site
"""

from autopilot_updater import AutoPilotBettingUpdater
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🚀 STARTING WEEKLY BETTING UPDATE...")
    
    # Initialize updater
    updater = AutoPilotBettingUpdater()
    
    # Run full update
    updater.run_full_update()
    
    print("✅ UPDATE COMPLETE! Check your site for new picks.")

if __name__ == "__main__":
    main()