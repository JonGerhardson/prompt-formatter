import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog
import os # Needed for os.path.basename

# --- Base Prompt Template ---
# Derived from the framework discussed previously
PROMPT_TEMPLATE = """
## Prompt for Generating Official Meeting Reports

**Role:** You are an AI assistant specialized in processing official meeting records and generating accurate, objective summaries. Your primary goal is to create a factual report based *exclusively* on the provided definitive source material, typically a meeting transcript.

**Task:** Generate a thorough and accurate report summarizing a specific official meeting (e.g., [MEETING_BODY]). The report should accurately reflect the discussions, decisions, and outcomes based *only* on the provided transcript from [MEETING_DATE].

**Input:**

1.  **Primary Source (Required):** The full, official transcript of the meeting:
    ```transcript
    [MEETING_TRANSCRIPT_TEXT]
    ```

2.  **Meeting Context (Required):**
    * Meeting Body: [MEETING_BODY]
    * Meeting Date: [MEETING_DATE]

3.  **Report Type (Required):** [REPORT_TYPE]
    * Specific Topic (if applicable): [SPECIFIC_TOPIC]

4.  **Supporting Documents (Optional):**
    ```supporting_docs
    [OPTIONAL_SUPPORTING_DOCS]
    ```

5.  **Style Guidelines (Optional):**
    ```style_guidelines
    [STYLE_GUIDELINES]
    ```

**Process & Instructions:**

1.  **Prioritize Transcript:** Base the entire report *solely* on the provided official transcript text. Do not incorporate information from external knowledge or preliminary summaries unless explicitly instructed and corroborated by the transcript.
2.  **Verify Information:** Meticulously extract and verify all details from the transcript: Facts (actions, motions, decisions, figures, item numbers), Votes (precise counts, abstentions), Speakers & Names (accurate attribution, use **Name** format, ignore obvious transcript spelling errors if correct spelling is known), Procedural Details (referrals, readings, etc.).
3.  **Handle Quotes:** Identify direct quotes. Include quotes **only if they are exactly verbatim** from the transcript. Use `<u>underlining</u>` format for verbatim quotes. Do *not* paraphrase and present it as a direct quote.
4.  **Identify Key Topics (for Comprehensive Reports):** Analyze the transcript to identify the most significant discussions/actions based on debate intensity, financial/policy/community impact.
5.  **Structure the Report:**
    * **Comprehensive:** Organize logically (thematically or chronologically). Detail key topics. Include sections for major items, public input, other actions, context.
    * **Topic-Specific:** Focus exclusively on the specified topic (`[SPECIFIC_TOPIC]`). Include all relevant discussion, actions, context, and outcomes related *only* to that item.
6.  **Drafting Style:** Maintain a neutral, objective, factual tone. Clearly attribute statements/arguments. Use item/order numbers for clarity. Summarize routine actions concisely.
7.  **Context & Notes:** Include relevant context (opening/closing, tributes). If ambiguities remain *after analyzing the transcript*, list them in a separate "Notes for Clarification" section. Do not speculate.
8.  **Review:** Ensure the final report is accurate, clear, complete (for the specified scope), internally consistent, and adheres to any provided Style Guidelines.

**Output:**

* Produce the report in Markdown format.
* Adhere strictly to the specified `[REPORT_TYPE]`.
* Use specified formatting for names (`**Name**`) and quotes (`<u>quote</u>`) consistently.
"""

# --- GUI Functions ---

def update_topic_entry_state(*args):
    """Enable or disable the Specific Topic entry based on Report Type selection."""
    if report_type_var.get() == "Topic-Specific":
        topic_entry.config(state=tk.NORMAL)
    else:
        topic_entry.delete(0, tk.END) # Clear the entry if disabled
        topic_entry.config(state=tk.DISABLED)

def _load_file_content(text_widget, title):
    """Loads text from a SINGLE file into the specified ScrolledText widget, replacing content."""
    filepath = filedialog.askopenfilename(
        title=title,
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")] # Kept simple for single file load
    )
    if not filepath:
        return # User cancelled

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Ensure widget is editable, clear it, insert new content
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", content)
        # No need to disable again - keep it editable
        messagebox.showinfo("File Loaded", f"Successfully loaded content from:\n{os.path.basename(filepath)}")

    except Exception as e:
        messagebox.showerror("Error Reading File", f"Failed to read file: {filepath}\n{e}")
        # Optionally clear the text area or leave previous content upon error
        # text_widget.delete("1.0", tk.END)

def load_and_append_docs_files():
    """Loads content from one or more selected files (.txt, .md) and APPENDS it
       to the Supporting Docs text area."""
    filepaths = filedialog.askopenfilenames( # Use askopenfilenames for multiple files
        title="Select Supporting Docs Files (Text or Markdown)",
        filetypes=[("Text/Markdown Files", "*.txt *.md"),
                   ("Text Files", "*.txt"),
                   ("Markdown Files", "*.md"),
                   ("All Files", "*.*")]
    )
    if not filepaths:
        return # User cancelled

    # Ensure the text area is editable before appending
    docs_text_area.config(state=tk.NORMAL)
    files_loaded_count = 0
    for filepath in filepaths:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            filename = os.path.basename(filepath)
            separator = f"\n\n--- Supporting Doc: {filename} ---\n\n"

            # Append separator and content
            docs_text_area.insert(tk.END, separator)
            docs_text_area.insert(tk.END, content)
            files_loaded_count += 1

        except Exception as e:
            messagebox.showwarning("Error Reading File", f"Failed to read file: {filepath}\n{e}\nSkipping this file.")

    if files_loaded_count > 0:
         messagebox.showinfo("Files Appended", f"Successfully appended content from {files_loaded_count} file(s).")
    # Keep the text area editable

def load_transcript_file():
    """Command for the Load Transcript button (loads single file, replaces content)."""
    _load_file_content(transcript_text_area, "Select Transcript File")

# Keep load_docs_file for reference or remove if only append is desired.
# Let's rename the function called by the button to the new multi-file one.
# def load_docs_file():
#    """Command for the Load Supporting Docs button."""
#    _load_file_content(docs_text_area, "Select Supporting Docs File")

def load_style_file():
    """Command for the Load Style Guidelines button (loads single file, replaces content)."""
    _load_file_content(style_text_area, "Select Style Guidelines File")


def generate_prompt():
    """Gathers inputs and formats the final prompt."""
    # Get values from input fields
    transcript_text = transcript_text_area.get("1.0", tk.END).strip()
    meeting_date = date_entry.get().strip()
    meeting_body = body_entry.get().strip()
    report_type = report_type_var.get()
    specific_topic = topic_entry.get().strip() if report_type == "Topic-Specific" else "N/A"
    supporting_docs = docs_text_area.get("1.0", tk.END).strip() # Get potentially appended content
    style_guidelines = style_text_area.get("1.0", tk.END).strip()

    # Basic Validation
    if not transcript_text:
        messagebox.showerror("Input Error", "Meeting Transcript text cannot be empty.")
        return
    if not meeting_date:
        messagebox.showerror("Input Error", "Meeting Date cannot be empty.")
        return
    if not meeting_body:
        messagebox.showerror("Input Error", "Meeting Body cannot be empty.")
        return
    if report_type == "Topic-Specific" and not specific_topic:
         messagebox.showerror("Input Error", "Specific Topic cannot be empty when Report Type is 'Topic-Specific'.")
         return

    # Replace placeholders in the template
    formatted_prompt = PROMPT_TEMPLATE
    formatted_prompt = formatted_prompt.replace("[MEETING_TRANSCRIPT_TEXT]", transcript_text)
    formatted_prompt = formatted_prompt.replace("[MEETING_DATE]", meeting_date)
    formatted_prompt = formatted_prompt.replace("[MEETING_BODY]", meeting_body)
    formatted_prompt = formatted_prompt.replace("[REPORT_TYPE]", report_type)
    formatted_prompt = formatted_prompt.replace("[SPECIFIC_TOPIC]", specific_topic)
    formatted_prompt = formatted_prompt.replace("[OPTIONAL_SUPPORTING_DOCS]", supporting_docs if supporting_docs else "None provided.")
    formatted_prompt = formatted_prompt.replace("[STYLE_GUIDELINES]", style_guidelines if style_guidelines else "None provided.")

    # Display the formatted prompt
    output_text_area.config(state=tk.NORMAL) # Enable writing
    output_text_area.delete("1.0", tk.END)    # Clear previous output
    output_text_area.insert(tk.END, formatted_prompt) # Insert new prompt
    output_text_area.config(state=tk.DISABLED) # Disable editing

# --- GUI Setup ---
root = tk.Tk()
root.title("LLM Meeting Report Prompt Formatter")

# Configure grid weights for resizing
root.columnconfigure(1, weight=1) # Allow main content column to expand
# Add weights to rows containing the main text areas to allow vertical expansion
root.rowconfigure(2, weight=1) # Transcript text area row
root.rowconfigure(7, weight=1) # Optional Docs text area row
root.rowconfigure(9, weight=1) # Style Guidelines text area row
root.rowconfigure(11, weight=3) # Output text area row


# --- Top Frame for Basic Info & Load Buttons ---
top_frame = ttk.Frame(root, padding="5")
top_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
top_frame.columnconfigure(1, weight=1) # Allow body entry to expand

# Meeting Body
body_label = ttk.Label(top_frame, text="Meeting Body:")
body_label.grid(row=0, column=0, padx=(0,5), pady=5, sticky="w")
body_entry = ttk.Entry(top_frame, width=60)
body_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Meeting Date
date_label = ttk.Label(top_frame, text="Meeting Date:")
date_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
date_entry = ttk.Entry(top_frame, width=15)
date_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

# --- Input Widgets ---

# Transcript Text Area + Load Button
transcript_frame = ttk.Frame(root)
transcript_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5)
transcript_label = ttk.Label(transcript_frame, text="Paste Meeting Transcript Text Here (or Load File):")
transcript_label.pack(side=tk.LEFT, anchor='w', pady=(5,0))
# Button to load a SINGLE transcript file (replaces content)
load_transcript_button = ttk.Button(transcript_frame, text="Load Transcript...", command=load_transcript_file)
load_transcript_button.pack(side=tk.RIGHT, anchor='e', padx=5)

transcript_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10)
transcript_text_area.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

# Report Type Options Frame
options_frame = ttk.Frame(root, padding="5")
options_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5)
options_frame.columnconfigure(1, weight=1) # Allow topic entry to expand

report_type_label = ttk.Label(options_frame, text="Report Type:")
report_type_label.grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")
report_type_var = tk.StringVar(value="Comprehensive") # Default value
report_type_var.trace_add("write", update_topic_entry_state) # Add trace to update topic field state

comprehensive_radio = ttk.Radiobutton(options_frame, text="Comprehensive", variable=report_type_var, value="Comprehensive")
comprehensive_radio.grid(row=0, column=1, padx=5, pady=5, sticky="w")
topic_specific_radio = ttk.Radiobutton(options_frame, text="Topic-Specific", variable=report_type_var, value="Topic-Specific")
topic_specific_radio.grid(row=0, column=2, padx=5, pady=5, sticky="w")

# Specific Topic Entry (conditionally enabled)
topic_label = ttk.Label(options_frame, text="Specific Topic (if Topic-Specific):")
topic_label.grid(row=1, column=0, padx=(0,10), pady=5, sticky="w")
topic_entry = ttk.Entry(options_frame, width=80, state=tk.DISABLED) # Initially disabled
topic_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

# Optional Supporting Docs Text Area + Load Button
docs_frame = ttk.Frame(root)
docs_frame.grid(row=6, column=0, columnspan=4, sticky="ew", padx=5)
docs_label = ttk.Label(docs_frame, text="Paste Optional Supporting Docs Text (Agenda, etc.) (or Load Files):")
docs_label.pack(side=tk.LEFT, anchor='w', pady=(5,0))
# Button now calls the multi-file append function
load_docs_button = ttk.Button(docs_frame, text="Load/Append Docs...", command=load_and_append_docs_files)
load_docs_button.pack(side=tk.RIGHT, anchor='e', padx=5)

docs_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5)
docs_text_area.grid(row=7, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

# Optional Style Guidelines Text Area + Load Button
style_frame = ttk.Frame(root)
style_frame.grid(row=8, column=0, columnspan=4, sticky="ew", padx=5)
style_label = ttk.Label(style_frame, text="Paste Optional Style Guidelines (or Load File):")
style_label.pack(side=tk.LEFT, anchor='w', pady=(5,0))
# Button to load a SINGLE style file (replaces content)
load_style_button = ttk.Button(style_frame, text="Load Style...", command=load_style_file)
load_style_button.pack(side=tk.RIGHT, anchor='e', padx=5)

style_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=3)
style_text_area.grid(row=9, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

# Generate Button
generate_button = ttk.Button(root, text="Generate Prompt", command=generate_prompt)
generate_button.grid(row=10, column=0, columnspan=4, padx=10, pady=10)

# Output Text Area
output_label = ttk.Label(root, text="Formatted Prompt:")
output_label.grid(row=11, column=0, padx=5, pady=(5,0), sticky="nw")
output_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, state=tk.DISABLED) # Start disabled
output_text_area.grid(row=11, column=1, columnspan=3, padx=5, pady=5, sticky="nsew") # Span remaining columns


# --- Run GUI ---
update_topic_entry_state() # Set initial state of topic entry
root.mainloop()

