#!/usr/bin/env python3
"""
Auto-scheduler for weekly updates
Runs the update script automatically on schedule
"""

import schedule
import time
from run_update import main as run_update

def tuesday_nfl_update():
    print("🏈 TUESDAY NFL UPDATE TRIGGERED")
    run_update()

def wednesday_cfb_update():
    print("🎓 WEDNESDAY CFB UPDATE TRIGGERED") 
    run_update()

# Schedule updates
schedule.every().tuesday.at("18:00").do(tuesday_nfl_update)  # 6 PM EST
schedule.every().wednesday.at("14:00").do(wednesday_cfb_update)  # 2 PM EST

print("⏰ SCHEDULER ACTIVE - Waiting for update times...")
print("📅 NFL Updates: Every Tuesday at 6:00 PM")
print("📅 CFB Updates: Every Wednesday at 2:00 PM")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute