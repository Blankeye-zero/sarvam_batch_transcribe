import os
import sys
import io
import asyncio
from pprint import pprint
from dotenv import load_dotenv
import job_functions as jbf
from transform_files import split_video_to_audio_segments
from sarvam_client import SarvamClient

async def main():
    '''
    The Main Execution Flow
    '''
    load_dotenv()
    INPUT_PATH = os.getenv("INPUT_PATH")
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH") 
    print("=== Starting Video Input Process ===")
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    video_files_list = os.listdir(INPUT_PATH)
    upload_list = []
    file_chunks_path_list = [] 
    execution_flow_switch = int(input("Choose one of the following options: \n 1) Input is a range of files from directory \t 2) Input is taken from file_names.txt \n"))
    if execution_flow_switch == 1:
        start_idx = int(input("Enter the start index: "))
        end_idx = int(input("Enter the end index: "))
        upload_list= video_files_list[start_idx:end_idx]
        print("You have selected the following videos: ")
        temp_list=[]
        for each_vid in upload_list:
            file_path = f"{INPUT_PATH}//{each_vid}"
            temp_list.append(file_path)
            print(file_path)
        upload_list = temp_list

    elif execution_flow_switch == 2:
        with open("file_names.txt",'r',encoding="utf-8") as f:
            for line in f:
                file_path = f"{INPUT_PATH}//{line.strip()}"
                if  line not in video_files_list:
                    print(f"The given file %s is not in the INPUT PATH: %s" % (line,INPUT_PATH))
                upload_list.append(file_path)
        print("You have selected the following videos: ")
        for each_vid in upload_list:
            print(each_vid)            
    else:
        print("Please enter either the number 1 or 2 for options")
        exit()
    
    for each_vid_path in upload_list:
        chunk_paths = split_video_to_audio_segments(video_path=each_vid_path,output_dir="audio_segments",segment_length_mins=5)
        file_chunks_path_list.extend(chunk_paths)
    ## initialize the job

    job_info =  await jbf.initialize_job()
    if not job_info:
        print("Job initialization failed")

    sarvam_job_id= job_info["job_id"]
    remote_input_storage_path = job_info["input_storage_path"]
    remote_output_storage_path= job_info["output_storage_path"]

    #Uploading files to remote input storage(azure)
    client = SarvamClient(remote_input_storage_path)
    await client.upload_files(file_chunks_path_list)

    await client.list_files()

    job_start_status = await jbf.start_job(job_id=sarvam_job_id)
    if not job_start_status:
        print("Failed to start job")
    
    print("\n=== Monitoring job status ===\n")
    attempt = 1
    while True:
        print(f"\n === Status Check attempt {attempt} === \n")
        job_run_status = await jbf.check_job_status(job_id=sarvam_job_id)
        if not job_run_status:
            print("\n === Failed to get job status === \n")
            break

        status =  job_run_status["job_state"]
        if(status == 'Completed'):
            print("\n === Job Completed Successfully === \n")
            break
        elif status == 'Failed':
            print("\n === Job Failed === \n")
            break
        else:
            print(f"⏳ Current status: {status}")
            await asyncio.sleep(10)
        attempt += 1
    
    if status == 'Completed':
        print(f"\n === Downloading Results from : {remote_output_storage_path} === \n")
        client.update_url(remote_output_storage_path)

        remote_generated_transcript_file_names = await client.list_files() 
        await client.download_files(remote_generated_transcript_file_names, destination_dir=DOWNLOAD_PATH)

    print(f"\n === Download Complete === \n")
    print(f"\n === Files available at {DOWNLOAD_PATH} === ")



# Run the main function
if __name__ == "__main__":
    asyncio.run(main())