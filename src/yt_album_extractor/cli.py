import argparse
from .rippers.video import VideoRipper


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
    parser.add_argument("--yt-dlp-args")

    args = parser.parse_args()

    ripper = VideoRipper(args)
    ripper.rip()


if __name__ == "__main__":
    main()