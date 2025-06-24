"""
Main script to run the mailing.
This needs to be added to "Scheduled Tasks" on PythonAnywhere.
"""

import asyncio
from bot_logic import send_daily_digest
from database import init_db

if __name__ == '__main__':
    print('Initializing DB...')
    init_db()
    print('Starting digest mailing...')
    asyncio.run(send_daily_digest())
    print('Digest mailing finished')
