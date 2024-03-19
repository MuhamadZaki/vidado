from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from googletrans import Translator
import os
from google.cloud import speech_v1p1beta1 as speech
import math

# Path ke file kunci JSON
credential_path = "C:/Users/ThinkPad\Documents/path/name_files.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# Ekstrak audio dari video
video_path = 'fakyu.mp4'
audio_file = 'extracted_audio.wav'

try:
    # Load video clip
    video = VideoFileClip(video_path)
    
    # Ekstrak audio dari video
    audio = video.audio
    audio.write_audiofile(audio_file)

    # Inisialisasi klien Speech-to-Text
    client = speech.SpeechClient()

    # Konfigurasi transkripsi audio
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="en-US",
    )

    # Membagi audio menjadi bagian-bagian yang tidak lebih besar dari 10 MB
    max_chunk_size = 9 * 1024 * 1024  # 10 MB (maksimum ukuran per bagian)
    total_file_size = os.path.getsize(audio_file)
    num_chunks = math.ceil(total_file_size / max_chunk_size)

    for i in range(num_chunks):
        start_byte = i * max_chunk_size
        end_byte = min((i + 1) * max_chunk_size, total_file_size)

        with open(audio_file, 'rb') as audio_file:
            audio_file.seek(start_byte)
            audio_chunk = audio_file.read(end_byte - start_byte)
            audio = speech.RecognitionAudio(content=audio_chunk)
            response = client.recognize(config=config, audio=audio)
            # Proses respons di sini

    # Periksa keberadaan file
    if os.path.isfile(audio_file):
        os.remove(audio_file)  # Hapus file audio jika sudah selesai digunakan

    # Melakukan transkripsi audio
    text = ""
    for result in response.results:
        text += result.alternatives[0].transcript

    print("Transkripsi: ", text)

    # Terjemahkan teks menggunakan Google Trans
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest='id').text
    print("Teks Terjemahan: ", translated_text)

    # Membuat subtitle dalam bentuk TextClip
    # Mengatur durasi subtitle sesuai dengan durasi video
    subtitle_clip_en = (TextClip(text, fontsize=24, color='white', font="Arial-Bold", size=video.size)
                        .set_position('bottom')
                        .set_duration(video.duration))

    subtitle_clip_id = (TextClip(translated_text, fontsize=24, color='white', font="Arial-Bold", size=video.size)
                        .set_position('bottom')
                        .set_duration(video.duration))

    # Membuat video komposit yang menyertakan subtitle
    final_clip = CompositeVideoClip([video.set_duration(subtitle_clip_en.duration), subtitle_clip_en.set_start(0),
                                     video.set_duration(subtitle_clip_id.duration), subtitle_clip_id.set_start(0)])

    # Ekspor video akhir dengan subtitle
    final_clip.write_videofile("video_with_subtitle.mp4", codec='libx264', audio_codec="aac")

except Exception as e:
    print("Error:", e)
