import subprocess
import yt_dlp
import ffmpeg
import argparse
import math
import os
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture
from mutagen import id3
from PIL import Image
import base64


def get_tracklist(tracklist_str):
    tracklist = tracklist_str.split("\n")
    tracklist = [line.strip().split(" ", maxsplit=1) for line in tracklist]
    tracklist = [(e1.strip(), e2.strip()) for e1, e2 in tracklist]
    return tuple(tracklist)


def set_cover(cover_filename, ogg_opus):
    """
        This function doesn't saves ogg_opus
    """

    with open(cover_filename, "rb") as cf:
        data = cf.read()

    cover = Picture()
    cover.data = data

    with Image.open(cover_filename) as im:
        cover.type = id3.PictureType.COVER_FRONT
        cover.width = im.width
        cover.height = im.height
        
        match im.mode:
            case "1":
                cover.depth = 1
            case "L" | "P" | "":
                cover.depth = 8
            case "RGB" | "YCbCr" | "LAB" | "HSV":
                cover.depth = 24
            case "RGBA" | "CMYK" | "I" | "F":
                cover.depth = 32
            case _:
                raise RuntimeError(f"Cannot find bit depth for {im.mode} mode")
            
        # Not tested !!! TODO
        cover.mime = f"image/{im.format}"

    cover_data = cover.write()
    encoded_data = base64.b64encode(cover_data)
    vcomment_value = encoded_data.decode("ascii")

    ogg_opus["metadata_block_picture"] = [vcomment_value]


def main():
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
    parser.add_argument(
        "-k", "--keep-source",
        action="store_true", default=False,
    )

    args = parser.parse_args()

    ydl_opts = {
        "format": "bestaudio/best"
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(args.url, download=False)
        source_filename = ydl.prepare_filename(info_dict)

        if not os.path.isfile(source_filename):
            ydl.download(args.url)

    tracklist = get_tracklist(args.tracklist)
    track_no_pad = math.floor(math.log10(len(tracklist))) + 1
    for track_no, (track_start, track_name) in enumerate(tracklist, 1):
        # Slice current track from source
        stream = ffmpeg.input(source_filename)

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

        # Tag the track's audio file
        track_audio = OggOpus(track_filename)

        track_audio.update({
            "TRACKNUMBER": str(track_no),
            "TOTALTRACKS": str(len(tracklist)),
            "TITLE": track_name,
        })

        if args.album_title is not None:
            track_audio["ALBUM"] = args.album_title

        if args.artist is not None:
            track_audio["ARTIST"] = args.artist
            if args.album_artist is None:
                track_audio["ALBUMARTIST"] = args.artist
            else:
                track_audio["ALBUMARTIST"] = args.album_artist

        if args.date is not None:
            track_audio["DATE"] = str(args.date)

        if args.genre is not None:
            track_audio["GENRE"] = args.genre

        if args.cover is not None:
            set_cover(args.cover, track_audio)

        track_audio.save()

    if not args.keep_source:
        os.remove(source_filename)


if __name__ == "__main__":
    main()