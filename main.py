import subprocess
import yt_dlp
import ffmpeg
import argparse
import math
import os


def get_tracklist(tracklist_str):
    tracklist = tracklist_str.split("\n")
    tracklist = [line.split(" ", maxsplit=1) for line in tracklist]
    tracklist = [(e1.strip(), e2.strip()) for e1, e2 in tracklist]
    return tuple(tracklist)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="YTAlbumExtracter"
    )

    parser.add_argument("url")
    parser.add_argument("-l", "--tracklist")
    parser.add_argument("-t", "--album-title")
    parser.add_argument("-a", "--artist")
    parser.add_argument("--album-artist")
    parser.add_argument("-d", "--date", type=int)
    parser.add_argument("-c", "--cover")
    parser.add_argument("-g", "--genre")

    args = parser.parse_args()

    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(args.url, download=False)
        video_filename = ydl.prepare_filename(info_dict)

        if not os.path.isfile(video_filename):
            ydl.download(args.url)

    tracklist = get_tracklist(args.tracklist)
    track_no_pad = math.floor(math.log10(len(tracklist))) + 1
    for track_no, (track_start, track_name) in enumerate(tracklist, 1):
        stream = ffmpeg.input(video_filename)

        track_filename = f"{track_no:0>{track_no_pad}} - {track_name}.opus"
        stream = stream.output(
            track_filename,
            acodec="libopus",
            audio_bitrate="128k",
            ss=track_start
        )

        try:
            track_stop = tracklist[track_no][0]
            stream.node.kwargs["to"] = track_stop
        except IndexError:
            pass

        ffmpeg.run(stream)

        tags = {
            "TRACKNUMBER": track_no,
            "TITLE": track_name,
        }

        if args.album_title is not None:
            tags["ALBUM"] = args.album_title

        if args.artist is not None:
            tags["ARITST"] = args.artist
            if args.album_artist is None:
                tags["ALBUMARTIST"] = args.artist
            else:
                tags["ALBUMARTIST"] = args.album_artist

        if args.date is not None:
            tags["DATE"] = args.date

        if args.genre is not None:
            tags["GENRE"] = args.genre

        opustags_args = [
            "opustags", "-i",
            *(item for k, v in tags.items() for item in ("--set", f"{k}={v}")),
        ]

        if args.cover is not None:
            opustags_args.extend(("--set-cover", args.cover))

        opustags_args.append(track_filename)

        subprocess.run(opustags_args)
