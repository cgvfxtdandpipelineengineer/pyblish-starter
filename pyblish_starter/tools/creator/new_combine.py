import os
import maya.cmds as cmds
from capture import capture
import ffmpeg
import os #for controlling file and folder path



def get_cameras():
    all_cameras = cmds.ls(type = 'camera')

    cameras = []
    for camera in all_cameras:
        if camera.startswith("CAM"):
            cameras.append(camera)

    return cameras


def get_output_directory():
    home_dir = os.path.expanduser('~')
    output_dir = os.path.join(home_dir, "Documents", "MayaOutputVideos", "test1")
    return output_dir


def get_output_file(filename):
    return os.path.join(get_output_directory(), filename)


def get_all_paths_file(filename):
    return os.path.join(get_output_directory(), filename)


def capturing_videos(all_cameras, output_directory):
    list_of_videos = []

    #checking if the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)#creates the directory if it doesn't exist
   
       
    for i in all_cameras:
        output_path = os.path.join(output_directory, f"{i}_playblast.mov") #creating path for each camera
        list_of_videos.append(output_path)
       
        capture(i, 800, 600,
            viewport_options={
                # "displayAppearance": "wireframe",
                "grid": True,
                "polymeshes": True,
            },
            camera_options={
                "displayResolution": True
            },
            filename=output_path, 
            overwrite = True,
        )
    
    return list_of_videos
    
    
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
        
    #if os.path.exists(all_paths):
    #    os.remove(all_paths)
     

if __name__ == "__main__":
    all_cameras = get_cameras()
    output_directory = get_output_directory()
    output_file = get_output_file("combined_video_test1.mov")
    all_paths = get_all_paths_file("all_paths.txt")

    list_of_videos = capturing_videos(all_cameras, output_directory)

    #capturing_videos(all_cameras, output_directory) #calling the function to playblast everything

    try:
        combine_videos(list_of_videos, output_file, all_paths)
    except Exception as e:
        print("Error during video combination:", e)