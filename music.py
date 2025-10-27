import os
import re
import shutil
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from tqdm import tqdm

SUPPORTED_FORMATS = ['.mp3', '.flac', '.wav']
LOGFILE = "music_organizer_log.txt"
UNDOFILE = "music_organizer_undo.txt"
MISC_FOLDER = "Miscellaneous"

def clean_name(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def get_metadata(file_path):
    try:
        audio = File(file_path, easy=True)
        artist = audio.get('artist', ['Unknown Artist'])[0]
        album = audio.get('album', ['Unknown Album'])[0]
        genre = audio.get('genre', ['Unknown Genre'])[0]
        year = audio.get('date', ['Unknown Year'])[0]
        return map(clean_name, [artist, album, genre, year])
    except Exception as e:
        return ("Unknown Artist", "Unknown Album", "Unknown Genre", "Unknown Year")

def write_log(msg):
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def write_undo(original, new):
    with open(UNDOFILE, "a", encoding="utf-8") as f:
        f.write(f"{new}|{original}\n")

def create_playlist(dir_path):
    songs = [f for f in os.listdir(dir_path) if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS]
    if songs:
        playlist_path = os.path.join(dir_path, "playlist.m3u")
        with open(playlist_path, "w", encoding="utf-8") as f:
            f.write("\n".join(songs))

def undo_restore():
    if not os.path.isfile(UNDOFILE):
        print("No undo log found.")
        return
    with open(UNDOFILE, "r", encoding="utf-8") as f:
        lines = [line.strip().split("|") for line in f if "|" in line]
    for new, original in lines:
        if os.path.exists(new):
            shutil.move(new, original)
            print(f"Restored {new} to {original}")
    os.remove(UNDOFILE)
    print("Undo completed.")

def organize_music(music_path, by='artist_album', dry_run=False, flatten=2):
    if not os.path.isdir(music_path):
        print("Invalid music folder path.")
        return

    os.makedirs(LOGFILE, exist_ok=True)
    moved, skipped, errors = 0, 0, 0
    folder_counts = {}

    all_files = []
    for root, _, files in os.walk(music_path):
        for file in files:
            if os.path.splitext(file)[1].lower() in SUPPORTED_FORMATS:
                all_files.append(os.path.join(root, file))

    for file_path in tqdm(all_files, desc="Processing Files"):
        artist, album, genre, year = get_metadata(file_path)
        if by == 'genre_year':
            new_dir = os.path.join(music_path, genre, year)
        elif by == 'artist_album':
            new_dir = os.path.join(music_path, artist, album)
        else:
            new_dir = os.path.join(music_path, artist, album)

        folder_counts.setdefault(new_dir, 0)
        folder_counts[new_dir] += 1

        file_name = clean_name(os.path.basename(file_path))
        new_path = os.path.join(new_dir, file_name)

        # Duplicate check & normalization
        i = 1
        while os.path.exists(new_path):
            # Append number if duplicate
            base, ext = os.path.splitext(file_name)
            new_path = os.path.join(new_dir, f"{base}_{i}{ext}")
            i += 1

        # Miscellaneous flattener
        if folder_counts[new_dir] <= flatten:
            new_dir = os.path.join(music_path, MISC_FOLDER)
            new_path = os.path.join(new_dir, file_name)

        if dry_run:
            print(f"[Dry Run] Would move '{file_path}' to '{new_path}'")
            continue

        try:
            os.makedirs(new_dir, exist_ok=True)
            if file_path != new_path:
                shutil.move(file_path, new_path)
                write_log(f"Moved '{file_path}' -> '{new_path}'")
                write_undo(file_path, new_path)
                moved += 1
            else:
                skipped += 1
        except Exception as e:
            write_log(f"Error moving '{file_path}': {e}")
            errors += 1

    # Generate playlists
    for dir_path in folder_counts:
        create_playlist(dir_path)
    create_playlist(os.path.join(music_path, MISC_FOLDER))

    print(f"\nSummary: Moved={moved} Skipped={skipped} Errors={errors}")
    print(f"Log written to: {LOGFILE}")
    print(f"Undo log written to: {UNDOFILE}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Advanced Music Organizer")
    parser.add_argument("path", help="Path to your music folder")
    parser.add_argument("--by", choices=['artist_album', 'genre_year'], default='artist_album', help="Organize by")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--undo", action="store_true", help="Restore previous state")
    parser.add_argument("--flatten", type=int, default=2, help="Merge folders with <= n files into Miscellaneous")

    args = parser.parse_args()
    if args.undo:
        undo_restore()
    else:
        organize_music(args.path, by=args.by, dry_run=args.dry_run, flatten=args.flatten)
