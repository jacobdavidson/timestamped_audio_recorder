import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime, timezone
import numpy as np
import argparse
import sys

# Function to convert datetime to formatted string
def dt_to_str(dt):
    """Converts a datetime object to a formatted string."""
    isoformat = "%Y-%m-%dT%H_%M_%S"
    dt_str = dt.strftime(isoformat)
    if dt.microsecond != 0:
        dt_str += ".{:06d}".format(dt.microsecond)
    if dt.tzinfo is not None and dt.utcoffset().total_seconds() == 0:
        dt_str += "Z"
        return dt_str
    else:
        return dt_str

# Function to generate timestamped filename
def get_timestamped_filename(prefix, use_utc=False):
    if use_utc:
        now = datetime.now(timezone.utc)
    else:
        now = datetime.now()
    timestamp_str = dt_to_str(now)
    filename = f"{prefix}_{timestamp_str}.wav"
    return filename

# Function to record audio chunk
def record_audio_chunk(duration, fs, channels, device=None):
    print(f"Recording audio chunk for {duration} seconds...")
    try:
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype='int16', device=device)
        sd.wait()  # Wait for the recording to finish
    except Exception as e:
        print(f"An error occurred during recording: {e}")
        sys.exit(1)
    return audio_data

# Function to save audio data to a file
def save_audio(filename, fs, audio_data):
    try:
        write(filename, fs, audio_data)
        print(f"Recording saved as {filename}")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")
        sys.exit(1)

# Main function
def main():
    parser = argparse.ArgumentParser(description="Continuous Audio Recording Script")
    parser.add_argument('-d', '--duration', type=float, default=60, help='Duration of each recording chunk in seconds')
    parser.add_argument('-t', '--total-duration', type=float, help='Total duration of recording in seconds (default: runs indefinitely until cancelled)')
    parser.add_argument('-r', '--samplerate', type=int, default=44100, help='Sampling rate in Hz')
    parser.add_argument('-c', '--channels', type=int, default=2, help='Number of audio channels')
    parser.add_argument('--device', type=int, help='Device index for recording')
    parser.add_argument('--print-devices', action='store_true', help='Print list of audio devices and exit')
    parser.add_argument('--prefix', type=str, default='audio_recording', help='Custom prefix for the filename')
    parser.add_argument('--use-utc', action='store_true', help='Use UTC time for the filename timestamp (default is local time)')
    args = parser.parse_args()

    if args.print_devices:
        print("Available audio devices:")
        print(sd.query_devices())
        sys.exit(0)

    start_time = datetime.now()
    elapsed_time = 0

    try:
        while True:
            # Check if total duration is specified and if elapsed time exceeds it
            if args.total_duration and elapsed_time >= args.total_duration:
                print("Total recording duration reached. Exiting.")
                break

            filename = get_timestamped_filename(args.prefix, use_utc=args.use_utc)
            audio_data = record_audio_chunk(args.duration, args.samplerate, args.channels, device=args.device)
            save_audio(filename, args.samplerate, audio_data)

            elapsed_time = (datetime.now() - start_time).total_seconds()
    except KeyboardInterrupt:
        print("\nRecording interrupted by user. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
