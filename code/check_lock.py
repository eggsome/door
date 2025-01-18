import warnings
warnings.filterwarnings("ignore", message=".*joblib will operate in serial mode.*")
import librosa
import noisereduce as nr
import numpy as np
from fastdtw import fastdtw
import sys


def reduce_noise(input_file):
    """
    Reduce noise in an audio file using noisereduce.
    """
    y, sr = librosa.load(input_file, sr=None)
    if len(y) < sr:
        raise ValueError(f"Audio file {input_file} is shorter than 1 second.")
    
    # Extract a noise profile from the first second of audio
    noise_sample = y[:sr]
    
    # Apply noise reduction
    reduced_noise = nr.reduce_noise(y=y, sr=sr, y_noise=noise_sample)
    
    return reduced_noise, sr


def extract_features(y, sr):
    """
    Extract Mel spectrogram features for comparison.
    """
    try:
        # Extract Mel spectrogram
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40)
        log_mel_spec = librosa.power_to_db(mel_spec)

        # Normalize globally
        features = (log_mel_spec - np.mean(log_mel_spec)) / np.std(log_mel_spec)
        return features
    except Exception as e:
        raise ValueError(f"Feature extraction failed: {e}")


def calculate_similarity(file1_path, file2_path):
    """
    Calculate similarity between two audio files using enhanced features and DTW.
    """
    y1, sr1 = reduce_noise(file1_path)
    y2, sr2 = reduce_noise(file2_path)

    # Ensure sampling rates match
    if sr1 != sr2:
        y2 = librosa.resample(y2, orig_sr=sr2, target_sr=sr1)
        sr2 = sr1

    # Extract features
    features1 = extract_features(y1, sr1)
    features2 = extract_features(y2, sr2)

    # Check if features are valid
    if features1.shape[1] == 0 or features2.shape[1] == 0:
        raise ValueError("Feature matrices are empty. Check audio preprocessing.")

    # Compute DTW distance
    distance, path = fastdtw(features1.T, features2.T, dist=lambda x, y: np.linalg.norm(x - y))

    # Normalize DTW distance by path length
    normalized_distance = distance / len(path)

    # Debugging: Log normalized DTW distance
    print(f"Normalized DTW Distance: {normalized_distance}")

    # Calculate similarity with adaptive scaling
    scaling_factor = 10  # Adjust based on typical DTW ranges observed
    similarity = max(0, 1 - (normalized_distance / scaling_factor))
    print(f"Similarity Score: {similarity}")

    return similarity


def main():
    test_file = "/root/test.wav"
    known_good_file1 = "/root/unlocked.wav"
    known_good_file2 = "/root/locked.wav"

    # Calculate similarity scores
    try:
        similarity_score1 = calculate_similarity(known_good_file1, test_file)
        similarity_score2 = calculate_similarity(known_good_file2, test_file)
    except Exception as e:
        print(f"Error during similarity calculation: {e}")
        sys.exit(1)

    print(f"Similarity Score (unlocked.wav vs test.wav): {similarity_score1:.2f}")
    print(f"Similarity Score (locked.wav vs test.wav): {similarity_score2:.2f}")

    similarity_score1 = round(similarity_score1, 2)
    similarity_score2 = round(similarity_score2, 2)

    # Threshold check
    match1 = similarity_score1 >= 0.30
    match2 = similarity_score2 >= 0.30
    
    # If both samples roughly match the latest recording, then pick the best match
    if match1 and match2:
        sys.exit(10 if similarity_score1 >= similarity_score2 else 11)
    # If we match 
    elif match1:
        sys.exit(10)
    # If we match 
    elif match2:
        sys.exit(11)
    # There is no match 
    else:
        sys.exit(21)


if __name__ == "__main__":
    main()
