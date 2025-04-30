import os
import hashlib
import shutil
import argparse
import imagehash
from pathlib import Path

from PIL import Image

parser = argparse.ArgumentParser(description="Ident File Handler")

# Add arguments
parser.add_argument("path", type=str, help="Filepath of folder to start with")
parser.add_argument('--sub', action='store_true', help="Include subfolders")
parser.add_argument('--dry', action='store_true', help="Run a dry run")
# Parse the arguments
args = parser.parse_args()


def get_content_hash(path: str) -> imagehash.ImageHash:
    # Open the images (they can be of different resolutions)
    image1 = Image.open(path)

    # Compute a perceptual hash for each image.
    # You can choose from various algorithms like average_hash, phash, dhash, whash.
    hash1 = imagehash.average_hash(image1, hash_size=16)

    print(f"Image 1 Hash: {hash1}")

    return hash1


def compare_images(hash1: imagehash.ImageHash, hash2: imagehash.ImageHash) -> bool:
    # Check if the hashes are identical
    if hash1 == hash2:
        print("The images are the same (or nearly identical).")
    else:
        # Optionally, allow a small hamming distance if you expect minor changes.
        difference = hash1 - hash2
        tolerance = 5  # You can adjust this threshold
        if difference <= tolerance:
            print("The images are considered similar (within tolerance).")
        else:
            print("The images are different.")


def get_file_hash(file_path):
    """Calculate the hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def find_duplicates_with_image_hash(root_folder: str, dry_run: bool = False, include_sub_folders: bool = False):
    image_hashes = {}

    folder_path = Path(root_folder)
    if not folder_path.exists() and not folder_path.is_dir():
        raise FileNotFoundError("Folder does not exist")

    for dirpath, _, filenames in os.walk(root_folder):
        if not include_sub_folders:
            image_hashes = {}

        if not dirpath.endswith('_duplicates'):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                image_hash = get_content_hash(file_path)

                if image_hash in image_hashes:
                    existing_file_path = image_hashes[image_hash]

                    # Determine which file is bigger
                    file_size = os.path.getsize(file_path)
                    existing_file_size = os.path.getsize(existing_file_path)
                    if file_size > existing_file_size:
                        duplicate_file_path = existing_file_path
                        image_to_keep = file_path
                        image_hashes[image_hash] = file_path
                    else:
                        duplicate_file_path = file_path
                        image_to_keep = existing_file_path

                    # Create '_duplicates' folder if it doesn't exist
                    duplicates_folder = os.path.join(dirpath, '_duplicates')
                    if not os.path.exists(duplicates_folder):
                        os.makedirs(duplicates_folder)

                    # Move the duplicate file to '_duplicates' folder
                    if not dry_run:
                        shutil.move(duplicate_file_path, duplicates_folder)
                        print("Keep image {}. Move duplicate image {} to {}".format(image_to_keep, duplicate_file_path, duplicates_folder))
                    else:
                        print("SIMULATION: Keep image {}. Move duplicate image {} to {}".format(image_to_keep, duplicate_file_path, duplicates_folder))

                else:
                    image_hashes[image_hash] = file_path
            else:
                print("Folder _duplicates will not be processed")

    print("Duplicate image files have been moved to '_duplicates' folders.")



def find_duplicates(root_folder: str, dry_run: bool = False, include_sub_folders: bool = False):
    """Find and move duplicate images to '_duplicates' folder."""
    file_hashes = {}

    folder_path = Path(root_folder)
    if not folder_path.exists() and not folder_path.is_dir():
        raise FileNotFoundError("Folder does not exist")

    for dirpath, _, filenames in os.walk(root_folder):
        if not include_sub_folders:
            file_hashes = {}

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_hash = get_file_hash(file_path)

            if file_hash in file_hashes:
                existing_file_path = file_hashes[file_hash]
                existing_filename = os.path.basename(existing_file_path)

                # Determine which file has the shorter name
                if len(filename) < len(existing_filename):
                    duplicate_file_path = existing_file_path
                    file_hashes[file_hash] = file_path
                else:
                    duplicate_file_path = file_path

                # Create '_duplicates' folder if it doesn't exist
                duplicates_folder = os.path.join(dirpath, '_duplicates')
                if not os.path.exists(duplicates_folder):
                    os.makedirs(duplicates_folder)

                # Move the duplicate file to '_duplicates' folder
                if not dry_run:
                    shutil.move(duplicate_file_path, duplicates_folder)
                    print("Moved duplicate file path {} to {}".format(duplicate_file_path, duplicates_folder))
                else:
                    print("Simulated moved duplicate file path {} to {}".format(duplicate_file_path, duplicates_folder))

            else:
                file_hashes[file_hash] = file_path
    print("Duplicate image files have been moved to '_duplicates' folders.")


# Specify the root folder to search for duplicates
root_folder = args.path
sub = args.sub
dry = args.dry

if __name__ == '__main__':
    # Find and move duplicate images
    print("Start Ident File Handler")
    #find_duplicates(root_folder, include_sub_folders=False)
    find_duplicates_with_image_hash(root_folder, dry_run=dry, include_sub_folders=sub)
    print("Finished")
