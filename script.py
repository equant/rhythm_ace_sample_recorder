import threading
import sounddevice as sd
import numpy as np
import wavio

from patterns import *

#print(sd.query_devices())

def list_audio_devices():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"Device ID: {i}")
        print(f"  Name: {device['name']}")
        print(f"  Max Input Channels: {device['max_input_channels']}")
        print(f"  Max Output Channels: {device['max_output_channels']}")
        print(f"  Default Sample Rate: {device['default_samplerate']}")
        print("---")

def record_audio(filename, duration, samplerate, device=5):
    print()
    print(f"Ready to record: {filename}")
    input("Press Enter to start recording.")

    print(f"Recording {duration} seconds...")
    
    audio_data = sd.rec(
                        int(samplerate * duration),
                        samplerate=samplerate,
                        channels=2,
                        dtype='int16',
                        device=device
    )

    sd.wait()
    print(f"...saved.")
    print()
    
    silenced_audio_data = remove_starting_silence(audio_data)

    peak_value = np.max(np.abs(audio_data))
    target_peak = 32767 * 10**(-3 / 20)

    if peak_value < target_peak:
        try:
            normalization_factor = target_peak / peak_value
            normalized_audio = audio_data * normalization_factor
            wavio.write(f"recordings/normalized/{filename}_lowout.wav", silenced_audio_data[:, 0], samplerate, sampwidth=2)
            wavio.write(f"recordings/normalized/{filename}_highout.wav", silenced_audio_data[:, 1], samplerate, sampwidth=2)
        except:
            pass
    
    left_channel = audio_data[:, 0]
    right_channel = audio_data[:, 1]

    wavio.write(f"recordings/raw/{filename}_lowout.wav", left_channel, samplerate, sampwidth=2)
    wavio.write(f"recordings/raw/{filename}_highout.wav", right_channel, samplerate, sampwidth=2)
    try:
        wavio.write(f"recordings/leading_silence_removed/{filename}_lowout.wav", silenced_audio_data[:, 0], samplerate, sampwidth=2)
        wavio.write(f"recordings/leading_silence_removed/{filename}_highout.wav", silenced_audio_data[:, 1], samplerate, sampwidth=2)
    except:
        pass
    print(f"Saved {filename}_lowout.wav and {filename}_highout.wav")
    return audio_data

#def remove_silence(audio_data, threshold=1000):
    #audio_abs = np.abs(audio_data)
    #silence_removed = audio_data[np.max(audio_abs, axis=1) > threshold]
    #return silence_removed

def remove_starting_silence(audio_data, silence_threshold=1000):
    for i, sample in enumerate(audio_data):
        if np.linalg.norm(sample) > silence_threshold:
            return audio_data[i:]
    return np.array([])  # return empty array if all samples are silent

if __name__ == "__main__":
    # Ask for the BPM
    list_audio_devices()
    print()

    bpm = input("Tell me the bpm: ")
    
    # Want to record for n loops
    n_loops = 10
    #n_loops = 5
    beats = n_loops * 4
    minutes = 1/int(bpm) * beats
    duration = int(minutes * 60 + 1.5) # seconds
    samplerate = 44100  # Hertz
    
    patterns = beat_patterns + latin_patterns + top_row_patterns
    patterns = latin_patterns + top_row_patterns
    #patterns = latin_patterns
    
    # Recording loop
    for pattern in patterns:
        #record_audio(f"{pattern}_{bpm}-noBass", duration, samplerate)
        record_audio(f"{pattern}_{bpm}-noBass-noSnare-noCymbal-noGuiro", duration, samplerate)
        #record_audio(f"{pattern}_{bpm}", duration, samplerate)
