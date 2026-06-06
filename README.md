# yt-album-extractor
Download album from YouTube album and automatically split them into Opus files with tagging

# Prerequisites

* ffmpeg
* opustags
* yt-dlp

# Usage

Now, only extracting from videos (like ones that has "FULL ALBUM", etc. in title) is working.
Gather video URL, episodes/track listing (from video description or made it by yourself) in for of:

```
[HH:]MM:SS Track1 title
[HH:]MM:SS Track2 title
...
```

and optional album name, artist name, album date, and cover file. If you do not add optional
arguments, there will be no tags in resulting track files and as consequence will not be organized
in your collection.

Then pass these arguments to the script:

```
python main.py -l episodes -t album_name -a artist_name -d album_date -c cover_file URL
```

After the script finishes it leaves video file downloaded by `yt-dlp`.

If you provided all optional arguments, then after all your current working directory
has album with each track in separate file with tagging to add it to your music library
effortlessly.
