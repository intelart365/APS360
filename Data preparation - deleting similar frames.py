import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

def compute_image_hash(image_path):
    """
    Compute a hash of the image for quick comparison.
    """
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img = img.resize((64, 64), Image.LANCZOS)
        img_bytes = img.tobytes()
        return hashlib.md5(img_bytes).hexdigest()

def compare_images(image1, image2):
    """
    Compare two images using Structural Similarity Index (SSI).
    Returns the similarity score.
    """
    gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(gray_image1, gray_image2, full=True)
    return score

def find_and_delete_similar_images(folder_path, similarity_threshold=0.95):
    """
    Find and delete pairs of images that are similar.
    """
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    image_paths = [os.path.join(folder_path, f) for f in image_files]

    # Precompute image dimensions and hashes
    images_info = []
    for path in image_paths:
        try:
            image = cv2.imread(path)
            if image is None:
                continue
            image_hash = compute_image_hash(path)
            images_info.append((path, image.shape, image_hash))
        except Exception as e:
            print(f"Failed to process {path}: {e}")

    total_comparisons = 0
    delete_count = 0
    used_indices = set()

    def process_pair(idx1, idx2):
        nonlocal delete_count, total_comparisons
        path1, shape1, hash1 = images_info[idx1]
        path2, shape2, hash2 = images_info[idx2]

        if shape1 != shape2 or hash1 != hash2 or idx1 in used_indices or idx2 in used_indices:
            return None

        image1 = cv2.imread(path1)
        image2 = cv2.imread(path2)

        similarity = compare_images(image1, image2)
        total_comparisons += 1

        if similarity >= similarity_threshold:
            try:
                os.remove(path2)
                used_indices.add(idx2)
                return os.path.basename(path2)
            except FileNotFoundError:
                pass

        return None

    # Use multiprocessing for parallel processing
    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(len(images_info)):
            for j in range(i + 1, len(images_info)):
                futures.append(executor.submit(process_pair, i, j))

        for future in as_completed(futures):
            result = future.result()
            if result:
                print(result)
                delete_count += 1

    print(f"Total images deleted: {delete_count}")

# Usage
folder_path = r'C:\Users\ollie\OneDrive\Desktop\Mixed Images'  # Update this path to your images folder
find_and_delete_similar_images(folder_path, similarity_threshold=0.9)
