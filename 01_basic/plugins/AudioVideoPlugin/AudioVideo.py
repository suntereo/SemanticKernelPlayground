import subprocess
from semantic_kernel.skill_definition import sk_function
import os
import whisper

class AudioVideo:

    @sk_function(
        description="extract audio in wav format from an mp4 file",
        name="ExtractAudio",
        input_description="Full path to the mp4 file",
    )
    def extract_audio(self, videofile: str) -> str:
        """
        Extract audio from a video file and return the full path to the extracted file.

        :param videofile: Full path to the mp4 file 
        :return: full path to the extracted audio file
        """
        print(f"Extracting auio file from video {videofile}")
        # first of all change the extension to the video file to create output path
        audio_path = videofile.replace(".mp4", ".wav")
        
        #if audio file exists, delete, maybe it is an old version
        if os.path.exists(audio_path):
            os.remove(audio_path)

        command = f'ffmpeg -i {videofile} -vn -acodec pcm_s16le -ar 44100 -ac 2 {audio_path}'
        with open(os.devnull, 'w') as devnull:
            subprocess.call(command, shell=True, stdout=devnull, stderr=devnull)

        # now ffmpeg has created the audio file, return the path to it
        return audio_path

    @sk_function(
        description="Transcript audio from a wav file to a timeline",
        name="TranscriptTimeline",
        input_description="Full path to the wav file",
    )
    def transcript_timeline(self, audiofile: str) -> str:

        """
        Extract a transcript from an audio file and return a transcript file that
        contains for each line the start and end time of the audio segment and the
        transcripted text.
        :param audiofile: Full path to the wav file 
        :return: transcripted text with start and end time
        """
        print(f"Extracting transcript from audio file {audiofile}")
        model = whisper.load_model("medium.en")

        transcription_options = {
            "task": "transcribe",
            "prompt": "You will transcribe the video to generate timeline for youtube"  # Add your prompt here
        }
        result = model.transcribe(audiofile, **transcription_options)

        transcription_string = ""
        for segment in result['segments']:
            start = segment['start']
            end = segment['end']
            text = segment['text']

            # Now I need to convert the start value, expressed in seconds, to 00:00 format
            # I can use the divmod function to get the minutes and seconds
            minutes, seconds = divmod(start, 60)
            transcription_string += f"{str(int(minutes)).zfill(2)}:{str(int(seconds)).zfill(2)}\t{text}\n"

        print(f"extracted {len(result['segments'])} audio segments")
        return transcription_string
