# Advanced Music Organizer

A powerful Python script to organize your music library by artist, album, genre, or year. Supports multiple audio formats, duplicate handling, playlists, logging, undo, and more!

## Features

- Organizes MP3, FLAC, WAV files into folders by artist/album or genre/year
- Cleans/normalizes filenames and folder names
- Skips or renames duplicate songs automatically
- Option to merge small folders into "Miscellaneous"
- Creates playlist (.m3u) files in each folder
- Generates action/error logs for easy review
- Supports dry-run mode for a safe preview
- Undo log: restore previous state if needed
- Command-line interface with progress bar
- End-of-run summary (moved, skipped, errors)

## Requirements

- Python 3.x
- [Mutagen](https://mutagen.readthedocs.io/en/latest/)
- [tqdm](https://tqdm.github.io/)


### Options

- `--by [artist_album|genre_year]`  
   Organize folders by artist/album (default) or genre/year

- `--dry-run`  
   Preview moves/changes without making them

- `--undo`  
   Restore all files to their original location (uses undo log)

- `--flatten NUM`  
   Folders with ≤ NUM songs are merged into “Miscellaneous” (default: 2)

### Example
python music_organizer.py ~/Music --by genre_year --flatten 1
python music_organizer.py D:\music --dry-run
python music_organizer.py ./songs --undo


## Logs

- `music_organizer_log.txt`: actions and errors
- `music_organizer_undo.txt`: all file moves (for undo)

## License

MIT

## Contributing

Pull requests, ideas, and feedback are welcome! Please open issues or contribute features/fixes.

## Author

Tanveer Singh

---



