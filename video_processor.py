import os
import streamlit as st
import speech_recognition as sr

def process_video_submission(uploaded_file):
    """Process uploaded video file and return its transcript."""
    try:
        # Try to import moviepy
        try:
            from moviepy.editor import VideoFileClip
            has_moviepy = True
        except ImportError:
            has_moviepy = False
            st.error("""
                MoviePy package is not installed. Video processing is limited.
                To enable full video processing, please install MoviePy:
                pip install moviepy
            """)
            return "Video processing is currently unavailable. Please submit a text file instead."

        if not has_moviepy:
            return "Video processing is currently unavailable. Please submit a text file instead."

        # Save uploaded video temporarily
        video_path = f"temp_video.{uploaded_file.name.split('.')[-1]}"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())

        # Extract audio from video
        video_clip = VideoFileClip(video_path)
        audio_path = "temp_audio.wav"
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path)
        
        # Clean up video resources
        audio_clip.close()
        video_clip.close()

        # Transcribe audio
        transcript = transcribe_audio_chunks(audio_path)

        # Clean up temporary files
        os.remove(video_path)
        os.remove(audio_path)

        return transcript

    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return "Error processing video. Please submit a text file instead."

def transcribe_audio_chunks(audio_path):
    """Transcribe audio file by processing it in chunks."""
    try:
        # Try to import pydub
        try:
            from pydub import AudioSegment
            has_pydub = True
        except ImportError:
            has_pydub = False
            st.error("""
                Pydub package is not installed. Audio transcription is limited.
                To enable full audio transcription, please install Pydub:
                pip install pydub
            """)
            return "Audio transcription is currently unavailable."

        if not has_pydub:
            return "Audio transcription is currently unavailable."

        audio = AudioSegment.from_wav(audio_path)
        chunk_length_ms = 15000
        num_chunks = len(audio) // chunk_length_ms
        complete_transcript = ""

        for i in range(num_chunks):
            start = i * chunk_length_ms
            end = (i + 1) * chunk_length_ms
            chunk = audio[start:end]

            # Export chunk to temporary file
            chunk_filename = f"temp_chunk_{i}.wav"
            chunk.export(chunk_filename, format="wav")

            # Transcribe chunk
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 150
            with sr.AudioFile(chunk_filename) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language="en-US")
                    chunk_transcript = text
                except (sr.UnknownValueError, sr.RequestError):
                    chunk_transcript = ""

            complete_transcript += chunk_transcript + " "
            os.remove(chunk_filename)

        return complete_transcript.strip()

    except Exception as e:
        st.error(f"Error processing audio chunks: {str(e)}")
        return "Error in audio transcription. Please submit a text file instead."