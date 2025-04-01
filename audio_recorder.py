import sounddevice as sd
import soundfile as sf
from datetime import datetime, timezone, timedelta
import argparse
import sys
from pathlib import Path
import queue
import threading
import time
import shutil

################################################################################
# Utility functions
################################################################################

def dt_to_str(dt):
    """
    Converts a datetime object to a formatted string such that if you join
    all files, they'd sort properly in time order. Includes microseconds
    and UTC 'Z' suffix if dt is UTC.
    """
    isoformat = "%Y-%m-%dT%H_%M_%S"
    dt_str = dt.strftime(isoformat)
    if dt.microsecond != 0:
        dt_str += ".{:06d}".format(dt.microsecond)
    if dt.tzinfo is not None and dt.utcoffset().total_seconds() == 0:
        dt_str += "Z"
    return dt_str

def get_timestamped_filename(prefix, directory, use_utc=False):
    """
    Generates a timestamped .wav filename in the given directory.
    If use_utc is True, the timestamp is in UTC; otherwise local time.
    """
    if use_utc:
        now = datetime.now(timezone.utc)
    else:
        now = datetime.now()
    timestamp_str = dt_to_str(now)
    filename = f"{prefix}_{timestamp_str}.wav"
    return directory / filename

################################################################################
# Global variables for the audio callback
################################################################################
audio_queue = queue.Queue()  # This queue gets audio data from the callback

def audio_callback(indata, frames, time_info, status):
    """SoundDevice callback: push received audio blocks into audio_queue."""
    if status:
        print(status, file=sys.stderr)
    # Copy so we don't lose data if SoundDevice reuses the buffer
    audio_queue.put(indata.copy())

################################################################################
# Writer thread logic
################################################################################

def writer_thread_func(control_queue, samplerate, channels, subtype, prefix,
                       use_utc, tmp_dir, out_dir):
    """
    Continuously reads raw audio blocks from `audio_queue` and writes into
    the *current* WAV file. The main thread signals chunk rotations or
    termination by putting commands in `control_queue`:
      - "ROTATE": close current file, move it to out_dir, open a new one in tmp_dir
      - "STOP":   close file, move it, then break out of loop
    """
    current_sf = None
    current_tmp_path = None

    while True:
        # 1) Check if there's a control command (e.g. "ROTATE", "STOP").
        try:
            command = control_queue.get_nowait()
        except queue.Empty:
            command = None

        if command == "STOP":
            # Close any open file and move it to final output
            if current_sf is not None:
                current_sf.close()
                if current_tmp_path and current_tmp_path.exists():
                    final_path = out_dir / current_tmp_path.name
                    shutil.move(str(current_tmp_path), str(final_path))
            break

        elif command == "ROTATE":
            # 1) Close the old file and move it to out_dir
            if current_sf is not None:
                current_sf.close()
                if current_tmp_path and current_tmp_path.exists():
                    final_path = out_dir / current_tmp_path.name
                    shutil.move(str(current_tmp_path), str(final_path))

            # 2) Open a brand new .wav file in the tmp_dir
            current_tmp_path = get_timestamped_filename(prefix, tmp_dir, use_utc)
            current_sf = sf.SoundFile(
                str(current_tmp_path),
                mode='x',
                samplerate=samplerate,
                channels=channels,
                subtype=subtype
            )

        # 2) If we have an open file, write frames from the audio_queue
        if current_sf is not None:
            try:
                # Try to get up to 0.1 seconds worth of data from the queue
                block = audio_queue.get(timeout=0.1)
                current_sf.write(block)
            except queue.Empty:
                # No data available in the queue yet
                pass

################################################################################
# Main function
################################################################################

def main():
    parser = argparse.ArgumentParser(description="Continuous Audio Recorder with gapless chunk rotation.")
    parser.add_argument('-d', '--duration', type=float, required=True,
                        help='Duration of each recording chunk in seconds.')
    parser.add_argument('-t', '--total-duration', type=float,
                        help='Total duration of recording in seconds (default: infinite).')
    parser.add_argument('-r', '--samplerate', type=int,
                        help='Sampling rate in Hz (default: device default).')
    parser.add_argument('-c', '--channels', type=int,
                        help='Number of audio channels (default: device max).')
    parser.add_argument('--device', type=int,
                        help='Device index for recording (REQUIRED).')
    parser.add_argument('--prefix', type=str, default='audio_recording',
                        help='Custom prefix for the filename.')
    parser.add_argument('--use-utc', action='store_true',
                        help='Use UTC time for the filename timestamp (default is local).')
    parser.add_argument('--out-dir', type=str, default='out',
                        help='Final output directory (default: ./out).')
    parser.add_argument('--tmp-dir', type=str, default='tmp',
                        help='Temporary directory for active recording (default: ./tmp).')
    parser.add_argument('--subtype', type=str, default='PCM_16',
                        help='Sound file subtype (e.g., PCM_16, PCM_24, FLOAT).')
    parser.add_argument('--print-devices', action='store_true',
                        help='Print list of audio devices and exit.')
    parser.add_argument('--print-subtypes', action='store_true',
                        help='Print list of available soundfile subtypes and exit.')
    args = parser.parse_args()

    # If just printing device info or subtypes, do so and exit
    if args.print_devices:
        print("Available audio devices:")
        print(sd.query_devices())
        sys.exit(0)
    if args.print_subtypes:
        print("Available sound file subtypes:")
        print(sf.available_subtypes())
        sys.exit(0)

    if args.device is None:
        print("Error: No recording device specified. Use --device <index>.")
        sys.exit(1)

    # Make sure out_dir and tmp_dir exist
    out_dir = Path(args.out_dir)
    tmp_dir = Path(args.tmp_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Determine samplerate/channels from device if not provided
    if args.samplerate is None or args.channels is None:
        device_info = sd.query_devices(args.device, 'input')
        if args.samplerate is None:
            args.samplerate = int(device_info['default_samplerate'])
        if args.channels is None:
            args.channels = device_info['max_input_channels']

    # Start the writer thread:
    control_queue = queue.Queue()
    writer_thread = threading.Thread(
        target=writer_thread_func,
        args=(
            control_queue,
            args.samplerate,
            args.channels,
            args.subtype,
            args.prefix,
            args.use_utc,
            tmp_dir,
            out_dir
        ),
        daemon=True
    )
    writer_thread.start()

    # Immediately tell the writer to open the first chunk file
    control_queue.put("ROTATE")

    print("#" * 80)
    print("Recording... Press Ctrl+C to stop.")
    print(f"Chunk duration = {args.duration} sec")
    print(f"Writing temporary chunks in: {str(tmp_dir)}")
    print(f"Moving finished chunks into: {str(out_dir)}")
    print("#" * 80)

    start_time = time.time()
    next_rotate_time = start_time + args.duration

    try:
        with sd.InputStream(
            samplerate=args.samplerate,
            device=args.device,
            channels=args.channels,
            callback=audio_callback
        ):
            while True:
                current_time = time.time()

                # If chunk time has passed, rotate to a new file
                if current_time >= next_rotate_time:
                    control_queue.put("ROTATE")
                    next_rotate_time += args.duration

                # If total-duration was specified, check if we've passed it
                if args.total_duration is not None:
                    if (current_time - start_time) >= args.total_duration:
                        print("Total recording duration reached. Exiting loop.")
                        break

                # Sleep briefly to avoid busy-wait
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nRecording interrupted by user (Ctrl+C).")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

    finally:
        # Stop the writer thread
        control_queue.put("STOP")
        writer_thread.join()
        print("Writer thread stopped. All chunks finalized.")
        print("Exiting.")


if __name__ == "__main__":
    main()