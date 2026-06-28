import base64

from PIL import Image

from mutagen.flac import Picture
from mutagen.oggopus import OggOpus
from mutagen import id3

def get_tracklist_from_str(tracklist_str):
    tracklist = tracklist_str.split("\n")
    tracklist = [line.strip().split(" ", maxsplit=1) for line in tracklist]
    tracklist = [(e1.strip(), e2.strip()) for e1, e2 in tracklist]
    return tuple(tracklist)

def set_opus_cover(cover_filename, ogg_opus: OggOpus):
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