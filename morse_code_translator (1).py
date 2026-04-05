"""
╔══════════════════════════════════════════════════════════╗
║           MORSE CODE TRANSLATOR — GUI Application        ║
║           Built with Python & Tkinter                    ║
║           Features: Encode, Decode, Sound, Clipboard     ║
╚══════════════════════════════════════════════════════════╝
"""

# ─── IMPORTS ─────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox, font
import threading
import time
import winsound  # Windows only — see cross-platform note below
import sys


# ─── MORSE CODE DICTIONARY ───────────────────────────────────────────────────
# Maps each letter/digit to its Morse code representation
MORSE_CODE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..',  '9': '----.',
    ' ': '/'      # Word separator
}

# Reverse dictionary: Morse code → Letter  (used for decoding)
REVERSE_MORSE = {v: k for k, v in MORSE_CODE.items()}


# ─── ENCODE FUNCTION ─────────────────────────────────────────────────────────
def encode_text(text: str) -> str:
    """
    Convert plain English text into Morse code.
    Each letter is separated by a space.
    Each word is separated by ' / '.

    Args:
        text (str): The English sentence to encode.

    Returns:
        str: The Morse code string.

    Raises:
        ValueError: If a character is not supported.
    """
    text = text.upper().strip()
    if not text:
        raise ValueError("Input is empty. Please enter some text.")

    morse_parts = []
    for char in text:
        if char in MORSE_CODE:
            morse_parts.append(MORSE_CODE[char])
        else:
            raise ValueError(
                f"Character '{char}' is not supported.\n"
                "Only A–Z, 0–9, and spaces are allowed."
            )
    return ' '.join(morse_parts)


# ─── DECODE FUNCTION ─────────────────────────────────────────────────────────
def decode_morse(morse: str) -> str:
    """
    Convert Morse code back into English text.
    Expects letters separated by spaces, words by ' / '.

    Args:
        morse (str): The Morse code string.

    Returns:
        str: The decoded English sentence.

    Raises:
        ValueError: If an unknown Morse sequence is found.
    """
    morse = morse.strip()
    if not morse:
        raise ValueError("Input is empty. Please enter Morse code.")

    words = morse.split(' / ')   # Split on word-separator
    result = []

    for word in words:
        letters = word.split(' ')   # Each letter separated by space
        decoded_word = ''
        for code in letters:
            if code == '':
                continue  # Skip extra spaces
            if code in REVERSE_MORSE:
                decoded_word += REVERSE_MORSE[code]
            else:
                raise ValueError(
                    f"Unknown Morse sequence: '{code}'\n"
                    "Make sure letters are separated by single spaces\n"
                    "and words are separated by ' / '."
                )
        result.append(decoded_word)

    return ' '.join(result)


# ─── SOUND PLAYBACK ──────────────────────────────────────────────────────────
# Morse timing constants (in milliseconds)
DOT_DURATION  = 80    # Duration of a dot beep
DASH_DURATION = 240   # Duration of a dash beep (3× dot)
SYMBOL_GAP    = 80    # Gap between symbols within a letter
LETTER_GAP    = 240   # Gap between letters
WORD_GAP      = 560   # Gap between words
BEEP_FREQ     = 700   # Frequency of the beep in Hz


def play_morse_sound(morse: str):
    """
    Play Morse code as audio beeps using winsound (Windows).
    Runs in a background thread so the GUI stays responsive.

    Note: On macOS/Linux, replace winsound.Beep() with:
        import subprocess
        subprocess.call(['afplay', '/System/Library/Sounds/Tink.aiff'])
    Or use the 'beepy' or 'playsound' packages.
    """
    def _play():
        for char in morse:
            if char == '.':
                winsound.Beep(BEEP_FREQ, DOT_DURATION)
                time.sleep(SYMBOL_GAP / 1000)
            elif char == '-':
                winsound.Beep(BEEP_FREQ, DASH_DURATION)
                time.sleep(SYMBOL_GAP / 1000)
            elif char == ' ':
                time.sleep(LETTER_GAP / 1000)
            elif char == '/':
                time.sleep(WORD_GAP / 1000)

    # Run in a daemon thread so it doesn't block the GUI
    t = threading.Thread(target=_play, daemon=True)
    t.start()


def is_windows() -> bool:
    """Check if running on Windows (winsound is Windows-only)."""
    return sys.platform == 'win32'


# ─── MAIN APPLICATION CLASS ──────────────────────────────────────────────────
class MorseTranslatorApp:
    """
    The main GUI application class.
    Builds the entire Tkinter interface and wires up all buttons.
    """

    # ── Color Palette ────────────────────────────────────────────────────────
    COLORS = {
        'bg':         '#F5F0E8',   # Warm off-white background
        'panel':      '#FFFDF7',   # Slightly lighter panel
        'accent':     '#2D3A3A',   # Dark teal-black for titles
        'btn_encode': '#2E7D6E',   # Deep teal for Encode
        'btn_decode': '#1A4A7A',   # Navy for Decode
        'btn_clear':  '#8B4513',   # Earthy brown for Clear
        'btn_sound':  '#6B3D7A',   # Purple for Sound
        'btn_copy':   '#4A4A4A',   # Charcoal for Copy
        'btn_fg':     '#FFFFFF',   # White button text
        'border':     '#C8BFA8',   # Muted border
        'label':      '#5A4E3C',   # Warm brown label text
        'output_bg':  '#EEF4F0',   # Light green tint for output
        'dot':        '#2E7D6E',   # Dot colour indicator
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self._configure_window()
        self._build_ui()

    # ── Window Setup ─────────────────────────────────────────────────────────
    def _configure_window(self):
        """Set window title, size, and background."""
        self.root.title("Morse Code Translator")
        self.root.geometry("700x620")
        self.root.resizable(True, True)
        self.root.configure(bg=self.COLORS['bg'])
        self.root.minsize(560, 520)

    # ── UI Construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        """Build all widgets: header, input, buttons, output, status bar."""
        self._build_header()
        self._build_input_section()
        self._build_button_row()
        self._build_output_section()
        self._build_status_bar()

    def _build_header(self):
        """Title banner at the top."""
        header_frame = tk.Frame(self.root, bg=self.COLORS['accent'], pady=16)
        header_frame.pack(fill='x')

        tk.Label(
            header_frame,
            text="• — — •  MORSE CODE TRANSLATOR  • — — •",
            font=("Courier New", 15, "bold"),
            fg="#A8D8C8",
            bg=self.COLORS['accent']
        ).pack()

        tk.Label(
            header_frame,
            text="Encode · Decode · Hear · Copy",
            font=("Courier New", 9),
            fg="#6AADA0",
            bg=self.COLORS['accent']
        ).pack(pady=(2, 0))

    def _build_input_section(self):
        """Input label + text box."""
        frame = tk.Frame(self.root, bg=self.COLORS['bg'], padx=24, pady=14)
        frame.pack(fill='x')

        tk.Label(
            frame,
            text="✏  Input  (English text  OR  Morse code):",
            font=("Courier New", 10, "bold"),
            fg=self.COLORS['label'],
            bg=self.COLORS['bg'],
            anchor='w'
        ).pack(fill='x')

        # Text box with scroll bar
        input_container = tk.Frame(
            frame,
            bg=self.COLORS['border'],
            padx=1, pady=1
        )
        input_container.pack(fill='x', pady=(4, 0))

        self.input_box = tk.Text(
            input_container,
            height=5,
            font=("Courier New", 11),
            bg=self.COLORS['panel'],
            fg=self.COLORS['accent'],
            insertbackground=self.COLORS['accent'],
            relief='flat',
            padx=10, pady=8,
            wrap='word'
        )
        input_scroll = tk.Scrollbar(input_container, command=self.input_box.yview)
        self.input_box.configure(yscrollcommand=input_scroll.set)
        input_scroll.pack(side='right', fill='y')
        self.input_box.pack(fill='x')

    def _build_button_row(self):
        """Row of action buttons."""
        frame = tk.Frame(self.root, bg=self.COLORS['bg'], padx=24, pady=10)
        frame.pack(fill='x')

        btn_config = [
            ("⬆  ENCODE",  self.COLORS['btn_encode'], self._on_encode),
            ("⬇  DECODE",  self.COLORS['btn_decode'], self._on_decode),
            ("✖  CLEAR",   self.COLORS['btn_clear'],  self._on_clear),
            ("♫  SOUND",   self.COLORS['btn_sound'],  self._on_sound),
            ("⎘  COPY",    self.COLORS['btn_copy'],   self._on_copy),
        ]

        for (label, color, command) in btn_config:
            btn = tk.Button(
                frame,
                text=label,
                bg=color,
                fg=self.COLORS['btn_fg'],
                activebackground=color,
                activeforeground='#FFFFFF',
                font=("Courier New", 10, "bold"),
                relief='flat',
                padx=14, pady=8,
                cursor='hand2',
                command=command
            )
            btn.pack(side='left', padx=(0, 8))

        # Hover effects
        for widget in frame.winfo_children():
            self._add_hover(widget)

    def _add_hover(self, btn: tk.Button):
        """Add subtle hover brightness to a button."""
        original_bg = btn.cget('bg')

        def on_enter(_):
            btn.configure(relief='groove')

        def on_leave(_):
            btn.configure(relief='flat')

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

    def _build_output_section(self):
        """Output label + read-only text box."""
        frame = tk.Frame(self.root, bg=self.COLORS['bg'], padx=24, pady=4)
        frame.pack(fill='both', expand=True)

        tk.Label(
            frame,
            text="📋  Output:",
            font=("Courier New", 10, "bold"),
            fg=self.COLORS['label'],
            bg=self.COLORS['bg'],
            anchor='w'
        ).pack(fill='x')

        output_container = tk.Frame(
            frame,
            bg=self.COLORS['border'],
            padx=1, pady=1
        )
        output_container.pack(fill='both', expand=True, pady=(4, 0))

        self.output_box = tk.Text(
            output_container,
            height=8,
            font=("Courier New", 11),
            bg=self.COLORS['output_bg'],
            fg='#1A3A2A',
            relief='flat',
            padx=10, pady=8,
            wrap='word',
            state='disabled'   # Read-only
        )
        output_scroll = tk.Scrollbar(output_container, command=self.output_box.yview)
        self.output_box.configure(yscrollcommand=output_scroll.set)
        output_scroll.pack(side='right', fill='y')
        self.output_box.pack(fill='both', expand=True)

    def _build_status_bar(self):
        """Bottom status bar showing feedback messages."""
        self.status_var = tk.StringVar(value="Ready — enter text above and click Encode or Decode.")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Courier New", 9),
            fg='#7A6A55',
            bg='#E0D8C8',
            anchor='w',
            padx=12,
            pady=5
        )
        status_bar.pack(fill='x', side='bottom')

    # ── Helper: Read & Write Text Boxes ─────────────────────────────────────
    def _get_input(self) -> str:
        """Return text from the input box (stripped)."""
        return self.input_box.get("1.0", tk.END).strip()

    def _set_output(self, text: str):
        """Write text to the (read-only) output box."""
        self.output_box.configure(state='normal')
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert("1.0", text)
        self.output_box.configure(state='disabled')

    def _set_status(self, msg: str):
        """Update the status bar message."""
        self.status_var.set(msg)

    # ── Button Callbacks ─────────────────────────────────────────────────────
    def _on_encode(self):
        """Triggered when ENCODE button is clicked."""
        text = self._get_input()
        try:
            morse = encode_text(text)
            self._set_output(morse)
            self._set_status(f"✔ Encoded successfully — {len(text)} characters → {len(morse)} symbols.")
        except ValueError as e:
            messagebox.showerror("Encode Error", str(e))
            self._set_status("✘ Encode failed — see error popup.")

    def _on_decode(self):
        """Triggered when DECODE button is clicked."""
        morse = self._get_input()
        try:
            text = decode_morse(morse)
            self._set_output(text)
            self._set_status(f"✔ Decoded successfully → '{text}'")
        except ValueError as e:
            messagebox.showerror("Decode Error", str(e))
            self._set_status("✘ Decode failed — see error popup.")

    def _on_clear(self):
        """Clear both input and output boxes."""
        self.input_box.delete("1.0", tk.END)
        self._set_output("")
        self._set_status("Cleared — ready for new input.")

    def _on_sound(self):
        """Play Morse code from the OUTPUT box as audio beeps."""
        morse = self.output_box.get("1.0", tk.END).strip()
        if not morse:
            messagebox.showwarning(
                "No Morse Code",
                "Please encode some text first so Morse appears in the output box."
            )
            return

        if not is_windows():
            messagebox.showinfo(
                "Sound Not Available",
                "Sound playback uses winsound and is only available on Windows.\n"
                "On macOS/Linux, install the 'beepy' package and update play_morse_sound()."
            )
            return

        self._set_status("♫ Playing Morse code as sound…")
        play_morse_sound(morse)

    def _on_copy(self):
        """Copy the output text to the system clipboard."""
        output = self.output_box.get("1.0", tk.END).strip()
        if not output:
            messagebox.showwarning("Nothing to Copy", "The output box is empty.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(output)
        self.root.update()  # Keeps clipboard alive after app closes
        self._set_status("⎘ Output copied to clipboard!")


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
def main():
    """Create the Tkinter root window and launch the app."""
    root = tk.Tk()
    app = MorseTranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
