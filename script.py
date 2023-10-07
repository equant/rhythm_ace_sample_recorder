import threading
from pynput import keyboard
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

def on_key_release(key, lock, skip_lock):
    if key == keyboard.Key.space:
        lock.set()
    elif key == keyboard.KeyCode.from_char('s'):
        skip_lock.set()

def record_audio(filename, duration, samplerate, device=5):
    print()
    print(f"Ready to record: {filename}")
    print("Press Space to start recording or 's' to skip...")

    lock = threading.Event()
    skip_lock = threading.Event()

    with keyboard.Listener(on_release=lambda key: on_key_release(key, lock, skip_lock)) as listener:
        lock.wait()
        if skip_lock.is_set():
            print("Skipping...")
            return

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
    
    # Remove silence at the beginning
    #audio_data = remove_silence(audio_data)
    
    # Split channels and save
    left_channel = audio_data[:, 0]
    right_channel = audio_data[:, 1]

    wavio.write(f"{filename}_lowout.wav", left_channel, samplerate, sampwidth=2)
    wavio.write(f"{filename}_highout.wav", right_channel, samplerate, sampwidth=2)
    
    print(f"Saved {filename}_lowout.wav and {filename}_highout.wav")

def remove_silence(audio_data, threshold=1000):
    audio_abs = np.abs(audio_data)
    silence_removed = audio_data[np.max(audio_abs, axis=1) > threshold]
    return silence_removed

if __name__ == "__main__":
    # Ask for the BPM
    list_audio_devices()
    print()

    bpm = input("Tell me the bpm: ")
    
    # Want to record for n loops
    n_loops = 10
    beats = n_loops * 4
    minutes = 1/int(bpm) * beats
    duration = int(minutes * 60 + 1.5) # seconds
    samplerate = 44100  # Hertz
    
    #patterns = ['Rock and Roll 1', 'Rock and Roll 2', 'Jazz', 'Blues']
    patterns = top_row_patterns
    
    components = ['Cymbal', 'Guiro', 'Bass', 'Snare']
    
    # Recording loop
    for pattern in patterns:
        record_audio(f"{pattern}_{bpm}", duration, samplerate)
        
        #for component in components:
            #record_audio(f"{pattern}_{component}_{bpm}", duration, samplerate)

