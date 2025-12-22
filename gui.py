
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import queue
import sys
import os

# Add the project root to the Python path to allow importing jyakoTen
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jyakoTen.score import run_scoring

class QueueIO(queue.Queue):
    def write(self, msg):
        self.put(msg)

    def flush(self):
        sys.__stdout__.flush()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JyakoTen Scorer")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- File Path Inputs ---
        path_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="10")
        path_frame.pack(fill=tk.X, pady=5)
        path_frame.columnconfigure(1, weight=1)

        # Transcript Path
        ttk.Label(path_frame, text="Transcript Path:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.transcript_path = tk.StringVar()
        transcript_entry = ttk.Entry(path_frame, textvariable=self.transcript_path)
        transcript_entry.grid(row=0, column=1, sticky="ew", padx=5)
        transcript_button = ttk.Button(path_frame, text="Browse...", command=lambda: self.browse_file(self.transcript_path))
        transcript_button.grid(row=0, column=2, padx=5)

        # Recognition Path
        ttk.Label(path_frame, text="Recognition Path:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.recognition_path = tk.StringVar()
        recognition_entry = ttk.Entry(path_frame, textvariable=self.recognition_path)
        recognition_entry.grid(row=1, column=1, sticky="ew", padx=5)
        recognition_button = ttk.Button(path_frame, text="Browse...", command=lambda: self.browse_file(self.recognition_path))
        recognition_button.grid(row=1, column=2, padx=5)

        # --- Execute Button ---
        self.execute_button = ttk.Button(main_frame, text="Execute Scoring", command=self.execute_scoring)
        self.execute_button.pack(pady=10)

        # --- Results Display ---
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state="disabled")
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def browse_file(self, string_var):
        filename = filedialog.askopenfilename()
        if filename:
            string_var.set(filename)

    def execute_scoring(self):
        transcript_path = self.transcript_path.get()
        recognition_path = self.recognition_path.get()

        if not transcript_path or not recognition_path:
            self.update_results("Error: Both transcript and recognition paths must be selected.\n")
            return

        self.execute_button.config(state="disabled")
        self.update_results("Starting scoring process...\n", clear=True)

        args_dict = {
            "transcript_path": transcript_path,
            "recognition_path": recognition_path,
            # Add other default arguments from score.py if necessary
            'key1': 'gui_run',
        }

        self.process_queue = QueueIO()
        threading.Thread(target=self.scoring_thread_target, args=(args_dict,), daemon=True).start()
        self.after(100, self.check_queue)

    def scoring_thread_target(self, args_dict):
        original_stdout = sys.stdout
        sys.stdout = self.process_queue

        try:
            run_scoring(args_dict)
        except Exception as e:
            self.process_queue.write(f"\n--- An error occurred ---\n{e}\n")
        finally:
            sys.stdout = original_stdout
            self.process_queue.put(None) # Signal that the process is done

    def check_queue(self):
        try:
            line = self.process_queue.get_nowait()
            if line is None:
                self.execute_button.config(state="normal")
                self.update_results("\nScoring process finished.\n")
            else:
                self.update_results(line)
                self.after(100, self.check_queue)
        except queue.Empty:
            self.after(100, self.check_queue)

    def update_results(self, message, clear=False):
        self.results_text.config(state="normal")
        if clear:
            self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)
        self.results_text.config(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()
