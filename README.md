
# Timestamped Audio Recorder

A Python script for continuous audio recording in timestamped chunks. This tool allows you to record audio continuously, splitting the recordings into manageable chunks with precise timestamps in the filenames.

## Features

- **Continuous Recording**: Record audio indefinitely or for a specified total duration.
- **Chunked Recording**: Split recordings into chunks of a specified duration.
- **Timestamped Filenames**: Save recordings with precise UTC timestamps, including microseconds.
- **Device Selection**: Choose the audio input device for recording.
- **Customizable Parameters**: Adjust sampling rate, number of channels, and more via command-line arguments.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Listing Audio Devices](#listing-audio-devices)
  - [Specifying Recording Parameters](#specifying-recording-parameters)
  - [Examples](#examples)
- [Filename Format](#filename-format)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/timestamped-audio-recorder.git
   cd timestamped-audio-recorder
   ```

2. **Install Required Libraries**


   ```bash
   pip install sounddevice soundfile
   ```

**Note:** in case you get issues with PortAudio when trying the audio_recorder, try installing sounddevice via conda-forge instread

```bash
conda install -c conda-forge python-sounddevice
```

## Usage

### Basic Usage

Run the script with default settings:

```bash
python audio_recorder.py
```

This command will:

- Record audio indefinitely until you stop the script (`Ctrl+C`).
- Record in chunks of **60 seconds** (this is the default, it can be changed).
- Use the default audio input device.
- Save recordings in the current directory with timestamped filenames.

### Listing Audio Devices

To list all available audio input devices:

```bash
python audio_recorder.py --print-devices
```

**Example Output:**

```
Available audio devices:
   0 BlackHole 2ch, Core Audio (2 in, 2 out)
   1 MacBook Pro Microphone, Core Audio (1 in, 0 out)
   2 MacBook Pro Speakers, Core Audio (0 in, 2 out)
>  3 External Microphone, Core Audio (1 in, 0 out)
<  4 External Microphone, Core Audio (0 in, 2 out)
```

- Use the device index (e.g., `1`) to specify the recording device.

### Specifying Recording Parameters

You can customize the recording using various command-line arguments:

- **Chunk Duration** (`-d` or `--duration`): Duration of each recording chunk in seconds.
- **Total Duration** (`-t` or `--total-duration`): Total duration of recording in seconds. If not specified, the script runs indefinitely until cancelled.
- **Sampling Rate** (`-r` or `--samplerate`): Sampling rate in Hertz. Default is the maximum samplerate of the selected device if not provided.
- **Channels** (`-c` or `--channels`): Number of audio channels. Default is the maximum number of input channels of the selected device if not provided.
- **Device** (`--device`): Device index for recording. Use `--print-devices` to find the index.
- **Output Directory** (`--output-dir`): Directory where recordings are saved. Default is the current directory (`.`).
- **Prefix** (`--prefix`): Custom prefix for the filename. Default is `audio_recording`.
- **Use UTC Time** (`--use-utc`): Use UTC time for the filename timestamp. By default, local time is used.
- **Align Chunks** (`--align-chunks`): Align recording chunks to specific time boundaries.
- **File Subtype** (`--subtype`): Specify the sound file subtype (e.g., `PCM_16`, `PCM_24`, `FLOAT`). Default is `PCM_16`.
- **Print Available Subtypes** (`--print-subtypes`): Print a list of available sound file subtypes and exit.
- **Help** (`-h` or `--help`): Show help message and exit.

### Examples

**Record in 30-Second Chunks Indefinitely**

```bash
python audio_recorder.py -d 30
```

**Record in 10-Second Chunks for a Total of 5 Minutes**

```bash
python audio_recorder.py -d 10 -t 300
```

**Record Using a Specific Device**

```bash
python audio_recorder.py --device 1
```

**Record Mono Audio at 48 kHz**

```bash
python audio_recorder.py -c 1 -r 48000
```

**Combine Multiple Parameters**

```bash
python audio_recorder.py -d 15 -t 120 --device 3 -c 1 -r 48000
```

This command records mono audio at 48 kHz using device index `3`, in 15-second chunks, for a total of 2 minutes.

### Filename Format

Recordings are saved with filenames in the following format:

Example: `audio_recording_2023-10-01T14_30_45.123456Z.wav`

Components:
- `<prefix>`: Customizable prefix for the filename (default is `audio_recording`).
- `YYYY-MM-DD`: Year, month, and day.
- `T`: Separator indicating the start of the time component.
- `HH_MM_SS`: Hour, minute, and second.
- `.microseconds`: Microseconds (if not zero).
- `Z`: Indicates that the time is in UTC if the `--use-utc` option is used.

**Note**: The timestamps can be in either Coordinated Universal Time (UTC) or local time, depending on the `--use-utc` parameter.


## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software in accordance with the license terms.

---

**Disclaimer**: Use this software responsibly and ensure compliance with local laws and regulations regarding audio recording and privacy.


