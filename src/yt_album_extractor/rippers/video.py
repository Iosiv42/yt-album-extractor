import yt_dlp
import os
from yt_album_extractor import utils, cli_to_api
from mutagen.oggopus import OggOpus
import ffmpeg
import math


class VideoRipper:
    def __init__(self, args):
        self.args = args

    def rip(self):
        source_filename = self.__download_source()

        tracklist = utils.get_tracklist_from_str(self.args.tracklist)
        track_no_pad = math.floor(math.log10(len(tracklist))) + 1

        for track_no, (track_start, track_name) in enumerate(tracklist, 1):
            # Slice current track from source
            track_filename = self.__slice_track_from_source(
                source_filename, track_no,
                track_no_pad, track_name,
                track_start, tracklist
            )

            # Tag the track's audio file
            self.__write_tags(
                track_filename, track_name,
                track_no, tracklist
            )


        if not self.args.keep_source:
            os.remove(source_filename)


    def __download_source(self):
        ydl_opts = {
            "format": "bestaudio/best"
        }

        ydl_opts.update(cli_to_api.cli_to_api(self.args.yt_dlp_args))
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.args.url, download=False)
            source_filename = ydl.prepare_filename(info_dict)

            if not os.path.isfile(source_filename):
                ydl.download(self.args.url)
                

        return source_filename


    def __slice_track_from_source(
        self,
        source_filename,
        track_no,
        track_no_pad,
        track_name,
        track_start,
        tracklist
    ):
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

        return track_filename


    def __write_tags(
        self,
        track_filename,
        track_name,
        track_no,
        tracklist
    ):
        track_audio = OggOpus(track_filename)

        track_audio.update({
            "TRACKNUMBER": str(track_no),
            "TOTALTRACKS": str(len(tracklist)),
            "TITLE": track_name,
        })

        if self.args.album_title is not None:
            track_audio["ALBUM"] = self.args.album_title

        if self.args.artist is not None:
            track_audio["ARTIST"] = self.args.artist
            if self.args.album_artist is None:
                track_audio["ALBUMARTIST"] = self.args.artist
            else:
                track_audio["ALBUMARTIST"] = self.args.album_artist

        if self.args.date is not None:
            track_audio["DATE"] = str(self.args.date)

        if self.args.genre is not None:
            track_audio["GENRE"] = self.args.genre

        if self.args.cover is not None:
            utils.set_opus_cover(self.args.cover, track_audio)

        track_audio.save()