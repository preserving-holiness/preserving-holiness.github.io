import tkinter as tk
from tkinter import ttk, messagebox, Listbox, filedialog, simpledialog
from datetime import datetime
import os
import re
import json

class PostCreator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Pelican Post Creator")
        self.geometry("770x825")

        # --- Config ---
        self.config = self.load_config()
        self.profiles = self.config.get("profiles", {})

        # --- Data ---
        self.hardcoded_categories = ["Sermons", "Bible Studies"]
        self.hardcoded_tags = ["Bible-Studies", "Word-Studies", "Sermons", "Articles"]

        self.categories = self.get_unique_metadata("Category", self.hardcoded_categories)
        self.tags = self.get_unique_metadata("Tags", self.hardcoded_tags)

        # Add default if empty
        if not self.categories:
            self.categories = ["misc"]
        if not self.tags:
            self.tags = ["general"]

        # --- Field Dictionaries ---
        self.new_post_fields = {}
        self.existing_post_fields = {}
        self.batch_process_fields = {}
        self.numeric_prefix = None

        # --- Widgets ---
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle window close event."""
        self.save_config()
        self.destroy()

    def load_config(self):
        """Loads configuration from a JSON file."""
        try:
            with open("post_creator_config.json", "r") as f:
                config = json.load(f)
                # Ensure essential keys exist, providing defaults if not
                if "last_open_dir" not in config:
                    config["last_open_dir"] = os.path.join(os.getcwd(), "content")
                if "last_save_dir" not in config:
                    config["last_save_dir"] = os.path.join(os.getcwd(), "content", "posts")
                if "profiles" not in config:
                    config["profiles"] = {}
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default config if file doesn't exist or is invalid
            return {
                "last_open_dir": os.path.join(os.getcwd(), "content"),
                "last_save_dir": os.path.join(os.getcwd(), "content", "posts"),
                "profiles": {}
            }

    def save_config(self):
        """Saves configuration to a JSON file."""
        try:
            with open("post_creator_config.json", "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}") # Log error, don't crash

    def get_unique_metadata(self, field, initial_items=[]):
        items = set(initial_items)
        posts_dir = os.path.join("content", "posts")
        if not os.path.exists(posts_dir):
            return sorted(list(items))

        for filename in os.listdir(posts_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(posts_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line in f:
                            # Stop searching for metadata at the first blank line.
                            if not line.strip():
                                break
                            if line.lower().startswith(field.lower() + ":"):
                                value = line.split(":", 1)[1].strip()
                                if field == "Tags":
                                    items.update([tag.strip() for tag in value.split(",") if tag.strip()])
                                else:
                                    items.add(value)
                except Exception as e:
                    print(f"Could not process {filename}: {e}") # Log error
        return sorted(list(items))


    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create Notebook for different modes
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- Tab 1: Create New Post ---
        new_post_tab = ttk.Frame(notebook, padding="10")
        notebook.add(new_post_tab, text="Create New Post")
        self.create_metadata_fields(new_post_tab, self.new_post_fields, is_new_post=True)


        # --- Tab 2: Process Existing File ---
        existing_post_tab = ttk.Frame(notebook, padding="10")
        notebook.add(existing_post_tab, text="Process Existing File")
        
        # Frame for file selection
        file_frame = ttk.Frame(existing_post_tab)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.existing_filepath_var = tk.StringVar()
        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(file_frame, textvariable=self.existing_filepath_var, state="readonly", width=70).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(file_frame, text="Browse...", command=self.load_file).pack(side=tk.LEFT, padx=(5, 0))

        # Preview area
        preview_frame = ttk.LabelFrame(existing_post_tab, text="Content Preview", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.preview_text = tk.Text(preview_frame, height=10, width=80, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Metadata fields for existing post
        self.create_metadata_fields(existing_post_tab, self.existing_post_fields, is_new_post=False)


        # --- Tab 3: Batch Process ---
        batch_process_tab = ttk.Frame(notebook, padding="10")
        notebook.add(batch_process_tab, text="Batch Process")
        self.create_batch_process_widgets(batch_process_tab, self.batch_process_fields)


    def create_batch_process_widgets(self, parent, fields):
        """Creates the UI for the batch processing tab."""
        # --- Directory Selection ---
        dir_frame = ttk.LabelFrame(parent, text="Directories", padding=10)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)

        # Source Directory
        ttk.Label(dir_frame, text="Source:").grid(row=0, column=0, sticky=tk.W, pady=2)
        source_entry_frame = ttk.Frame(dir_frame)
        source_entry_frame.grid(row=0, column=1, sticky="we")
        fields['source_dir'] = ttk.Entry(source_entry_frame, width=80)
        fields['source_dir'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(source_entry_frame, text="Browse...", command=lambda: self.browse_batch_directory(fields['source_dir'])).pack(side=tk.LEFT, padx=(5,0))
        
        # Destination Directory
        ttk.Label(dir_frame, text="Destination:").grid(row=1, column=0, sticky=tk.W, pady=2)
        dest_entry_frame = ttk.Frame(dir_frame)
        dest_entry_frame.grid(row=1, column=1, sticky="we")
        fields['dest_dir'] = ttk.Entry(dest_entry_frame, width=80)
        fields['dest_dir'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dest_entry_frame, text="Browse...", command=lambda: self.browse_batch_directory(fields['dest_dir'])).pack(side=tk.LEFT, padx=(5,0))

        # Start Index
        ttk.Label(dir_frame, text="Start Index (optional):").grid(row=2, column=0, sticky=tk.W, pady=2)
        fields['start_index'] = ttk.Entry(dir_frame, width=20)
        fields['start_index'].grid(row=2, column=1, sticky="w", pady=2)

        # --- Profile Selection ---
        profile_frame = ttk.LabelFrame(parent, text="Metadata Profile", padding=10)
        profile_frame.pack(fill=tk.X, pady=(0, 10))
        profile_frame.columnconfigure(1, weight=1)

        ttk.Label(profile_frame, text="Apply Profile:").grid(row=0, column=0, sticky=tk.W, pady=2)
        fields['profile_selector'] = ttk.Combobox(profile_frame, values=list(self.profiles.keys()), state="readonly")
        fields['profile_selector'].grid(row=0, column=1, sticky="we", pady=2)

        ttk.Label(profile_frame, text="Author:").grid(row=1, column=0, sticky=tk.W, pady=2)
        fields['author'] = ttk.Entry(profile_frame)
        fields['author'].grid(row=1, column=1, sticky="we", pady=2)
        fields['author'].insert(0, self.config.get("default_author", "nameless"))

        # --- Action Button ---
        action_frame = ttk.Frame(parent, padding=(0, 10, 0, 0))
        action_frame.pack(fill=tk.X)
        ttk.Button(action_frame, text="Start Batch Process", command=self.start_batch_processing).pack(side=tk.RIGHT)

        # --- Log Viewer ---
        log_frame = ttk.LabelFrame(parent, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        fields['log_text'] = tk.Text(log_frame, wrap=tk.WORD, state="disabled", height=15)
        log_scroll = ttk.Scrollbar(log_frame, command=fields['log_text'].yview)
        fields['log_text']['yscrollcommand'] = log_scroll.set
        
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        fields['log_text'].pack(fill=tk.BOTH, expand=True)


    def log_message(self, message):
        """Adds a message to the log viewer on the batch process tab."""
        log_widget = self.batch_process_fields['log_text']
        log_widget.config(state="normal")
        log_widget.insert(tk.END, message + "\n")
        log_widget.config(state="disabled")
        log_widget.see(tk.END) # Auto-scroll
        self.update_idletasks() # Refresh the UI to show the message immediately

    def start_batch_processing(self):
        """Main logic for the batch processing feature."""
        fields = self.batch_process_fields
        source_dir = fields['source_dir'].get().strip()
        dest_dir = fields['dest_dir'].get().strip()
        profile_name = fields['profile_selector'].get()
        author_name = fields['author'].get().strip()
        start_index_str = fields['start_index'].get().strip()

        # --- Validation ---
        current_index = None
        if start_index_str:
            try:
                current_index = int(start_index_str)
            except ValueError:
                messagebox.showerror("Error", "Start Index must be a valid number.")
                return

        if not source_dir or not dest_dir:
            messagebox.showerror("Error", "Source and Destination directories must be selected.")
            return
        if not os.path.isdir(source_dir):
            messagebox.showerror("Error", f"Source directory not found:\n{source_dir}")
            return
        if not profile_name:
            messagebox.showerror("Error", "A profile must be selected to apply metadata.")
            return
        if not author_name:
            messagebox.showerror("Error", "The Author field cannot be empty.")
            return
        
        profile = self.profiles.get(profile_name)
        if not profile:
            messagebox.showerror("Error", f"Profile '{profile_name}' not found.")
            return

        if not os.path.exists(dest_dir):
            if not messagebox.askyesno("Create Directory", f"The destination directory does not exist. Create it?"):
                return
            try:
                os.makedirs(dest_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create destination directory: {e}")
                return

        # --- Save config with new default author ---
        self.config['default_author'] = author_name
        self.save_config()

        # --- Find files ---
        files_to_process = []
        for root, _, files in os.walk(source_dir):
            for filename in files:
                if filename.lower().endswith((".txt", ".md")):
                    files_to_process.append(os.path.join(root, filename))

        # --- Interactive Processing ---
        self.log_message(f"--- Starting Interactive Batch Process: {len(files_to_process)} files found ---")
        
        processed_count = 0
        for filepath in files_to_process:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                self.log_message(f"ERROR reading {os.path.basename(filepath)}: {e}")
                continue

            dialog = BatchEditDialog(self, filepath, content)
            result = dialog.show()

            if result['status'] == 'cancel':
                self.log_message("--- Batch process cancelled by user. ---")
                return # Stop everything
            
            if result['status'] == 'skip':
                self.log_message(f"SKIPPED: {os.path.basename(filepath)}")
                continue

            if result['status'] == 'save':
                processed_count += 1
                title = result['title']
                slug = result['slug']
                summary = result['summary']
                edited_content = result['content']
                
                # The user has edited the content, so we just need to parse any header
                # remnants out of it to get the clean body.
                _, body_content = self.parse_markdown_file(edited_content)

                # Determine filename
                new_filename = f"{slug}.md" # Default
                if current_index is not None:
                    new_filename = f"{current_index}-{slug}.md"
                    current_index += 1
                else:
                    basename = os.path.basename(filepath)
                    basename_no_ext, _ = os.path.splitext(basename)
                    # Check if filename starts with a number (e.g., "01-my-post")
                    match = re.match(r'^(\d+)', basename_no_ext)
                    if match:
                        numeric_prefix = match.group(1)
                        new_filename = f"{numeric_prefix}-{slug}.md"
                    else:
                        new_filename = f"{slug}.md"


                # Build header
                header_parts = [
                    f"Title: {title}",
                    f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "Status: published",
                    f"Category: {profile.get('category', 'misc')}",
                    f"Tags: {', '.join(profile.get('tags', []))}",
                    f"Author: {author_name}",
                    f"Slug: {slug}",
                ]
                if summary:
                    header_parts.append(f"Summary: {summary}")

                header = "\n".join(header_parts)
                full_new_content = header + "\n\n---\n\n" + body_content

                # Write file
                new_filepath = os.path.join(dest_dir, new_filename)
                try:
                    with open(new_filepath, "w", encoding="utf-8") as f_out:
                        f_out.write(full_new_content)
                    self.log_message(f"SUCCESS: Saved {new_filename}")
                except Exception as e:
                    self.log_message(f"ERROR saving {new_filename}: {e}")

        self.log_message(f"--- Batch Process Complete: {processed_count} file(s) processed. ---")
        messagebox.showinfo("Complete", "Batch processing has finished.")


    def create_metadata_fields(self, parent, fields, is_new_post):
        # Create a main frame to hold everything, allowing the content text area to expand
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)

        fields_frame = ttk.Frame(container)
        fields_frame.pack(fill=tk.X)

        # --- Input fields ---
        row = 0

        # Title
        ttk.Label(fields_frame, text="Title:").grid(row=row, column=0, sticky=tk.W, pady=2)
        
        title_frame = ttk.Frame(fields_frame)
        title_frame.grid(row=row, column=1, columnspan=2, sticky="we")
        
        fields['title'] = ttk.Entry(title_frame, width=80)
        fields['title'].pack(side=tk.LEFT, fill=tk.X, expand=True)

        format_button = ttk.Button(title_frame, text="Format Title", command=lambda f=fields: self.format_title_field(f))
        format_button.pack(side=tk.LEFT, padx=(5, 0))
        
        row += 1

        if is_new_post:
             # Removed automatic slug generation on title key release
             pass

        # Filename
        ttk.Label(fields_frame, text="Filename:").grid(row=row, column=0, sticky=tk.W, pady=2)
        fields['filename'] = ttk.Entry(fields_frame, width=80)
        fields['filename'].grid(row=row, column=1, columnspan=2, sticky="we", pady=2)
        row += 1

        # Save Directory
        ttk.Label(fields_frame, text="Save Directory:").grid(row=row, column=0, sticky=tk.W, pady=2)
        dir_frame = ttk.Frame(fields_frame)
        dir_frame.grid(row=row, column=1, columnspan=2, sticky="we")
        fields['directory'] = ttk.Entry(dir_frame, width=70)
        fields['directory'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse...", command=lambda: self.browse_directory(fields)).pack(side=tk.LEFT, padx=(5,0))
        fields['directory'].insert(0, self.config.get("last_save_dir"))
        row += 1

        # Slug
        ttk.Label(fields_frame, text="Slug:").grid(row=row, column=0, sticky=tk.W, pady=2)
        slug_frame = ttk.Frame(fields_frame)
        slug_frame.grid(row=row, column=1, columnspan=2, sticky="we")
        fields['slug'] = ttk.Entry(slug_frame, width=80)
        fields['slug'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(slug_frame, text="Generate Slug", command=lambda f=fields: self.generate_slug(f)).pack(side=tk.LEFT, padx=(5,0))
        row += 1

        # Author
        ttk.Label(fields_frame, text="Author:").grid(row=row, column=0, sticky=tk.W, pady=2)
        fields['author'] = ttk.Entry(fields_frame, width=80)
        fields['author'].grid(row=row, column=1, columnspan=2, sticky="we", pady=2)
        fields['author'].insert(0, "nameless") # Default author
        row += 1

        # --- Profile Management ---
        profile_frame = ttk.LabelFrame(fields_frame, text="Profiles", padding=5)
        profile_frame.grid(row=row, column=0, columnspan=3, sticky="we", pady=(10, 5))

        ttk.Label(profile_frame, text="Select Profile:").pack(side=tk.LEFT, padx=(0, 5))
        
        fields['profile_selector'] = ttk.Combobox(profile_frame, values=list(self.profiles.keys()), state="readonly")
        fields['profile_selector'].pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        fields['profile_selector'].bind("<<ComboboxSelected>>", lambda e, f=fields: self.apply_profile(e, f))

        ttk.Button(profile_frame, text="Save", command=lambda f=fields: self.save_profile(f)).pack(side=tk.LEFT, padx=5)
        ttk.Button(profile_frame, text="Delete", command=lambda f=fields: self.delete_profile(f)).pack(side=tk.LEFT, padx=5)
        
        row += 1

        # Date
        ttk.Label(fields_frame, text="Date:").grid(row=row, column=0, sticky=tk.W, pady=2)
        fields['date'] = ttk.Entry(fields_frame, width=80)
        fields['date'].grid(row=row, column=1, columnspan=2, sticky="we", pady=2)
        fields['date'].insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        row += 1

        # Status
        ttk.Label(fields_frame, text="Status:").grid(row=row, column=0, sticky=tk.W, pady=2)
        fields['status'] = tk.StringVar(value="published")
        ttk.Combobox(fields_frame, textvariable=fields['status'], values=["published", "hidden", "draft"], state="readonly").grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        # Category
        ttk.Label(fields_frame, text="Category:").grid(row=row, column=0, sticky=tk.W, pady=2)
        fields['category'] = tk.StringVar(value=self.categories[0] if self.categories else "")
        ttk.Combobox(fields_frame, textvariable=fields['category'], values=self.categories, state="readonly").grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        # Tags
        ttk.Label(fields_frame, text="Tags:").grid(row=row, column=0, sticky=tk.NW, pady=2)
        tags_frame = ttk.Frame(fields_frame)
        tags_frame.grid(row=row, column=1, columnspan=2, sticky="we", pady=2)
        fields['tags_listbox'] = Listbox(tags_frame, selectmode=tk.MULTIPLE, height=5)
        for tag in self.tags:
            fields['tags_listbox'].insert(tk.END, tag)
        fields['tags_listbox'].pack(side="left", fill="x", expand=True)
        row += 1
        
        # Summary
        ttk.Label(fields_frame, text="Summary:").grid(row=row, column=0, sticky=tk.NW, pady=2)
        summary_frame = ttk.Frame(fields_frame)
        summary_frame.grid(row=row, column=1, columnspan=2, sticky="we")
        fields['summary'] = tk.Text(summary_frame, height=4, width=60)
        fields['summary'].pack(fill="x", expand=True)

        # The command for the button needs to know which content widget to use
        summary_command = lambda: self.generate_summary_from_content(fields)
        ttk.Button(summary_frame, text="Generate Summary", command=summary_command).pack(pady=(5,0))
        
        row += 1

        # --- Post Content (only for "New Post" tab) ---
        if is_new_post:
            content_frame = ttk.LabelFrame(container, text="Post Content", padding=5)
            content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            fields['content_editor'] = tk.Text(content_frame, wrap=tk.WORD)
            fields['content_editor'].pack(fill=tk.BOTH, expand=True)
            fields['content_editor'].insert("1.0", "<!-- Your content goes here. -->")


        # Create Button
        create_button = ttk.Button(fields_frame, text="Create Post", command=lambda: self.create_post(fields, is_new_post))
        create_button.grid(row=row, column=2, sticky=tk.E, pady=10)

        fields_frame.columnconfigure(1, weight=1)

    def apply_profile(self, event, fields):
        """Applies a selected profile's category and tags."""
        profile_name = fields['profile_selector'].get()
        if not profile_name:
            return
        
        profile = self.profiles.get(profile_name)
        if not profile:
            return

        # Apply category
        fields['category'].set(profile.get('category', ''))
        
        # Apply tags
        tags_to_select = profile.get('tags', [])
        tags_listbox = fields['tags_listbox']
        tags_listbox.selection_clear(0, tk.END)
        
        all_tags = list(self.tags)
        for tag_to_select in tags_to_select:
            if tag_to_select in all_tags:
                idx = all_tags.index(tag_to_select)
                tags_listbox.selection_set(idx)

    def save_profile(self, fields):
        """Saves the current category and tags as a new profile."""
        profile_name = simpledialog.askstring("Save Profile", "Enter a name for this profile:")
        if not profile_name:
            return

        category = fields['category'].get()
        selected_tags_indices = fields['tags_listbox'].curselection()
        selected_tags = [fields['tags_listbox'].get(i) for i in selected_tags_indices]
        
        self.profiles[profile_name] = {"category": category, "tags": selected_tags}
        
        # Update the profile selector combobox in both tabs
        for field_set in [self.new_post_fields, self.existing_post_fields]:
             if 'profile_selector' in field_set:
                field_set['profile_selector']['values'] = list(self.profiles.keys())
                field_set['profile_selector'].set(profile_name)
        
        messagebox.showinfo("Success", f"Profile '{profile_name}' saved.")

    def delete_profile(self, fields):
        """Deletes the currently selected profile."""
        profile_name = fields['profile_selector'].get()
        if not profile_name:
            messagebox.showwarning("Warning", "No profile selected to delete.")
            return

        if messagebox.askyesno("Delete Profile", f"Are you sure you want to delete the profile '{profile_name}'?"):
            if profile_name in self.profiles:
                del self.profiles[profile_name]
                
                # Update the profile selector combobox in both tabs
                for field_set in [self.new_post_fields, self.existing_post_fields]:
                    if 'profile_selector' in field_set:
                        field_set['profile_selector']['values'] = list(self.profiles.keys())
                        field_set['profile_selector'].set('') # Clear selection
                
                messagebox.showinfo("Success", f"Profile '{profile_name}' deleted.")

    def format_title_field(self, fields):
        """Callback to format the title field to title case via button press."""
        title_entry = fields['title']
        original_title = title_entry.get()
        if original_title: # only format if there's content
            formatted_title = self.smart_title_case(original_title)
            if formatted_title != original_title:
                pos = title_entry.index(tk.INSERT)
                title_entry.delete(0, tk.END)
                title_entry.insert(0, formatted_title)
                title_entry.icursor(pos)
                self.update_filename(None, fields)

    def smart_title_case(self, title):
        """Converts a string to title case, following common style guide rules."""
        
        LITTLE_WORDS = {
            'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 
            'from', 'by', 'in', 'of', 'over', 'with'
        }
        
        # This regex splits the title by spaces and hyphens, keeping the delimiters
        words = re.split(r'([-\s])', title)
        
        # Capitalize the first word unconditionally
        if words:
            words[0] = words[0].capitalize()

        for i in range(1, len(words)):
            # Capitalize words that are not in the LITTLE_WORDS set
            # Also capitalize any word that follows a hyphen
            if words[i].lower() not in LITTLE_WORDS or (i > 1 and words[i-1] == '-'):
                words[i] = words[i].capitalize()
            else:
                # Lowercase all other words (handles cases where user enters all caps)
                words[i] = words[i].lower()
                
        return "".join(words)

    def browse_directory(self, fields):
        directory = filedialog.askdirectory(
            initialdir=self.config.get("last_save_dir"),
            title="Select a Save Directory"
        )
        if directory:
            fields['directory'].delete(0, tk.END)
            fields['directory'].insert(0, directory)
            self.config["last_save_dir"] = directory

    def browse_batch_directory(self, entry_widget):
        """Opens a directory browser and inserts the selection into the provided entry widget."""
        directory = filedialog.askdirectory(
            initialdir=self.config.get("last_open_dir"),
            title="Select a Directory"
        )
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            initialdir=self.config.get("last_open_dir", os.path.join(os.getcwd(), "content")),
            title="Select a post file",
            filetypes=(
                ("All Supported Files", "*.md *.txt"),
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            )
        )
        if not filepath:
            return

        # Check for and store a numeric prefix from the original filename
        basename = os.path.basename(filepath)
        basename_no_ext, _ = os.path.splitext(basename)
        if basename_no_ext.isdigit():
            self.numeric_prefix = basename_no_ext
        else:
            self.numeric_prefix = None # Reset if not numeric

        self.config["last_open_dir"] = os.path.dirname(filepath)
        self.existing_filepath_var.set(filepath)
        self.preview_text.delete("1.0", tk.END)
        fields = self.existing_post_fields

        # Set the directory field
        directory, _ = os.path.split(filepath)
        fields['directory'].delete(0, tk.END)
        fields['directory'].insert(0, directory)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                full_content = f.read()

            content_to_preview = full_content
            if filepath.lower().endswith(".txt"):
                content_to_preview, title = self.convert_txt_to_md(full_content)
                self.populate_fields_from_txt(title)
            else: # Assume markdown file
                header, _ = self.parse_markdown_file(full_content)
                self.populate_fields_from_header(header)

            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", content_to_preview)

            # Generate the new filename after all fields are populated
            self.update_filename(None, fields)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def parse_markdown_file(self, content):
        header = {}
        body_lines = []
        is_header = True
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            # Header ends at the first blank line
            if is_header and not line.strip():
                is_header = False
                body_lines = lines[i+1:]
                break

            if is_header and ":" in line:
                key, value = line.split(":", 1)
                header[key.strip().lower()] = value.strip()
        
        # If the loop finishes and is_header is still true, it means no blank line was found.
        # Treat the whole file as body content with no header.
        if is_header:
            return {}, content
            
        return header, "\n".join(body_lines)

    def populate_fields_from_header(self, header):
        fields = self.existing_post_fields

        title = header.get('title', '')
        fields['title'].delete(0, tk.END)
        fields['title'].insert(0, title)
        
        # Preserve slug from header, otherwise create it from title
        slug = header.get('slug', self.to_slug(title))
        fields['slug'].delete(0, tk.END)
        fields['slug'].insert(0, slug)

        fields['author'].delete(0, tk.END)
        fields['author'].insert(0, header.get('author', 'nameless'))

        fields['date'].delete(0, tk.END)
        fields['date'].insert(0, header.get('date', datetime.now().strftime("%Y-%m-%d %H:%M")))

        fields['status'].set(header.get('status', 'published'))
        fields['category'].set(header.get('category', self.categories[0] if self.categories else ''))

        summary_text = header.get('summary', '')
        # Clean up old prefix if it exists
        prefix = "A summary of the post: "
        if summary_text.startswith(prefix):
            summary_text = summary_text[len(prefix):]
        fields['summary'].delete("1.0", tk.END)
        fields['summary'].insert("1.0", summary_text)

        # Handle tags
        tags_listbox = fields['tags_listbox']
        tags_listbox.selection_clear(0, tk.END)
        if 'tags' in header:
            tags_in_post = {tag.strip() for tag in header['tags'].split(',')}
            for i, tag_in_listbox in enumerate(self.tags):
                if tag_in_listbox in tags_in_post:
                    tags_listbox.selection_set(i)

    def populate_fields_from_txt(self, title):
        if not title:
            return
        
        fields = self.existing_post_fields
        fields['title'].delete(0, tk.END)
        fields['title'].insert(0, title)

        slug = self.to_slug(title)
        fields['slug'].delete(0, tk.END)
        fields['slug'].insert(0, slug)

        fields['filename'].delete(0, tk.END)
        fields['filename'].insert(0, f"{slug}.md")

    def convert_txt_to_md(self, text):
        lines = text.split('\n')
        
        title = ""
        if lines:
            title = lines[0].strip()
            lines[0] = f"# {title}"

        processed_lines = []
        for line in lines:
            stripped_line = line.strip()
            # Heuristic for headings: short, all caps, or ends with no punctuation and is relatively short.
            if stripped_line and (stripped_line.isupper() and len(stripped_line.split()) < 7) or \
               (len(stripped_line.split()) < 7 and not stripped_line.endswith(('.', '!', '?'))):
                processed_lines.append(f"\n## {stripped_line}\n")
            # Heuristic for lists
            elif stripped_line.startswith(('* ', '- ')):
                 processed_lines.append(line)
            # Regular paragraph lines
            else:
                processed_lines.append(line)
        
        # Join lines and handle paragraph breaks
        markdown_text = '\n'.join(processed_lines)
        markdown_text = re.sub(r'\n\n+', '\n\n', markdown_text) # Consolidate blank lines
        return markdown_text, title


    def generate_summary_from_content(self, fields):
        """Determines the correct content source and calls generate_summary."""
        # 'content_editor' exists only in new_post_fields
        if 'content_editor' in fields:
            content_to_summarize = fields['content_editor'].get("1.0", tk.END).strip()
        else:
            # For existing files, parse the body out of the preview text to avoid summarizing the header
            full_preview_content = self.preview_text.get("1.0", tk.END).strip()
            _, content_to_summarize = self.parse_markdown_file(full_preview_content)
        
        self.generate_summary(content_to_summarize, fields['summary'])

    def generate_summary(self, content, summary_field):
        if not content:
            messagebox.showwarning("Warning", "Cannot generate summary from empty content.")
            return
        
        # Clean the markdown for a better summary
        cleaned_content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)      # Headings
        cleaned_content = re.sub(r'---', '', cleaned_content)                     # Horizontal Rules
        cleaned_content = re.sub(r'[\*_`]', '', cleaned_content)                  # Emphasis
        cleaned_content = re.sub(r'!\[.*?\]\(.*?\)', '', cleaned_content)        # Images
        cleaned_content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', cleaned_content)     # Links
        cleaned_content = re.sub(r'^\s*>\s?', '', cleaned_content, flags=re.MULTILINE) # Blockquotes
        cleaned_content = ' '.join(cleaned_content.split()) # Consolidate whitespace
 
        if not cleaned_content:
            summary = "This document appears to contain formatting only, with no text to summarize."
        else:
            # A better placeholder for an "AI" summary
            words = cleaned_content.split()
            summary_word_count = min(50, max(15, int(len(words) * 0.15))) # A bit longer summary
            summary = ' '.join(words[:summary_word_count])
            if len(words) > summary_word_count:
                summary += "..."
        
        # Insert the clean summary without any prefix
        summary_field.delete("1.0", tk.END)
        summary_field.insert("1.0", summary)
        messagebox.showinfo("Success", "Summary generated and inserted.")


    def to_slug(self, s):
        s = s.lower()
        s = re.sub(r'[^a-z0-9\s-]', '', s) # remove non-alphanumeric
        s = re.sub(r'[\s-]+', '-', s)     # replace spaces and repeated hyphens with a single hyphen
        return s.strip('-')

    def generate_slug(self, fields):
        """Generates a slug from the title field and updates the slug and filename fields."""
        title = fields['title'].get()
        if not title:
            messagebox.showwarning("Warning", "Title is empty. Cannot generate slug.")
            return

        slug = self.to_slug(title)
        fields['slug'].delete(0, tk.END)
        fields['slug'].insert(0, slug)
        
        # After generating a new slug, the filename should be updated.
        self.update_filename(None, fields)

    def update_filename(self, event, fields):
        # The 'event' parameter is kept for compatibility but is no longer used
        # to differentiate behavior. Slug is now the single source of truth for the filename.
        slug = fields['slug'].get()

        # Prepend the numeric prefix to the filename if it exists
        if self.numeric_prefix:
            if slug:
                filename = f"{self.numeric_prefix}-{slug}.md"
            else:
                filename = f"{self.numeric_prefix}.md"
        else:
            filename = f"{slug}.md"

        fields['filename'].delete(0, tk.END)
        fields['filename'].insert(0, filename)


    def create_post(self, fields, is_new_post):
        # --- Get data from fields ---
        title = fields['title'].get().strip()
        if not title:
            messagebox.showerror("Error", "Title cannot be empty.")
            return

        slug = fields['slug'].get().strip()
        author = fields['author'].get().strip()
        date = fields['date'].get().strip()
        status = fields['status'].get()
        category = fields['category'].get()
        
        selected_tags_indices = fields['tags_listbox'].curselection()
        selected_tags = [fields['tags_listbox'].get(i) for i in selected_tags_indices]
        tags_str = ", ".join(selected_tags)

        summary = fields['summary'].get("1.0", tk.END).strip()

        # --- Build header ---
        header_parts = [
            f"Title: {title}",
            f"Date: {date}",
            f"Status: {status}",
            f"Category: {category}",
            f"Tags: {tags_str}",
            f"Author: {author}",
        ]
        if slug:
             header_parts.append(f"Slug: {slug}")
        if summary:
            header_parts.append(f"Summary: {summary}")
        
        header = "\n".join(header_parts)
        
        # --- Get content, directory and filename ---
        directory = fields['directory'].get().strip()
        filename = fields['filename'].get().strip()

        if not directory:
            messagebox.showerror("Error", "Save directory cannot be empty.")
            return
        if not filename:
            messagebox.showerror("Error", "Filename cannot be empty.")
            return

        self.config["last_save_dir"] = directory

        separator = "\n\n---\n\n"
        if is_new_post:
            content_body = separator + fields['content_editor'].get("1.0", tk.END)
        else: # Existing post
            # Get full content from preview and re-parse it to get only the body.
            # This prevents duplicating the header if the user didn't remove it manually.
            preview_content = self.preview_text.get("1.0", tk.END)
            _, body_content = self.parse_markdown_file(preview_content)
            content_body = separator + body_content

        # --- Create/overwrite file ---
        if not os.path.exists(directory):
            if messagebox.askyesno("Create Directory", f"The directory '{directory}' does not exist. Create it?"):
                try:
                    os.makedirs(directory)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create directory: {e}")
                    return
            else:
                return
        
        filepath = os.path.join(directory, filename)

        if os.path.exists(filepath):
             if not messagebox.askyesno("Warning", f"File '{filename}' already exists in the target directory. Overwrite?"):
                return
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header)
                f.write(content_body)
            
            self.save_config() # Save config on successful post creation
            messagebox.showinfo("Success", f"Post '{filename}' was successfully saved.")
            if messagebox.askyesno("Open File", "Do you want to open the new post file now?"):
                 os.startfile(filepath) # For Windows
            self.destroy() # Close the app on success
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create post: {e}")


class BatchEditDialog(tk.Toplevel):
    def __init__(self, parent, filepath, file_content):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set() # Make modal
        self.title("Interactive Batch Edit")
        self.geometry("800x600")

        self.result = {"status": "cancel"} # Default result

        # --- Data ---
        self.filepath = filepath
        self.file_content = file_content
        self.parent_app = parent # To access helper methods like to_slug

        # --- Widgets ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # Content Preview
        preview_frame = ttk.LabelFrame(main_frame, text=f"Preview: {os.path.basename(filepath)}", padding=5)
        preview_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)

        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=15)
        preview_scroll = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        self.preview_text['yscrollcommand'] = preview_scroll.set
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # Entry fields
        entry_frame = ttk.Frame(main_frame)
        entry_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        entry_frame.columnconfigure(1, weight=1)

        # Title
        ttk.Label(entry_frame, text="Title:").grid(row=0, column=0, sticky="w", pady=2)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(entry_frame, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=2)

        # Slug
        ttk.Label(entry_frame, text="Slug:").grid(row=1, column=0, sticky="w", pady=2)
        self.slug_var = tk.StringVar()
        slug_entry_frame = ttk.Frame(entry_frame)
        slug_entry_frame.grid(row=1, column=1, sticky="ew", pady=2)
        slug_entry_frame.columnconfigure(0, weight=1)
        self.slug_entry = ttk.Entry(slug_entry_frame, textvariable=self.slug_var)
        self.slug_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(slug_entry_frame, text="Generate Slug", command=self.generate_slug).pack(side=tk.LEFT, padx=(5,0))

        # Summary
        ttk.Label(entry_frame, text="Summary:").grid(row=2, column=0, sticky="nw", pady=2)
        summary_frame = ttk.Frame(entry_frame)
        summary_frame.grid(row=2, column=1, sticky="ew", pady=2)
        summary_frame.columnconfigure(0, weight=1)
        self.summary_text = tk.Text(summary_frame, wrap=tk.WORD, height=4)
        self.summary_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(summary_frame, text="Generate Summary", command=self.generate_summary_for_dialog).pack(side=tk.LEFT, padx=(5,0), anchor="center")
        
        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=1, sticky="e", pady=(20, 0))
        ttk.Button(button_frame, text="Save & Next", command=self.on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Skip", command=self.on_skip).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel Batch", command=self.on_cancel).pack(side=tk.RIGHT)

        main_frame.rowconfigure(0, weight=1) # Make preview expand

        # Populate initial title/slug and content
        self.populate_initial_fields()

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def populate_initial_fields(self):
        """Pre-populates the dialog's fields based on the file content."""
        title = ""
        content_for_editor = self.file_content # Default to raw content

        if self.filepath.lower().endswith(".txt"):
            # For text files, do an initial conversion to MD for the editor
            converted_md, title = self.parent_app.convert_txt_to_md(self.file_content)
            content_for_editor = converted_md
        elif self.filepath.lower().endswith(".md"):
            # For markdown, just parse the title out
            header, _ = self.parent_app.parse_markdown_file(self.file_content)
            title = header.get('title', '')
            summary = header.get('summary', '')
        
        # Set the content in the editor
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", content_for_editor)
        
        self.title_var.set(title)
        self.summary_text.insert("1.0", summary)
        self.slug_var.set(self.parent_app.to_slug(title))
        self.title_entry.focus_set()


    def generate_slug(self):
        slug = self.parent_app.to_slug(self.title_var.get())
        self.slug_var.set(slug)

    def generate_summary_for_dialog(self):
        """Calls the main app's summary generation method."""
        content = self.preview_text.get("1.0", tk.END).strip()
        _, body_content = self.parent_app.parse_markdown_file(content)
        self.parent_app.generate_summary(body_content, self.summary_text)

    def on_save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Title cannot be empty to save.", parent=self)
            return
            
        self.result = {
            "status": "save",
            "title": title,
            "slug": self.slug_var.get().strip() or self.parent_app.to_slug(title),
            "content": self.preview_text.get("1.0", tk.END),
            "summary": self.summary_text.get("1.0", tk.END).strip()
        }
        self.destroy()

    def on_skip(self):
        self.result = {"status": "skip"}
        self.destroy()

    def on_cancel(self):
        if messagebox.askyesno("Cancel Batch", "Are you sure you want to cancel the entire batch process?", parent=self):
            self.result = {"status": "cancel"}
            self.destroy()
        else:
            # If user clicks "No", do nothing, keep the dialog open.
            pass

    def show(self):
        self.wait_window(self)
        return self.result


if __name__ == "__main__":
    app = PostCreator()
    app.mainloop() 