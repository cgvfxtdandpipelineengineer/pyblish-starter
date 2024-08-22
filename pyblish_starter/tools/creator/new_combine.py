import maya.cmds as cmds
from capture import capture
import ffmpeg
import os #for controlling file and folder path

all_cameras = cmds.ls(type = 'camera')

list_of_videos = []

def capturing_videos(all_cameras, output_directory):
    global list_of_videos

    #checking if the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)#creates the directory if it doesn't exist
   
       
    for i in all_cameras:
        output_path = os.path.join(output_directory, f"{i}_playblast.mov") #creating path for each camera
        list_of_videos.append(output_path)
       
        capture(i, 800, 600,
        viewport_options={
            "displayAppearance": "wireframe",
            "grid": True,
            "polymeshes": True,
        },
        camera_options={
            "displayResolution": True
        },
        filename=output_path, 
        overwrite = True
       )
    
    
def combine_videos(list_of_videos, output_file, all_paths):
 
    #building the list of ffmpeg paths inputs
    inputs = [ffmpeg.input(video) for video in list_of_videos]
    
    #write in the txt file
    with open(all_paths, 'w') as allPaths:
        for i in list_of_videos:
            allPaths.write(f"file '{i}'\n")

    try: 
        ffmpeg.input(all_paths, format = 'concat', safe = 0) \
            .output(output_file, c = 'copy') \
            .run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print('FFmpeg failed:')
        print('stdout:', e.stdout.decode('utf8') if e.stdout else "No stdout output")
        print('stderr:', e.stderr.decode('utf8') if e.stderr else "No stderr output")
        raise e
        
    if os.path.exists(all_paths):
        os.remove(all_paths)
     
output_directory = "C:/Users/aluaa/Documents/MayaOutputVideos/test1"   
output_file = os.path.join(output_directory, "combined_video_test1.mov")
all_paths = os.path.join(output_directory, "my_videos.txt")

#capturing_videos(all_cameras, output_directory) #calling the function to playblast everything

'''
try:
    combine_videos(list_of_videos, output_file, all_paths)
except Exception as e:
    print("Error during video combination:", e)
'''