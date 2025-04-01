
# Timestamped Audio Recorder

A Python script for continuous audio recording in timestamped chunks. This tool allows you to record audio continuously, splitting the recordings into manageable chunks with precise timestamps in the filenames. Recorded audio data is first written to a temporary directory and then moved to the final output directory, ensuring no dropouts in between chunks.

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
   git clone https://github.com/jacobdavidson/timestamped-audio-recorder.git
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
python audio_recorder.py --device <DEVICE_INDEX> -d <CHUNK_DURATION>
```

For example, if --device 0 is available, you might do:

```bash
python audio_recorder.py --device 0 -d 60
```

This command will:

- Record audio from device 0, chunked into 60-second files.
- Run indefinitely until you stop the script (Ctrl+C).
- First write the active chunk in the tmp/ directory, then move it to the out/ directory once it’s done.
- Save the recordings with timestamped filenames.

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

- **Chunk Duration** (-d or --duration): Duration of each recording chunk in seconds (required).
- **Total Duration** (-t or --total-duration): Total duration of recording in seconds. If not specified, the script runs until you press Ctrl+C.
- **Sampling Rate** (-r or --samplerate): Sampling rate in Hertz. Defaults to the device’s default sample rate if not specified.
- **Channels** (-c or --channels): Number of input channels (e.g., mono=1, stereo=2). Defaults to device’s max input channels if not specified.
- **Device** (--device): Device index for recording (required).
- **Prefix** (--prefix): Custom prefix for each filename (default: audio_recording).
- **Use UTC Time** (--use-utc): Use UTC timestamps in filenames (default is local time).
- **Output Directory** (--out-dir): Final directory to store completed .wav files (default: out).
- **Temporary Directory** (--tmp-dir): Directory to store the actively recorded chunk (default: tmp).
- **File Subtype** (--subtype): Sound file subtype (e.g. PCM_16, PCM_24, FLOAT). Default is PCM_16.
- **Print Available Subtypes** (--print-subtypes): List the supported file subtypes and exit.
- **Print Devices** (--print-devices): List the available audio devices and exit.
- **Help** (-h or --help): Show help message and exit.


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



