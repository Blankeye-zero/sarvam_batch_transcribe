import asyncio
import os
from pprint import pprint
from dotenv import load_dotenv
import sys

async def main():
    '''
    The Main Execution Flow
    '''
    load_dotenv()
    sys.stdout.reconfigure(encoding='utf-8')
    INPUT_PATH = os.getenv("INPUT_PATH")
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH") 
    pprint("=== Starting Video Input Process ===")
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    video_files_list = os.listdir(INPUT_PATH)
    sub_list = [] 
    execution_flow_switch = int(input("Choose one of the following options: \n 1) Input is a range of files from directory \t 2) Input is taken from file_names.txt \t"))
    if execution_flow_switch == 1:
        start_idx = int(input("Enter the start index: "))
        end_idx = int(input("Enter the end index: "))
        sub_list= video_files_list[start_idx:end_idx]
        pprint("You have selected the following videos: ")
        temp_list=[]
        for each_vid in sub_list:
            file_path = f"{INPUT_PATH}//{each_vid}"
            temp_list.append(file_path)
            print(file_path)
        sub_list = temp_list

    elif execution_flow_switch == 2:
        with open("file_names.txt",'r',encoding="utf-8") as f:
            for line in f:
                file_path = f"{INPUT_PATH}//{line}"
                if  file_path not in video_files_list:
                    pprint(f"The given file %s is not in the INPUT PATH: %s" % (file_path,INPUT_PATH))
                sub_list.append(file_path)
            pprint("You have selected the following videos: ")
            for each_vid in sub_list:
                print(each_vid)
                

    else:
        pprint("Please enter either the number 1 or 2 for options")
        exit()


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())