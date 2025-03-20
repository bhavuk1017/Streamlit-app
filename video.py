import streamlit as st
import os
import requests
from moviepy.editor import VideoFileClip

st.title("Video Transcription")

uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])

if uploaded_file:
    try:
        # Save the video file
        video_path = "temp_video." + uploaded_file.name.split(".")[-1]
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())

        # Extract audio from video
        video_clip = VideoFileClip(video_path)
        audio_path = "temp_audio.wav"
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path)
        audio_clip.close()
        video_clip.close()

        # Transcribe audio with speech_recognition
        import speech_recognition as sr

        def convert_audio_to_text(audio_file):
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 150
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language="en-IN")
                    st.write(f"Speech Recognition output: {text}")
                    return text
                except sr.UnknownValueError:
                    st.write("Speech Recognition could not understand audio")
                    return ""
                except sr.RequestError as e:
                    st.write(f"Could not request results from Speech Recognition service; {e}")
                    return ""
            

        def transcribe_audio_chunks(audio_path):
            try:
                from pydub import AudioSegment
                import speech_recognition as sr
                import os

                # Load audio file
                audio = AudioSegment.from_wav(audio_path)

                # Set chunk length (in milliseconds)
                chunk_length_ms = 15000

                # Get the number of chunks
                num_chunks = len(audio) // chunk_length_ms

                # Initialize the complete transcript
                complete_transcript = ""

                # Iterate through the chunks
                for i in range(num_chunks):
                    start = i * chunk_length_ms
                    end = (i + 1) * chunk_length_ms
                    chunk = audio[start:end]

                    # Export the chunk to a temporary file
                    chunk_filename = f"temp_chunk_{i}.wav"
                    chunk.export(chunk_filename, format="wav")

                    # Transcribe the chunk
                    recognizer = sr.Recognizer()
                    recognizer.energy_threshold = 150
                    with sr.AudioFile(chunk_filename) as source:
                        audio_data = recognizer.record(source)
                        try:
                            text = recognizer.recognize_google(audio_data, language="en-US")
                            chunk_transcript = text
                        except sr.UnknownValueError:
                            chunk_transcript = ""
                        except sr.RequestError as e:
                            chunk_transcript = ""

                    # Append the chunk transcript to the complete transcript
                    complete_transcript += chunk_transcript + " "

                    # Remove the temporary chunk file
                    os.remove(chunk_filename)

                return complete_transcript

            except Exception as e:
                st.error(f"Error processing audio chunks: {e}")
                return ""

        st.write("Starting speech recognition...")
        transcript = transcribe_audio_chunks(audio_path)
        st.write("Speech recognition complete.")

        # Clean up temporary files
        os.remove(video_path)
        os.remove(audio_path)

        st.subheader("Transcript:")
        st.write(transcript)

    except Exception as e:
        st.error(f"Error: {e}")
