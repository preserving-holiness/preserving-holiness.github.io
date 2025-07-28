import tkinter as tk
from tkinter import ttk, messagebox
import textwrap
import os

class PromptCreator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Article Generator Prompt Creator (v2.0)")
        self.geometry("800x900")

        # --- Main container ---
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(3, weight=1) # Allow output frame to expand
        main_frame.columnconfigure(0, weight=1)

        self.fields = {}

        # --- Input from Extractor ---
        extractor_frame = ttk.LabelFrame(main_frame, text="2. INPUT DATA FROM EXTRACTOR PROMPT", padding="10")
        extractor_frame.pack(fill=tk.X, pady=(0, 10))
        extractor_frame.columnconfigure(0, weight=1)
        
        self.fields['extractor_output'] = tk.Text(extractor_frame, height=8, wrap=tk.WORD)
        self.fields['extractor_output'].pack(fill=tk.X, expand=True)
        self.fields['extractor_output'].insert("1.0", "[PASTE THE ENTIRE OUTPUT FROM THE 'CONTENT EXTRACTOR' PROMPT HERE...]")


        # --- Additional Context ---
        context_frame = ttk.LabelFrame(main_frame, text="Additional Context", padding="10")
        context_frame.pack(fill=tk.X)
        context_frame.columnconfigure(1, weight=1)

        # Row 0: Book Title
        ttk.Label(context_frame, text="Book Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fields['book_title'] = ttk.Entry(context_frame)
        self.fields['book_title'].grid(row=0, column=1, sticky="we", pady=5)
        
        # Row 1: Book Author
        ttk.Label(context_frame, text="Book Author:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fields['book_author'] = ttk.Entry(context_frame)
        self.fields['book_author'].grid(row=1, column=1, sticky="we", pady=5)

        # Row 2: Chapter
        ttk.Label(context_frame, text="Chapter Number/Title:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.fields['chapter'] = ttk.Entry(context_frame)
        self.fields['chapter'].grid(row=2, column=1, sticky="we", pady=5)
        

        # --- Action Button ---
        action_frame = ttk.Frame(main_frame, padding=(0, 10))
        action_frame.pack(fill=tk.X)
        
        generate_button = ttk.Button(action_frame, text="Generate Prompt", command=self.generate_prompt)
        generate_button.pack(side=tk.RIGHT, pady=5)

        # --- Output Textbox ---
        output_frame = ttk.LabelFrame(main_frame, text="Generated Prompt", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, state="disabled", height=25, bg="#f0f0f0")
        
        output_scroll = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        self.output_text['yscrollcommand'] = output_scroll.set
        
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(fill=tk.BOTH, expand=True)


    def generate_prompt(self):
        """Gathers data from fields and builds the final prompt."""
        
        # --- Get data from fields ---
        extractor_output = self.fields['extractor_output'].get("1.0", tk.END).strip()
        book_title = self.fields['book_title'].get().strip()
        book_author = self.fields['book_author'].get().strip()
        chapter = self.fields['chapter'].get().strip()
        
        # --- Validation ---
        if not all([book_title, book_author, chapter, extractor_output]) or extractor_output.startswith("[PASTE"):
            messagebox.showwarning("Incomplete Information", "Please paste the extractor output and fill in all 'Additional Context' fields.")
            return

        # --- Build the prompt string ---
        prompt = f"""
START OF PROMPT

# 1. PERSONA AND CORE INSTRUCTIONS

You are an expert theological communicator and writing assistant. You will be given a pre-analyzed summary from a theological analyst. Your job is to take this structured input and expand it into a full, in-depth article.

Your role is to act as a "Translator & Tour Guide" for the reader. The target audience is modern readers with little to no background in theological texts. The goal is to make the core message accessible, practical, and engaging.

Your tone should be grounded in Practical Theology, focusing on actionable principles and clear, doctrinal truth as presented in the source material. Avoid vague or overly "spiritualistic" language. The final article should be comprehensive and helpful.

# 2. INPUT DATA FROM EXTRACTOR PROMPT

{extractor_output}

Additional Context:

Book Title: [{book_title}]
Book Author: [{book_author}]
Chapter Number/Title: [{chapter}]

# 3. ARTICLE GENERATION TASK

Based on the pre-analyzed input data above, generate a draft for the article by following these steps precisely:

Step 1: Brainstorm Titles
Generate 5 potential titles for this article. They should be based on the provided "Core Idea."

Step 2: Write the Introduction
Write an introduction (approx. 150 words) that:
a. Hooks the reader with a relatable modern problem.
b. Introduces the book's author and the chapter's topic.
c. Presents the "Core Idea" from the input data in a simple and compelling way.

Step 3: Develop the Core Explanation with the Analogy
Take the "Core Idea" and the "Suggested Analogy" from the input data. Write a detailed section that fully explains the theological principle using the analogy as the primary teaching tool. Elaborate on how the analogy works and what it teaches the reader.

Step 4: Create the "Quote Sandwich"
Integrate the "Key Quote" from the input data.
a. First, set up the quote in your own words.
b. Then, present the "Key Quote," formatted as a blockquote.
c. Finally, explain the quote's meaning and practical importance.

Step 5: Write the "Modern Application" Section
Create a section titled "Why This Still Matters Today." Connect the "Core Idea" to specific, modern-day challenges or experiences. This section should provide clear, actionable advice.

Step 6: Write the Conclusion
Write a short, powerful conclusion (approx. 100 words) that summarizes the main takeaway from the "Core Idea" and gives the reader a simple, encouraging action step to apply to their life.

END OF PROMPT
"""
        
        # --- Display the prompt ---
        clean_prompt = textwrap.dedent(prompt).strip()
        
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", clean_prompt)
        self.output_text.config(state="disabled")

if __name__ == "__main__":
    app = PromptCreator()
    app.mainloop() 