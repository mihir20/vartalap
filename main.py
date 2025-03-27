import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
import threading
import queue
from datetime import datetime
import os
from meta_ai_api import MetaAI
from openai import OpenAI

prompt = '''
You are an AI Meeting Summarizer. Analyze the following meeting transcription and generate a comprehensive summary.

**Transcription:**

{}

**Instructions:**

1.  **Generate a concise summary** of the meeting, highlighting the main topics and key discussions.
2.  **Identify and list all action items**, including who is responsible and any deadlines mentioned. Format them as: "Action Item: [Action], Responsible: [Name], Deadline: [Date]".
3.  **Extract and list all key decisions** made during the meeting.
4.  **List the main speakers** and briefly mention their contributions.
5.  **Identify and list key keywords and topics** discussed.
6.  **Perform sentiment analysis** to determine the overall tone of the meeting (e.g., positive, negative, neutral, mixed).
7.  **Provide a longer more detailed summary** of the meeting.
8.  **If possible, provide a list of questions that were asked, and their answers.**

output should strictly follow specified Output Format

**Output Format:**

**Meeting Summary (Concise):**
[Concise summary here]

**Action Items:**
[Action item list here]

**Key Decisions:**
[Decision list here]

**Speakers:**
[Speaker list here]

**Keywords/Topics:**
[Keyword/topic list here]

**Sentiment Analysis:**
[Sentiment analysis here]

**Meeting Summary (Detailed):**
[Detailed summary here]

**Questions and Answers:**
[Question and answer list here]
'''

class AudioRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vartalap - AI Meeting Summarizer")
        self.recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        self.transcription_thread = None
        self.token_limit = 40000

        # Create GUI Elements
        # First create status label before using it
        self.status_label = ttk.Label(root, text="Status: Initializing...")
        self.status_label.pack(pady=5)

        # API Selection
        ai_options = ["MetaAI"]
        default_ai = "MetaAI"  # Default API choice
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and len(api_key) != 0:
            default_ai = "OpenAI"
            ai_options = ["OpenAI", "MetaAI"]
        self.api_choice = tk.StringVar(value=default_ai)  # Default API choice
        api_frame = ttk.Frame(root)
        api_frame.pack(pady=5)

        api_label = ttk.Label(api_frame, text="Select AI API:")
        api_label.pack(side=tk.LEFT, padx=5)

        api_dropdown = ttk.Combobox(api_frame, textvariable=self.api_choice, values=ai_options, state="readonly", width=10)
        api_dropdown.pack(side=tk.LEFT, padx=5)
        api_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_ai_client())

        # initialize AI client after status_label is created
        self.ai = None
        self.update_ai_client()

        # Record button
        self.record_button = ttk.Button(root, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(pady=10)

        # Text area
        self.text_area = tk.Text(root, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(pady=10, padx=10)

        # Configure text area tags for Markdown formatting
        self.text_area.tag_configure("bold", font=("Arial", 10, "bold"))
        self.text_area.tag_configure("italic", font=("Arial", 10, "italic"))
        self.text_area.tag_configure("heading1", font=("Arial", 16, "bold"))
        self.text_area.tag_configure("heading2", font=("Arial", 14, "bold"))
        self.text_area.tag_configure("code", font=("Courier", 10), background="#f0f0f0")

        # Initialize Whisper model
        self.status_label.config(text="Status: Loading model...")
        self.root.update()
        try:
            self.model = whisper.load_model("tiny")
            self.status_label.config(text=f"Status: Ready (Using {self.api_choice.get()})")
        except Exception as e:
            self.status_label.config(text=f"Error loading model: {e}")

    def update_ai_client(self):
        """Update the AI client based on user selection"""
        selection = self.api_choice.get()
        if selection == "MetaAI":
            self.ai = MetaAI()
        else:  # OpenAI
            self.ai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Update status label if it exists
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"Status: Using {selection}")

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.record_button.config(text="Stop Recording")
        self.status_label.config(text=f"Status: Recording... (Using {self.api_choice.get()})")
        self.recording_thread = RecordingThread(self.audio_queue)
        self.recording_thread.start()

    def stop_recording(self):
        self.recording = False
        self.record_button.config(text="Start Recording")
        self.status_label.config(text=f"Status: Stopping... (Using {self.api_choice.get()})")
        self.recording_thread.stop()
        self.recording_thread.join()

        # Generate timestamped filename and save in Documents folder
        timestamp = datetime.now().strftime("%d-%m-%y %H_%M_%S")
        documents_folder = os.path.join(os.path.expanduser("~"), "vartalap")
        text_filename = os.path.join(documents_folder, f"{timestamp}.txt")
        audio_filename = os.path.join(documents_folder, f"audio_{timestamp}.wav")

        # Create Documents folder if it doesn't exist
        os.makedirs(documents_folder, exist_ok=True)

        self.recording_thread.save(audio_filename)

        self.status_label.config(text=f"Status: Transcribing with {self.api_choice.get()}...")
        self.transcription_thread = TranscriptionThread(
            audio_filename, text_filename, self.model, self.root, self.update_transcription, self.ai, self.api_choice.get(), self.token_limit
        )
        self.transcription_thread.start()

    def update_transcription(self, text):
        self.text_area.delete(1.0, tk.END)
        self.apply_markdown_formatting(text)
        self.status_label.config(text=f"Status: Stopped (Using {self.api_choice.get()})")

    def apply_markdown_formatting(self, text):
        # Split text into lines and apply formatting
        lines = text.split("\n")
        for line in lines:
            if line.startswith("# "):
                # Heading 1
                self.text_area.insert(tk.END, line[2:] + "\n", "heading1")
            elif line.startswith("## "):
                # Heading 2
                self.text_area.insert(tk.END, line[3:] + "\n", "heading2")
            elif line.startswith("**") and line.endswith("**"):
                # Bold text
                self.text_area.insert(tk.END, line[2:-2] + "\n", "bold")
            elif line.startswith("*") and line.endswith("*"):
                # Italic text
                self.text_area.insert(tk.END, line[1:-1] + "\n", "italic")
            elif line.startswith("`") and line.endswith("`"):
                # Code block
                self.text_area.insert(tk.END, line[1:-1] + "\n", "code")
            else:
                # Normal text
                if line.endswith(":"):
                    self.text_area.insert(tk.END, line + "\n", "heading2")
                else:
                    self.text_area.insert(tk.END, line + "\n\n")

class RecordingThread(threading.Thread):
    def __init__(self, audio_queue):
        super().__init__()
        self.audio_queue = audio_queue
        self.fs = 44100  # Sample rate
        self.channels = 1  # Stereo
        self.frames = []
        self.stop_event = threading.Event()

    def callback(self, indata, frames, time, status):
        self.audio_queue.put(indata.copy())

    def run(self):
        try:
            with sd.InputStream(
                    samplerate=self.fs,
                    channels=self.channels,
                    callback=self.callback,
                    blocksize=1024
            ):
                while not self.stop_event.is_set():
                    data = self.audio_queue.get()
                    self.frames.append(data)
        except Exception as e:
            print(f"Recording error: {e}")

    def stop(self):
        self.stop_event.set()

    def save(self, filename):
        if self.frames:
            audio_data = np.concatenate(self.frames, axis=0)
            sf.write(filename, audio_data, self.fs)

class TranscriptionThread(threading.Thread):
    def __init__(self, audio_filename, text_filename, model, root, callback, ai, api_type, token_limit=28000):
        super().__init__()
        self.audio_filename = audio_filename
        self.text_filename = text_filename
        self.model = model
        self.root = root
        self.callback = callback
        self.ai = ai
        self.api_type = api_type
        self.token_limit = token_limit

    def run(self):
        try:
            result = self.model.transcribe(self.audio_filename)
            # Save to timestamped file
            with open(self.text_filename, "w", encoding="utf-8") as f:
                f.write(result["text"])
            transcribed_text = result["text"]
            if len(transcribed_text) > self.token_limit:
                transcribed_text = transcribed_text[:self.token_limit] + "..."

            req_prompt = prompt.format(transcribed_text)

            # Choose API based on selection
            if self.api_type == "MetaAI":
                response = self.ai.prompt(message=req_prompt)
                ai_response = response['message']
            else:  # OpenAI
                response = self.ai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": req_prompt}],
                )
                ai_response = response.choices[0].message.content

            summary_filename = self.text_filename.replace(".txt", f"_summary_{self.api_type}.txt")
            with open(summary_filename, "w", encoding="utf-8") as f:
                f.write(ai_response)

            self.root.after(0, self.callback, ai_response)
        except Exception as e:
            error_msg = f"Transcription/API error: {e}"
            self.root.after(0, self.callback, error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()