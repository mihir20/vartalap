# Audio Recorder and Transcriber

This project is an audio recording and transcription application built with Python and Tkinter. It allows users to record audio, save it as a `.wav` file, and transcribe the audio into text using a transcription model.

## Features

- Record audio and save it as a `.wav` file.
- Transcribe recorded audio into text.
- Save transcriptions with timestamps.
- Apply markdown formatting to transcriptions.

## Requirements

- Python 3.x
- Tkinter
- Sounddevice
- Numpy
- Soundfile

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/mihir20/vartalap.git
    cd vartalap
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
3. (Optional) If you want to use OpenAI for summarization, set the `OPENAI_API_KEY` environment variable:
    ```sh
    export OPENAI_API_KEY=your_openai_api_key

## Usage

1. Run the application:
    ```sh
    python main.py
    ```
2. Select the AI API you want to use (MetaAI or OpenAI-recommended) from the dropdown menu.

3. Use the GUI to start and stop recording.

## Note on API Usage

MetaAI has limitations on the number of characters in the prompt, which may cause it to fail when summarizing large meetings. To avoid this issue, it is recommended to set the `OPENAI_API_KEY` and use OpenAI for summarization.

## Project Structure

- `main.py`: The main application file.
- `.gitignore`: Git ignore file.
- `README.md`: Project documentation.

## License

This project is licensed under the MIT License.