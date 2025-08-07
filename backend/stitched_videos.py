import subprocess
import os

def stitch_videos(video_paths, output_path="output.mp4"):
    """
    Stitches multiple video files together using FFmpeg's concat demuxer.

    Args:
        video_paths (list): A list of strings, where each string is the
                            path to a video file to be included.
        output_path (str): The path for the final stitched video file.
    """

    if not video_paths:
        print("Error: No video paths provided.")
        return # Exit if the list is empty

    # Create a file list for ffmpeg (using a fixed name here)
    list_file = "video_list.txt" # Consider using tempfile module for more robustness

    try:
        print(f"Creating temporary list file: {list_file}")
        # --- MODIFICATION START ---
        # Write all video paths from the input list to the file
        with open(list_file, "w", encoding='utf-8') as f: # Good practice to specify encoding
            for video_path in video_paths:
                # It's safer to use absolute paths and forward slashes for ffmpeg
                abs_path = os.path.abspath(video_path)
                formatted_path = abs_path.replace('\\', '/') # Ensure forward slashes

                # Check if the file actually exists before adding it to the list
                if not os.path.exists(abs_path):
                    print(f"Warning: Input file not found, skipping: {abs_path}")
                    continue # Skip this file and go to the next one

                # Write the file directive, quoting the path
                f.write(f"file '{formatted_path}'\n")
        # --- MODIFICATION END ---

        # Check if any valid files were actually written to the list
        if os.path.getsize(list_file) == 0:
             print("Error: No valid video files found or written to the list file.")
             return

        # Ensure output directory exists (optional but good practice)
        output_dir = os.path.dirname(output_path)
        if output_dir: # Only create if output_path includes a directory
            os.makedirs(output_dir, exist_ok=True)

        # Construct the ffmpeg command to concatenate videos
        command = [
            "ffmpeg",
            "-y",             # Overwrite output file if it exists (optional)
            "-f", "concat",   # Use the concat demuxer
            "-safe", "0",     # Allow unsafe file paths (needed for absolute paths)
            "-i", list_file,  # Input is the text file listing the videos
            "-c", "copy",     # Copy streams without re-encoding (fast, requires compatibility)
            output_path       # The final output file path
        ]

        print("\nExecuting FFmpeg command:")
        print(" ".join(command)) # Print the command for debugging

        # Run the command, capture output for better error reporting
        process = subprocess.run(
            command,
            capture_output=True, # Capture stdout and stderr
            text=True,           # Decode as text
            check=False          # Don't raise exception on failure, check returncode manually
        )

        # Check if ffmpeg command was successful
        if process.returncode == 0:
            print(f"\nVideos successfully stitched into {output_path}")
        else:
            # Print detailed error information from ffmpeg
            print(f"\nError stitching videos. FFmpeg failed with exit code {process.returncode}.")
            print("--- FFmpeg STDERR ---")
            print(process.stderr)
            print("--- FFmpeg STDOUT ---")
            print(process.stdout)
            print("\nPossible issues: Incompatible video codecs/resolutions, file not found, permissions.")

    except Exception as e:
        # Catch other potential errors (e.g., writing the list file)
        print(f"An unexpected error occurred: {e}")

    finally:
        # Always try to clean up the temporary list file
        if os.path.exists(list_file):
            try:
                os.remove(list_file)
                print(f"Removed temporary list file: {list_file}")
            except OSError as e:
                 print(f"Warning: Could not remove temporary file {list_file}: {e}")

# --- Example Usage ---
# Corrected the __name__ check
if __name__ == "__main__":
    # Replace these with the actual paths to YOUR video files
    video_files = [
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
        "assets/Camera1/cam_1_stitched.mp4",
    ]

    # Check which files actually exist before trying to stitch
    existing_files = []
    print("Checking input files:")
    for f in video_files:
        if os.path.exists(f):
            print(f"  [OK] Found: {f}")
            existing_files.append(f)
        else:
            print(f"  [NOT FOUND] Missing: {f}")

    if not existing_files:
         print("\nNo valid input files found. Aborting stitch process.")
    elif len(existing_files) == 1:
         print("\nOnly one valid input file found. No stitching needed.")
         # Optionally copy the single file to the output path here
    else:
        output_filename = "stitched_video.mp4"
        print(f"\nAttempting to stitch {len(existing_files)} video(s) into {output_filename}...")
        stitch_videos(existing_files, output_filename)