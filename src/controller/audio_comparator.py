import numpy as np 
import librosa 
import os

from pydub import AudioSegment

class AudioComparator:
    def compare_audio(self, audio_original, audio_recorded):
        print("Comparing audio files:", audio_original, audio_recorded)
        parts_original = self.chunk_audio(audio_original)
        print("Original parts:", parts_original)
        parts_recorded = self.chunk_audio(audio_recorded)
        print("Recorded parts:", parts_recorded)
        summary = []
        for i, part in enumerate(parts_original):
            deviation = 100.0
            if i < len(parts_recorded):
                deviation = self.compare_features(part, parts_recorded[i])
            summary.append({
                "second": i,
                "deviation": float(deviation)
            })
        print(summary)
        return summary

    def chunk_audio(self, audio_path):
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        chunk_length_ms = 1000  # ms
        chunks = []
        base, _ = os.path.splitext(audio_path)
        for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
            chunk = audio[start:start+chunk_length_ms]
            chunk_path = f"{base}_chunk{i+1}.wav"
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
        return chunks
    
#    def convert_to_spectrogram(self, audio_path):
#        audio = AudioSegment.from_file(audio_path)
#        return audio.get_array_of_samples()

    def compare_features(self, audio_original, audio_recorded):
        features_original = self.extract_features(audio_original)
        features_recorded = self.extract_features(audio_recorded)
        # Compute the Euclidean distance between the feature vectors
        return np.linalg.norm(features_original - features_recorded)

    def extract_features(self, file_path): 
        y, sr = librosa.load(file_path, sr=None)
        # Extract MFCCs 
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        # Take the mean of the MFCCs across time
        return np.mean(mfccs.T, axis=0)
