import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


DATA_FOLDER = "subjects"
DATE_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%d%m%Y","%d.%m.%Y"]


def clean_subject(subject):
    """Make a subject name safe to use as a file name."""
    return subject.strip().replace("/", "-").replace("\\", "-")


def get_subject_file(subject):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    return os.path.join(DATA_FOLDER, clean_subject(subject) + ".json")


def get_subjects():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    files = [file for file in os.listdir(DATA_FOLDER) if file.endswith(".json")]
    return sorted(file[:-5] for file in files)


def load_topics(subject):
    try:
        with open(get_subject_file(subject), "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_topics(subject, topics):
    with open(get_subject_file(subject), "w") as file:
        json.dump(topics, file, indent=4)


def convert_date(text):
    """Accept several date formats and store the date as DD-MM-YYYY."""
    for date_format in DATE_FORMATS:
        try:
            date = datetime.strptime(text.strip(), date_format)
            return date.strftime("%d-%m-%Y")
        except ValueError:
            pass
    return None


def days_until_exam(exam_date):
    exam = datetime.strptime(exam_date, "%d-%m-%Y")
    return (exam - datetime.today()).days




def days_since_revision(last_revised):
    """Return the number of days since a topic was last revised."""
    revised = datetime.strptime(last_revised, "%d-%m-%Y")
    return (datetime.today() - revised).days


def revision_status(days):
    """Return a friendly message for how long ago revision happened."""
    if days < 0:
        return "Date is in the future"
    if days == 0:
        return "Revised today"
    if days == 1:
        return "1 day since revision"
    return f"{days} days since revision"


def exam_status(days):
    """Return a friendly message for time remaining until an exam."""
    if days < 0:
        return f"Exam was {abs(days)} days ago"
    if days == 0:
        return "Exam is today"
    if days == 1:
        return "1 day until exam"
    return f"{days} days until exam"


def calculate_priority(topic):
    """Calculate a priority from confidence, exam date, difficulty and recency."""

    confidence = topic["confidence"]
    confidence_score = 6 - confidence

    days = days_until_exam(topic["exam_date"])

    if days <= 0:
        exam_score = 10
    elif days <= 7:
        exam_score = 10
    elif days <= 14:
        exam_score = 8
    elif days <= 30:
        exam_score = 5
    elif days <= 60:
        exam_score = 2
    else:
        exam_score = 0

    
    difficulty_score = topic["difficulty"] * 2

    last_revised = datetime.strptime(topic["last_revised"], "%d-%m-%Y")
    days_since_revision = (datetime.today() - last_revised).days

    if days_since_revision <= 1:
        recency_score = 0
    elif days_since_revision <= 3:
        recency_score = 2
    elif days_since_revision <= 6:
        recency_score = 5
    elif days_since_revision <= 13:
        recency_score = 8
    else:
        recency_score = 10

    priority = (
        confidence_score * 0.40
        + exam_score * 0.30
        + difficulty_score * 0.20
        + recency_score * 0.10
    )

    if priority < 4:
        level = "Low"
    elif priority < 7:
        level = "Medium"
    else:
        level = "High"

    return round(priority, 1), level


def all_topics():
    """Return every topic from every subject."""
    topics = []
    for subject in get_subjects():
        topics.extend(load_topics(subject))
    return topics




class ReviseWise:
    """Main ReviseWise application."""

    BG = "#FFF7FB"
    CARD = "#FFFFFF"
    PURPLE = "#9B7EDE"
    PURPLE_DARK = "#7055B8"
    PINK = "#F3A6C8"
    PINK_LIGHT = "#FFE7F1"
    BLUE_LIGHT = "#E7F0FF"
    TEXT = "#3F3850"
    MUTED = "#827A8F"
    GREEN = "#8BC9A8"
    BORDER = "#E8DDEA"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ReviseWise ✿")
        self.root.geometry("900x650")
        self.root.minsize(780, 560)
        self.root.configure(bg=self.BG)

        self.font = "Segoe UI"
        self.title_font = (self.font, 24, "bold")
        self.heading_font = (self.font, 17, "bold")
        self.normal_font = (self.font, 11)
        self.button_font = (self.font, 11, "bold")

        self.show_home()





    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def header(self, title, subtitle=""):
        frame = tk.Frame(self.root, bg=self.BG)
        frame.pack(fill="x", padx=40, pady=(28, 15))

        tk.Label(
            frame,
            text="ReviseWise ✿",
            font=(self.font, 13, "bold"),
            fg=self.PURPLE_DARK,
            bg=self.BG
        ).pack(anchor="w")

        tk.Label(
            frame,
            text=title,
            font=self.title_font,
            fg=self.TEXT,
            bg=self.BG
        ).pack(anchor="w", pady=(5, 0))

        if subtitle:
            tk.Label(
                frame,
                text=subtitle,
                font=self.normal_font,
                fg=self.MUTED,
                bg=self.BG
            ).pack(anchor="w", pady=(3, 0))

    def card(self, parent):
        return tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
            bd=0
        )

    def button(self, parent, text, command, colour=None):
        colour = colour or self.PURPLE
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=self.button_font,
            fg="white",
            bg=colour,
            activebackground=self.PURPLE_DARK,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2"
        )

    def back_button(self, parent):
        return tk.Button(
            parent,
            text="← Back to Home",
            command=self.show_home,
            font=self.normal_font,
            fg=self.PURPLE_DARK,
            bg=self.BG,
            activebackground=self.BG,
            relief="flat",
            bd=0,
            cursor="hand2"
        )

    def entry(self, parent, width=35):
        return tk.Entry(
            parent,
            width=width,
            font=self.normal_font,
            fg=self.TEXT,
            bg="#FFFCFE",
            relief="flat",
            highlightbackground=self.BORDER,
            highlightcolor=self.PURPLE,
            highlightthickness=1
        )

    def label(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            font=(self.font, 10, "bold"),
            fg=self.TEXT,
            bg=self.CARD
        )

    def output_box(self, parent, height=18):
        box = tk.Text(
            parent,
            height=height,
            font=("Consolas", 10),
            fg=self.TEXT,
            bg="#FFFCFE",
            relief="flat",
            highlightbackground=self.BORDER,
            highlightthickness=1,
            wrap="word",
            padx=12,
            pady=10
        )
        box.pack(fill="both", expand=True, padx=20, pady=20)
        return box




    def show_home(self):
        self.clear()

        top = tk.Frame(self.root, bg=self.BG)
        top.pack(fill="x", padx=50, pady=(45, 10))

        tk.Label(
            top,
            text="ReviseWise ✿",
            font=(self.font, 32, "bold"),
            fg=self.PURPLE_DARK,
            bg=self.BG
        ).pack()

        tk.Label(
            top,
            text="Your little revision planner ♡",
            font=(self.font, 12),
            fg=self.MUTED,
            bg=self.BG
        ).pack(pady=(4, 0))

        subjects = len(get_subjects())
        topics = len(all_topics())

        stats = tk.Frame(self.root, bg=self.BG)
        stats.pack(pady=20)

        self.stat_card(stats, "Subjects", subjects, self.PINK_LIGHT, 0)
        self.stat_card(stats, "Topics", topics, self.BLUE_LIGHT, 1)

        menu = tk.Frame(self.root, bg=self.BG)
        menu.pack(padx=50, pady=15, fill="x")

        buttons = [
            ("＋  Add Topic", self.add_topic_gui),
            ("♡  View Topics", self.view_topics_gui),
            ("★  Revision Priorities", self.priorities_gui),
            ("⌕  Search Topics", self.search_gui),
            ("↕  Sort Topics", self.sort_gui),
            ("✎  Edit Topic", self.edit_gui)
        ]

        for index, (text, command) in enumerate(buttons):
            row = index // 3
            column = index % 3
            card = self.card(menu)
            card.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
            menu.columnconfigure(column, weight=1)

            tk.Button(
                card,
                text=text,
                command=command,
                font=(self.font, 11, "bold"),
                fg=self.TEXT,
                bg=self.CARD,
                activebackground=self.PINK_LIGHT,
                relief="flat",
                bd=0,
                pady=20,
                cursor="hand2"
            ).pack(fill="both", expand=True)

        self.button(self.root, "Exit", self.root.destroy, self.PINK).pack(pady=15)

    def stat_card(self, parent, title, value, colour, column):
        card = tk.Frame(parent, bg=colour, width=170, height=75)
        card.grid(row=0, column=column, padx=8)
        card.pack_propagate(False)

        tk.Label(
            card,
            text=str(value),
            font=(self.font, 20, "bold"),
            fg=self.TEXT,
            bg=colour
        ).pack(pady=(10, 0))

        tk.Label(
            card,
            text=title,
            font=(self.font, 9),
            fg=self.MUTED,
            bg=colour
        ).pack()



    def add_topic_gui(self):
        self.clear()
        self.header("Add a Topic", "Tell ReviseWise what you are working on.")

        card = self.card(self.root)
        card.pack(padx=100, pady=5, fill="x")

        fields = {}
        names = [
            "Subject",
            "Topic name",
            "Confidence (1-5)",
            "Difficulty (1-5)",
            "Exam date",
            "Last revised"
        ]

        for name in names:
            row = tk.Frame(card, bg=self.CARD)
            row.pack(fill="x", padx=30, pady=7)

            self.label(row, name).pack(side="left")
            fields[name] = self.entry(row, 30)
            fields[name].pack(side="right")

        hint = tk.Label(
            card,
            text="Date examples: 02-10-2026  •  02/10/2026  •  02102026",
            font=(self.font, 9),
            fg=self.MUTED,
            bg=self.CARD
        )
        hint.pack(pady=(2, 15))

        def save():
            subject = fields["Subject"].get().strip()
            topic_name = fields["Topic name"].get().strip()

            if not subject or not topic_name:
                messagebox.showerror("Missing information", "Please enter a subject and topic name.")
                return

            try:
                confidence = int(fields["Confidence (1-5)"].get())
                difficulty = int(fields["Difficulty (1-5)"].get())

                if not 1 <= confidence <= 5 or not 1 <= difficulty <= 5:
                    raise ValueError
                
            except ValueError:
                messagebox.showerror("Invalid rating", "Confidence and difficulty must be numbers from 1 to 5.")
                return

            exam_date = convert_date(fields["Exam date"].get())
            last_revised = convert_date(fields["Last revised"].get())

            if exam_date is None or last_revised is None:
                messagebox.showerror(
                    "Invalid date",
                    "Please enter valid dates.\n\nExample: 02-10-2026"
                )
                return

            topic = {
                "subject": subject,
                "name": topic_name,
                "confidence": confidence,
                "difficulty": difficulty,
                "exam_date": exam_date,
                "last_revised": last_revised,
                "times_revised": 0,
                "completed": False
            }

            topics = load_topics(subject)
            topics.append(topic)
            save_topics(subject, topics)

            messagebox.showinfo("Saved ✿", f"{topic_name} was added successfully!")
            self.show_home()

        buttons = tk.Frame(self.root, bg=self.BG)
        buttons.pack(pady=18)
        self.button(buttons, "Save Topic", save, self.PURPLE).pack(side="left", padx=8)
        self.back_button(buttons).pack(side="left", padx=8)

    

    def view_topics_gui(self):
        self.clear()
        self.header("View Topics", "Choose a subject to see its topics.")

        subjects = get_subjects()
        if not subjects:
            self.empty_page("No subjects yet", "Add your first topic to get started!")
            return

        controls = self.card(self.root)
        controls.pack(fill="x", padx=70, pady=5)

        tk.Label(
            controls,
            text="Subject:",
            font=self.normal_font,
            fg=self.TEXT,
            bg=self.CARD
        ).pack(side="left", padx=(25, 10), pady=18)

        selected = tk.StringVar(value=subjects[0])
        menu = tk.OptionMenu(controls, selected, *subjects)
        menu.config(font=self.normal_font, bg=self.PINK_LIGHT, fg=self.TEXT, relief="flat")
        menu.pack(side="left")

        output = self.output_box(self.root, 20)

        def display(*args):
            output.delete("1.0", tk.END)
            subject = selected.get()
            topics = load_topics(subject)

            if not topics:
                output.insert(tk.END, "No topics have been added to this subject yet.")
                return

            for number, topic in enumerate(topics, 1):
                output.insert(
                    tk.END,
                    f"{number}. {topic['name']}\n"
                    f"   Confidence: {topic['confidence']}/5\n"
                    f"   Difficulty: {topic['difficulty']}/5\n"
                    f"   Exam: {topic['exam_date']} ({exam_status(days_until_exam(topic['exam_date']))})\n"
                    f"   Last revised: {topic['last_revised']} ({revision_status(days_since_revision(topic['last_revised']))})\n"
                    f"   Times revised: {topic.get('times_revised', 0)}\n"
                    f"   {'─' * 55}\n"
                )

        selected.trace_add("write", display)
        display()

        self.back_button(self.root).pack(pady=10)


    def priorities_gui(self):
        self.clear()
        self.header("Revision Priorities", "Revise the topics that need your attention most.")

        subjects = get_subjects()
        if not subjects:
            self.empty_page("No topics yet", "Add some topics before checking priorities.")
            return

        choices = ["All Subjects"] + subjects
        selected = tk.StringVar(value=choices[0])

        controls = self.card(self.root)
        controls.pack(fill="x", padx=70, pady=5)

        tk.Label(
            controls,
            text="Show:",
            font=self.normal_font,
            fg=self.TEXT,
            bg=self.CARD
        ).pack(side="left", padx=(25, 10), pady=18)

        menu = tk.OptionMenu(controls, selected, *choices)
        menu.config(font=self.normal_font, bg=self.PINK_LIGHT, fg=self.TEXT, relief="flat")
        menu.pack(side="left")

        output = self.output_box(self.root, 20)

        def display(*args):
            output.delete("1.0", tk.END)

            if selected.get() == "All Subjects":
                topics = all_topics()
            else:
                topics = load_topics(selected.get())

            ranked = []
            for topic in topics:
                try:
                    priority, level = calculate_priority(topic)
                    ranked.append((priority, level, topic))
                except (ValueError, KeyError):
                    pass

            ranked.sort(reverse=True, key=lambda item: item[0])

            if not ranked:
                output.insert(tk.END, "No valid topics to display.")
                return

            for number, (priority, level, topic) in enumerate(ranked, 1):
                output.insert(
                    tk.END,
                    f"{number}. {topic['name']}  —  {level} priority\n"
                    f"   Subject: {topic['subject']}\n"
                    f"   Priority score: {priority}/10\n"
                    f"   Confidence: {topic['confidence']}/5\n"
                    f"   Difficulty: {topic['difficulty']}/5\n"
                    f"   Exam: {topic['exam_date']} ({exam_status(days_until_exam(topic['exam_date']))})\n"
                    f"   Last revised: {topic['last_revised']} ({revision_status(days_since_revision(topic['last_revised']))})\n"
                    f"   {'─' * 55}\n"
                )

        selected.trace_add("write", display)
        display()

        self.back_button(self.root).pack(pady=10)

    
    

    def search_gui(self):
        self.clear()
        self.header("Search Topics", "Find a topic by its name or subject.")

        controls = self.card(self.root)
        controls.pack(fill="x", padx=70, pady=5)

        search_box = self.entry(controls, 45)
        search_box.pack(side="left", padx=20, pady=18)

        output = self.output_box(self.root, 20)

        def search():
            term = search_box.get().strip().lower()
            output.delete("1.0", tk.END)

            if not term:
                output.insert(tk.END, "Type something to search for.")
                return

            matches = []
            for topic in all_topics():
                if term in topic["name"].lower() or term in topic["subject"].lower():
                    matches.append(topic)

            if not matches:
                output.insert(tk.END, "No matching topics found.")
                return

            for topic in matches:
                output.insert(
                    tk.END,
                    f"{topic['name']}\n"
                    f"Subject: {topic['subject']}\n"
                    f"Confidence: {topic['confidence']}/5\n"
                    f"Exam: {topic['exam_date']} ({exam_status(days_until_exam(topic['exam_date']))})\n"
                    f"Last revised: {topic['last_revised']} ({revision_status(days_since_revision(topic['last_revised']))})\n"
                    f"{'─' * 55}\n"
                )

        self.button(controls, "Search", search).pack(side="left", padx=5)
        search_box.bind("<Return>", lambda event: search())
        self.back_button(self.root).pack(pady=10)

   
   

    def sort_gui(self):
        self.clear()
        self.header("Sort Topics", "Choose how you want your topics arranged.")

        options = [
            "Confidence: lowest first",
            "Difficulty: highest first",
            "Exam: soonest first",
            "Name: A-Z"
        ]

        selected = tk.StringVar(value=options[0])

        controls = self.card(self.root)
        controls.pack(fill="x", padx=70, pady=5)

        menu = tk.OptionMenu(controls, selected, *options)
        menu.config(font=self.normal_font, bg=self.PINK_LIGHT, fg=self.TEXT, relief="flat")
        menu.pack(side="left", padx=20, pady=18)

        output = self.output_box(self.root, 20)

        def sort_topics(*args):
            topics = all_topics()
            choice = selected.get()

            if choice.startswith("Confidence"):
                topics.sort(key=lambda topic: topic["confidence"])
            elif choice.startswith("Difficulty"):
                topics.sort(key=lambda topic: topic["difficulty"], reverse=True)
            elif choice.startswith("Exam"):
                topics.sort(
                    key=lambda topic: datetime.strptime(topic["exam_date"], "%d-%m-%Y")
                )
            else:
                topics.sort(key=lambda topic: topic["name"].lower())

            output.delete("1.0", tk.END)

            if not topics:
                output.insert(tk.END, "No topics to sort.")
                return

            for number, topic in enumerate(topics, 1):
                output.insert(
                    tk.END,
                    f"{number}. {topic['name']} — {topic['subject']}\n"
                    f"   Confidence: {topic['confidence']}/5   "
                    f"Difficulty: {topic['difficulty']}/5   "
                    f"Exam: {topic['exam_date']} ({exam_status(days_until_exam(topic['exam_date']))})\n"
                    f"Last revised: {topic['last_revised']} ({revision_status(days_since_revision(topic['last_revised']))})\n"
                    f"{'─' * 55}\n"
                )

        selected.trace_add("write", sort_topics)
        sort_topics()

        self.back_button(self.root).pack(pady=10)


    def edit_gui(self):
        self.clear()
        self.header("Edit a Topic", "Update information whenever your revision changes.")

        subjects = get_subjects()
        if not subjects:
            self.empty_page("No subjects yet", "Add a topic before editing one.")
            return

        card = self.card(self.root)
        card.pack(padx=100, pady=5, fill="x")

        subject_var = tk.StringVar(value=subjects[0])
        topic_var = tk.StringVar()
        field_var = tk.StringVar(value="Confidence")

        self.form_option(card, "Subject", subject_var, subjects)

        topic_menu = tk.OptionMenu(card, topic_var, "Choose a topic")
        topic_menu.config(font=self.normal_font, bg="#FFFCFE", fg=self.TEXT, relief="flat")
        self.form_option_widget(card, "Topic", topic_menu)

        fields = ["Confidence", "Difficulty", "Exam date", "Last revised"]
        field_menu = tk.OptionMenu(card, field_var, *fields)
        field_menu.config(font=self.normal_font, bg="#FFFCFE", fg=self.TEXT, relief="flat")
        self.form_option_widget(card, "Change", field_menu)

        new_value = self.entry(card, 30)
        self.form_widget(card, "New value", new_value)

        def update_topic_menu(*args):
            topics = load_topics(subject_var.get())
            topic_names = [topic["name"] for topic in topics]

            topic_menu["menu"].delete(0, "end")
            for name in topic_names:
                topic_menu["menu"].add_command(
                    label=name,
                    command=lambda value=name: topic_var.set(value)
                )

            topic_var.set(topic_names[0] if topic_names else "No topics")

        def save_edit():
            if topic_var.get() in ("", "No topics"):
                messagebox.showerror("No topic", "Please choose a topic.")
                return

            topics = load_topics(subject_var.get())
            topic = next((t for t in topics if t["name"] == topic_var.get()), None)

            if topic is None:
                messagebox.showerror("Error", "That topic could not be found.")
                return

            value = new_value.get().strip()
            field = field_var.get()

            if field in ("Confidence", "Difficulty"):
                try:
                    value = int(value)
                    if not 1 <= value <= 5:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Invalid rating", "Enter a number from 1 to 5.")
                    return

                key = field.lower()
                topic[key] = value

            elif field in ("Exam date", "Last revised"):
                value = convert_date(value)
                if value is None:
                    messagebox.showerror("Invalid date", "Enter a valid date, such as 02-10-2026.")
                    return

                key = "exam_date" if field == "Exam date" else "last_revised"
                topic[key] = value

            save_topics(subject_var.get(), topics)
            messagebox.showinfo("Updated ✿", f"{topic['name']} has been updated.")
            self.show_home()

        subject_var.trace_add("write", update_topic_menu)
        update_topic_menu()

        buttons = tk.Frame(self.root, bg=self.BG)
        buttons.pack(pady=18)
        self.button(buttons, "Save Changes", save_edit, self.PURPLE).pack(side="left", padx=8)
        self.back_button(buttons).pack(side="left", padx=8)

    def form_option(self, parent, title, variable, values):
        menu = tk.OptionMenu(parent, variable, *values)
        menu.config(font=self.normal_font, bg="#FFFCFE", fg=self.TEXT, relief="flat")
        self.form_option_widget(parent, title, menu)

    def form_option_widget(self, parent, title, widget):
        row = tk.Frame(parent, bg=self.CARD)
        row.pack(fill="x", padx=30, pady=9)
        self.label(row, title).pack(side="left")
        widget.pack(side="right")

    def form_widget(self, parent, title, widget):
        row = tk.Frame(parent, bg=self.CARD)
        row.pack(fill="x", padx=30, pady=9)
        self.label(row, title).pack(side="left")
        widget.pack(side="right")

    



    def empty_page(self, title, message):
        card = self.card(self.root)
        card.pack(fill="both", expand=True, padx=100, pady=30)

        tk.Label(
            card,
            text="♡",
            font=(self.font, 35),
            fg=self.PINK,
            bg=self.CARD
        ).pack(pady=(80, 10))

        tk.Label(
            card,
            text=title,
            font=self.heading_font,
            fg=self.TEXT,
            bg=self.CARD
        ).pack()

        tk.Label(
            card,
            text=message,
            font=self.normal_font,
            fg=self.MUTED,
            bg=self.CARD
        ).pack(pady=5)

        self.back_button(self.root).pack(pady=15)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ReviseWise()
    app.run()
