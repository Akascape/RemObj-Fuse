"""
RemObj Setup Manager
=================
Author: Akascape
Version: 1.0
License: MIT License
"""

import os
import sys
import subprocess
import threading
import io 
from pathlib import Path

# Handle pythonw.exe environment where stdout and stderr are None
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont 

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Restart the application after installing the required libraries to use the testing utility.")

def is_library_installed():
    try:
        import onnxruntime
        import cv2
        import numpy
        import PIL
        return True
    except ImportError:
        return False

def install_libraries(option, callback):
    def run():
        # Standard pip command
        pip_cmd = [sys.executable, "-m", "pip", "install"]
        
        # Determine packages based on option
        if option == "CPU Only":
            packages = ["onnxruntime", "opencv-python", "numpy", "pillow"]
            uninstall_target = "onnxruntime-gpu"
        elif option == "CUDA Support":
            packages = ["onnxruntime-gpu", "opencv-python", "numpy", "pillow"]
            uninstall_target = "onnxruntime"
        else:
            packages = ["onnxruntime", "opencv-python", "numpy", "pillow"]
            uninstall_target = "onnxruntime-gpu"
            
        try:
            # Uninstall conflicting ONNX Runtime first to avoid CPU/GPU provider conflicts
            subprocess.run([sys.executable, "-m", "pip", "uninstall", uninstall_target, "-y"])
        except Exception:
            pass

        pip_cmd += packages
        try:
            proc = subprocess.Popen(pip_cmd)
            proc.wait()
            callback(proc.returncode == 0)
        except Exception:
            callback(False)

    threading.Thread(target=run, daemon=True).start()

class RemObjSetupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RemObj Setup Manager")
        self.geometry("800x600")
        self.resizable(True, True)
        self.minsize(700, 500)
        
        default_font = tkfont.nametofont("TkDefaultFont")
        self.font_family = default_font.actual()["family"]

        # Dark theme colors
        self.colors = {
            'bg_primary': '#1e1e1e',      # Main background
            'bg_secondary': '#2d2d2d',    # Card/frame background
            'bg_tertiary': '#404040',      # Slightly lighter elements
            'text_primary': '#ffffff',    # Main text
            'text_secondary': '#b3b3b3',  # Secondary text
            'text_disabled': '#666666',   # Disabled text
            'accent': '#007acc',          # Accent blue
            'accent_hover': '#1e90ff',    # Lighter blue for hover
            'success': '#4caf50',         # Success green
            'warning': '#ff9800',         # Warning orange
            'error': '#f44336',           # Error red
            'border': '#555555'           # Border color
        }
        
        self.configure(bg=self.colors['bg_primary'])
        self.setup_dark_theme()
        
        self.libraries_installed = is_library_installed()
        self.is_installing = False

        self.input_image_path = None
        self.input_mask_path = None
        self.processed_image_path = None
        self.tk_input_image = None
        self.tk_mask_image = None
        self.tk_output_image = None
        
        self.center_window()
        self.create_main_page()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if self.is_installing:
            if messagebox.askyesno("Exit Confirmation", "An installation is in progress. Are you sure you want to exit?"):
                self.destroy()
        else:
            self.destroy()
            
    def setup_dark_theme(self):
        style = ttk.Style()
        style.theme_use('alt')
        
        self.option_add('*TCombobox*Listbox.background', self.colors['bg_tertiary'])
        self.option_add('*TCombobox*Listbox.foreground', self.colors['text_primary'])
        self.option_add('*TCombobox*Listbox.selectBackground', self.colors['accent'])
        self.option_add('*TCombobox*Listbox.selectForeground', self.colors['text_primary'])
        
        style.configure('Dark.TFrame',
                        background=self.colors['bg_secondary'],
                        borderwidth=1,
                        relief='solid')
        
        style.configure('Dark2.TFrame',
                        background=self.colors['bg_primary'],
                        borderwidth=0,
                        relief='flat')
        
        style.configure('Main.TFrame',
                        background=self.colors['bg_primary'])
        
        style.configure('Title.TLabel',
                        background=self.colors['bg_secondary'],
                        foreground=self.colors['text_primary'],
                        font=(self.font_family, 18, 'bold'))
        
        style.configure('Subtitle.TLabel',
                        background=self.colors['bg_secondary'],
                        foreground=self.colors['text_secondary'],
                        font=(self.font_family, 12))
        
        style.configure('Info.TLabel',
                        background=self.colors['bg_secondary'],
                        foreground=self.colors['text_secondary'],
                        font=(self.font_family, 10))
        
        style.configure('Success.TLabel',
                        background=self.colors['bg_secondary'],
                        foreground=self.colors['success'],
                        font=(self.font_family, 14, 'bold'))
        
        style.configure('Action.TButton',
                          background=self.colors['accent'],
                          foreground='white',
                          focuscolor=self.colors['accent'], 
                          font=(self.font_family, 10, 'bold'),
                          padding=(20, 8),
                          borderwidth=0,
                          width=-1)
        
        style.map('Action.TButton',
                  background=[('active', self.colors['accent_hover']),
                               ('pressed', '#005999')], relief=[('pressed', 'flat')])
        
        style.configure('Secondary.TButton',
                        background=self.colors['bg_tertiary'],
                        foreground=self.colors['text_primary'],
                        font=(self.font_family, 9),
                        focuscolor=self.colors['accent'],
                        padding=(10, 5),
                        borderwidth=1,
                        relief='flat',
                        width=-1)
        
        style.map('Secondary.TButton',
                  background=[('active', self.colors['accent_hover']),
                               ('pressed', '#005999')], relief=[('pressed', 'flat')])
        
        style.configure('Dark.Horizontal.TProgressbar',
                        background=self.colors['accent'],
                        troughcolor=self.colors['bg_tertiary'],
                        borderwidth=0)
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(width, height)

    def create_main_page(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        self.geometry("800x600")
        self.minsize(700, 500)
        
        main_frame = ttk.Frame(self, style='Main.TFrame')
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        header_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        header_frame.pack(fill="x", pady=(0, 30))
        
        title_label = ttk.Label(header_frame, text="🎨 RemObj Setup Manager", style='Title.TLabel')
        title_label.pack(pady=(20, 10))
        
        subtitle_label = ttk.Label(header_frame, text="by Akascape | v1.0", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        content_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        content_frame.pack(expand=True, fill="both")
        
        if self.libraries_installed:
            status_frame = ttk.Frame(content_frame, style='Dark.TFrame')
            status_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
            uninstall_btn = tk.Button(status_frame, text="🗑️", justify="right",
                                    bg=self.colors['bg_secondary'],
                                    font=(self.font_family, 10),
                                    fg='white',
                                    activebackground=self.colors['bg_secondary'],
                                    activeforeground='white',
                                    width=4,
                                    bd=0, 
                                    cursor="hand2",
                                    command=self.confirm_uninstall)
            uninstall_btn.place(relx=1.0, y=5, x=-1, anchor="ne")

            success_label = tk.Label(status_frame, text="✅", 
                                     font=(self.font_family, 24),
                                     bg=self.colors['bg_secondary'],
                                     fg=self.colors['text_primary'])
            success_label.pack(pady=(40, 20))
            
            installed_label = ttk.Label(status_frame, text="RemObj libraries are installed!", style='Success.TLabel')
            installed_label.pack(pady=(0, 10))
            
            info_label = ttk.Label(status_frame, text="ONNX Runtime, OpenCV, and Numpy are configured correctly.", style='Subtitle.TLabel')
            info_label.pack(pady=(0, 40))
            
            action_buttons_frame = ttk.Frame(status_frame, style='Dark.TFrame')
            action_buttons_frame.pack(pady=20)

            test_btn = ttk.Button(action_buttons_frame, text="Test RemObj 🧪", command=self.create_test_page, style='Action.TButton')
            test_btn.pack(side="left", padx=5)
        else:
            install_frame = ttk.Frame(content_frame, style='Dark.TFrame')
            install_frame.pack(expand=True, fill="both", padx=20, pady=20)

            header_container = tk.Frame(install_frame, bg=self.colors['bg_secondary'])
            header_container.pack(fill="x", pady=(20, 30), padx=5)
            
            install_icon = tk.Label(header_container, text="⚙️", font=(self.font_family, 20), bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
            install_icon.pack(pady=(0, 10))
            
            install_title = tk.Label(header_container, text="Choose your installation type:", font=(self.font_family, 14, 'bold'), bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
            install_title.pack(pady=(0, 5))
            
            install_subtitle = tk.Label(header_container, text="Select CPU or CUDA support to install onnxruntime, cv2, and numpy", font=(self.font_family, 10), bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'])
            install_subtitle.pack(pady=(0, 10))
            
            options_container = tk.Frame(install_frame, bg=self.colors['bg_secondary'])
            options_container.pack(fill="both", pady=(0, 5), padx=2, expand=True)
            
            self.install_type = tk.StringVar(value="CPU Only")
            options = [
                ("CPU Only", "🔴", "CPU Only", "Installs CPU-only packages. Best for universal compatibility."),
                ("CUDA Support", "🚀", "CUDA Support", "Installs CUDA packages (onnxruntime-gpu) for NVIDIA GPU acceleration.")
            ]
            
            self.option_frames = []
            for i, (value, icon, title, description) in enumerate(options):
                option_card = tk.Frame(options_container, bg=self.colors['bg_tertiary'], relief='solid', bd=1, highlightbackground=self.colors['border'])
                option_card.pack(fill="both", pady=5, padx=10, side="left", expand=True)

                inner_frame = tk.Frame(option_card, bg=self.colors['bg_tertiary'])
                inner_frame.pack(fill="both", expand=True, padx=15, pady=15)
                
                top_row = tk.Frame(inner_frame, bg=self.colors['bg_tertiary'])
                top_row.pack(fill="x", anchor='w')
                
                radio = tk.Radiobutton(top_row, text="", variable=self.install_type, value=value, bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], selectcolor=self.colors['bg_primary'], command=self.update_option_selection)
                radio.pack(side="left", padx=(0, 5))
                
                icon_label = tk.Label(top_row, text=icon, font=(self.font_family, 16), bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'])
                icon_label.pack(side="left", padx=(0, 5))
                
                title_label = tk.Label(top_row, text=title, font=(self.font_family, 10, 'bold'), bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'])
                title_label.pack(side="left")
                
                desc_label = tk.Label(inner_frame, text=description, font=(self.font_family, 8), bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'], wraplength=200, justify='left')
                desc_label.pack(anchor="w", pady=(8, 0))
                
                self.option_frames.append((option_card, value))
                
                def make_clickable(card, val):
                    def on_click(event):
                        self.install_type.set(val)
                        self.update_option_selection()
                    card.bind("<Button-1>", on_click)
                    inner_frame.bind("<Button-1>", on_click)
                    icon_label.bind("<Button-1>", on_click)
                    title_label.bind("<Button-1>", on_click)
                    desc_label.bind("<Button-1>", on_click)
                
                make_clickable(option_card, value)
            
            self.update_option_selection()
            
            action_frame = tk.Frame(install_frame, bg=self.colors['bg_secondary'])
            action_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            self.install_btn = ttk.Button(action_frame, text="📩 Install Required Libraries", command=self.start_install, style='Action.TButton')
            self.install_btn.pack(fill="x", side="bottom")

    def confirm_uninstall(self):
        if messagebox.askyesno("Uninstall Libraries?", "Are you sure you want to uninstall ONNX Runtime, OpenCV, and Numpy?"):
            self.uninstall_libraries()

    def uninstall_libraries(self):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "onnxruntime", "onnxruntime-gpu", "opencv-python", "numpy", "-y"])
            messagebox.showinfo("Uninstall Successful", "Libraries have been successfully uninstalled.\nThe application will now close.")
            self.destroy()
        except Exception as e:
             messagebox.showerror("Error", f"An unexpected error occurred during uninstall: {e}")

    def update_option_selection(self):
        selected_value = self.install_type.get()
        for option_card, value in self.option_frames:
            if value == selected_value:
                option_card.config(bg=self.colors['accent'], highlightbackground=self.colors['accent'])
                self.update_frame_colors(option_card, self.colors['accent'], '#ffffff')
            else:
                option_card.config(bg=self.colors['bg_tertiary'], highlightbackground=self.colors['border'])
                self.update_frame_colors(option_card, self.colors['bg_tertiary'], self.colors['text_primary'])

    def update_frame_colors(self, parent, bg_color, fg_color):
        try:
            for child in parent.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg=bg_color)
                    self.update_frame_colors(child, bg_color, fg_color)
                elif isinstance(child, (tk.Label, tk.Radiobutton)):
                    child.config(bg=bg_color)
                    if isinstance(child, tk.Label):
                        if child.cget('font').split()[0] == self.font_family and int(child.cget('font').split()[1]) == 8:
                            child.config(fg=self.colors['text_secondary'] if bg_color == self.colors['bg_tertiary'] else '#e0e0e0')
                        else:
                            child.config(fg=fg_color)
                    elif isinstance(child, tk.Radiobutton):
                        child.config(fg=fg_color, activebackground=bg_color)
        except (tk.TclError, IndexError):
            pass

    def start_install(self):
        self.is_installing = True
        self.install_btn.config(state="disabled", text="Installing... This might take a few minutes...")
        install_libraries(self.install_type.get(), self.install_callback)

    def install_callback(self, success):
        self.is_installing = False
        self.install_btn.config(state="normal", text="📩 Install Required Libraries")
        if is_library_installed():
            self.libraries_installed = True
            messagebox.showinfo("Success", "Libraries installed successfully! Restarting setup manager...")
            self.create_main_page()
        else:
            messagebox.showerror("Installation Failed", "Could not install required libraries. Check console logs.")

    # --------------------------------------------------------------------
    # TESTING PAGE FOR REMOBJ
    # --------------------------------------------------------------------

    def create_test_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.geometry("1100x700")
        self.minsize(950, 600)

        main_frame = ttk.Frame(self, style='Main.TFrame')
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)
        
        header_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🧪 RemObj Testing Utility", style='Title.TLabel')
        title_label.pack(pady=(20, 5))
        
        subtitle_label = ttk.Label(header_frame, text="Test the LaMa AI model on your image with a mask", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        content_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        content_frame.pack(expand=True, fill="both")
        
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        controls_frame = ttk.Frame(content_frame, style='Dark.TFrame')
        controls_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        self.process_btn = ttk.Button(controls_frame, text="Process Image", command=self.start_image_processing, style='Action.TButton')
        self.process_btn.pack(side="right", padx=(5,0))

        self.save_btn = ttk.Button(controls_frame, text="Save Image...", command=self.save_processed_image, style='Secondary.TButton', state="disabled")
        self.save_btn.pack(side="right")
        
        choose_image_btn = ttk.Button(controls_frame, text="Choose Image...", command=self.select_image_for_test, style='Secondary.TButton')
        choose_image_btn.pack(side="left", padx=(0, 10))

        choose_mask_btn = ttk.Button(controls_frame, text="Choose Mask...", command=self.select_mask_for_test, style='Secondary.TButton')
        choose_mask_btn.pack(side="left", padx=(0, 10))

        # Grid view for Original, Mask, and Result
        image_area_frame = ttk.Frame(content_frame, style='Dark.TFrame')
        image_area_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        image_area_frame.columnconfigure(0, weight=1)
        image_area_frame.columnconfigure(1, weight=1)
        image_area_frame.columnconfigure(2, weight=1)
        image_area_frame.rowconfigure(1, weight=1)

        # Original Image Column
        original_label = ttk.Label(image_area_frame, text="Original Image", style='Subtitle.TLabel')
        original_label.grid(row=0, column=0, pady=(0, 5))
        self.original_canvas = tk.Canvas(image_area_frame, bg=self.colors['bg_primary'], bd=0, highlightthickness=0)
        self.original_canvas.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # Mask Image Column
        mask_label = ttk.Label(image_area_frame, text="Mask", style='Subtitle.TLabel')
        mask_label.grid(row=0, column=1, pady=(0, 5))
        self.mask_canvas = tk.Canvas(image_area_frame, bg=self.colors['bg_primary'], bd=0, highlightthickness=0)
        self.mask_canvas.grid(row=1, column=1, sticky="nsew", padx=(5, 5))

        # Processed Image Column
        processed_label = ttk.Label(image_area_frame, text="Inpainted Output", style='Subtitle.TLabel')
        processed_label.grid(row=0, column=2, pady=(0, 5))
        self.processed_canvas = tk.Canvas(image_area_frame, bg=self.colors['bg_primary'], bd=0, highlightthickness=0)
        self.processed_canvas.grid(row=1, column=2, sticky="nsew", padx=(5, 0))

        button_frame = ttk.Frame(main_frame, style='Dark2.TFrame')
        button_frame.pack(fill="x", pady=10, side="bottom")

        self.back_btn_test = ttk.Button(button_frame, text="← Back", command=self.create_main_page, style='Secondary.TButton')
        self.back_btn_test.pack(side="left")

    def select_image_for_test(self):
        path = filedialog.askopenfilename(
            title="Select an Input Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All files", "*.*")]
        )
        if not path:
            return
        
        self.input_image_path = Path(path)
        
        self.processed_canvas.delete("all")
        self.tk_output_image = None
        self.processed_image_path = None
        self.save_btn.config(state="disabled")

        self.display_image_on_canvas(self.original_canvas, self.input_image_path, "input")

    def select_mask_for_test(self):
        path = filedialog.askopenfilename(
            title="Select the Mask Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All files", "*.*")]
        )
        if not path:
            return
        
        self.input_mask_path = Path(path)
        
        self.processed_canvas.delete("all")
        self.tk_output_image = None
        self.processed_image_path = None
        self.save_btn.config(state="disabled")

        self.display_image_on_canvas(self.mask_canvas, self.input_mask_path, "mask")

    def display_image_on_canvas(self, canvas, image_source, image_type, in_memory=False):
        canvas.delete("all")
        
        self.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1: return

        try:
            image_object = Image.open(image_source) if not in_memory else image_source
            
            with image_object as img:
                img.thumbnail((canvas_width - 10, canvas_height - 10), Image.Resampling.LANCZOS)
                
                if image_type == "input":
                    self.tk_input_image = ImageTk.PhotoImage(img)
                    canvas.create_image(canvas_width / 2, canvas_height / 2, anchor="center", image=self.tk_input_image)
                elif image_type == "mask":
                    self.tk_mask_image = ImageTk.PhotoImage(img)
                    canvas.create_image(canvas_width / 2, canvas_height / 2, anchor="center", image=self.tk_mask_image)
                else:
                    self.tk_output_image = ImageTk.PhotoImage(img)
                    canvas.create_image(canvas_width / 2, canvas_height / 2, anchor="center", image=self.tk_output_image)

        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load or display image: {e}")

    def start_image_processing(self):
        if not self.input_image_path:
            messagebox.showwarning("Input Missing", "Please select an input image first.")
            return
        if not self.input_mask_path:
            messagebox.showwarning("Mask Missing", "Please select a mask image first.")
            return

        self.process_btn.config(state="disabled", text="Processing...")
        self.save_btn.config(state="disabled")
        self.back_btn_test.config(state="disabled")
        
        self.processed_canvas.delete("all")
        self.tk_output_image = None
        self.processed_image_path = None

        threading.Thread(target=self.run_remobj_processing, daemon=True).start()

    def run_remobj_processing(self):
        try:
            current_dir = Path(__file__).parent
            sys.path.append(str(current_dir))
            
            from obj_remover import LaMaInpainter
            
            model_path = current_dir / "lama_sim_fp32.onnx"
            inpainter = LaMaInpainter(str(model_path))
            
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            output_path = temp_dir / "remobj_test_output.png"
            
            success = inpainter.remove(
                str(self.input_image_path),
                str(self.input_mask_path),
                str(output_path)
            )
            
            if success and output_path.exists():
                self.processed_image_path = output_path
                self.after(0, self.processing_finished, True)
            else:
                self.after(0, self.processing_finished, False, "Inpainting processing failed. Check console output logs.")
                
        except Exception as e:
            print(f"Error during RemObj processing: {e}")
            import traceback
            traceback.print_exc()
            self.after(0, self.processing_finished, False, str(e))

    def processing_finished(self, success, error_msg=None):
        self.process_btn.config(state="normal", text="Process Image")
        self.back_btn_test.config(state="normal")

        if success:
            processed_image = Image.open(self.processed_image_path)
            self.display_image_on_canvas(self.processed_canvas, processed_image, "output", in_memory=True)
            self.save_btn.config(state="normal")
        else:
            messagebox.showerror("Processing Failed", f"An error occurred: {error_msg}")

    def save_processed_image(self):
        if not self.processed_image_path or not self.processed_image_path.exists():
            messagebox.showwarning("No Image", "There is no processed image to save.")
            return

        original_path = Path(self.input_image_path)
        default_filename = f"{original_path.stem}_inpainted.png"

        save_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")]
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy(self.processed_image_path, save_path)
                messagebox.showinfo("Success", f"Image saved successfully to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save the image: {e}")

if __name__ == "__main__":
    app = RemObjSetupApp()
    app.focus_force()
    app.mainloop()
