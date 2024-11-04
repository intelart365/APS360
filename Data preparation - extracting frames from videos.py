import cv2
import os


def get_number_of_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total_frames


def save_frame(video_path, frame_number, output_folder, video_label):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if not ret:
        print(f"Error: Could not read frame {frame_number} from video {video_path}.")
        return

    frame_filename = os.path.join(output_folder, f"{video_label}_frame_{frame_number:06d}.jpg")
    cv2.imwrite(frame_filename, frame)
    print(f"Frame {frame_number} from {video_label} has been saved to {output_folder}.")

    cap.release()


def process_videos(input_folder, output_folder, want_frames):
    for filename in os.listdir(input_folder):
        video_path = os.path.join(input_folder, filename)
        if os.path.isfile(video_path) and filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            video_label = os.path.splitext(filename)[0]  # Label derived from the video filename

            num_frames = get_number_of_frames(video_path)
            if num_frames is None:
                continue

            print(f"Processing {filename}: Total number of frames: {num_frames}")

            frames_to_save = []
            sections = num_frames / want_frames
            frame = 1
            while frame < num_frames:
                frames_to_save.append(round(frame))
                frame += sections

            print(f'Number of frames to save for {filename}: {len(frames_to_save)}')

            for frame_number in frames_to_save:
                save_frame(video_path, frame_number, output_folder, video_label)


# Paths
input_folder = r"C:\Users\ollie\OneDrive\Desktop\School\APS360 project\Raw Videos 30"
output_folder = r"C:\Users\ollie\OneDrive\Desktop\School\APS360 project\Raw Frames 15000"

# Specify the number of frames you want to save from each video
want_frames = 500

# Process the videos in the input folder
process_videos(input_folder, output_folder, want_frames)
