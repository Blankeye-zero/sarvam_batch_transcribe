import asyncio
import os
from pprint import pprint
from dotenv import load_dotenv
async def main():
    '''
    The Main Execution Flow
    '''
    load_dotenv()
    INPUT_PATH = os.getenv("INPUT_PATH")
    DONWLOAD_PATH = os.getenv("DOWNLOAD_PATH") 
    pprint("\\n=== Starting Video Input Process ===\\n")
    os.makedirs(DONWLOAD_PATH)


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())