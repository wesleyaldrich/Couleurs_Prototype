import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from deoldify.visualize import get_image_colorizer
import threading
import os
import uuid
import ctypes

os.environ['NUMEXPR_MAX_THREADS'] = '8'

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", message="Your training set is empty")
warnings.filterwarnings("ignore", message="Your validation set is empty")
warnings.filterwarnings("ignore", message="The parameter 'pretrained' is deprecated")
warnings.filterwarnings("ignore", message="Arguments other than a weight enum or `None` for 'weights' are deprecated")
warnings.filterwarnings("ignore", message="torch.nn.utils.weight_norm is deprecated")

# Create colorizer
colorizer = get_image_colorizer(artistic=True)

class CouleursApp:
    def __init__(self, root, colorizer):
        self.root = root
        self.colorizer = colorizer
        self.root.title("Couleurs Simulation")
        self.root.geometry("1600x1000")
        self.root.config(bg="#2b2b2b")

        self.style_font_title = ("Arial", 24, "bold")
        self.style_font_desc = ("Arial", 16)

        # Title
        self.title_label = tk.Label(root, text="Couleurs Simulation", font=self.style_font_title, bg="#2b2b2b", fg="#6495ed")
        self.title_label.pack(pady=(20, 10))

        # Description
        self.description_label = tk.Label(root, text="Upload an image to see it colorized!", font=self.style_font_desc, bg="#2b2b2b", fg="#ffffff")
        self.description_label.pack(pady=10)

        # Frame for images side by side
        self.image_frame = tk.Frame(root, bg="#2b2b2b")
        self.image_frame.pack(pady=(20, 0), padx=50, fill=tk.BOTH, expand=True)

        # Original image label
        self.image_label = tk.Label(self.image_frame, bg="#2b2b2b")
        self.image_label.pack(side=tk.LEFT, padx=10, pady=10, expand=True)

        # Colorized image label
        self.colorized_image_label = tk.Label(self.image_frame, bg="#2b2b2b")
        self.colorized_image_label.pack(side=tk.LEFT, padx=10, pady=10, expand=True)

        # Progress bar
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="indeterminate")
        self.progress_bar.pack(pady=(40, 20), padx=30)

        # Frame for buttons (upload and save)
        self.button_frame = tk.Frame(root, bg="#2b2b2b")
        self.button_frame.pack(pady=10)

        # Upload button
        self.upload_button = tk.Button(self.button_frame, text="Upload", command=self.upload_image,
                                       font=("Arial", 20, "bold"), bg="#6495ed", fg="white",
                                       bd=0, padx=30, pady=15)
        self.upload_button.config(highlightbackground="#6495ed", highlightcolor="#6495ed",
                                  highlightthickness=2, relief="flat")
        self.upload_button.pack(side=tk.LEFT, padx=30)

        # Save button
        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_image,
                                     font=("Arial", 20, "bold"), bg="#32CD32", fg="white",
                                     bd=0, padx=30, pady=15, state=tk.DISABLED)
        self.save_button.config(highlightbackground="#32CD32", highlightcolor="#32CD32",
                                highlightthickness=2, relief="flat")
        self.save_button.pack(side=tk.LEFT, padx=30)

        # Footer label
        self.footer_label = tk.Label(root, text="Couleurs Simulation by PPTI 17 - VI", font=("Arial", 12),
                                     bg="#2b2b2b", fg="#808080")
        self.footer_label.pack(side=tk.BOTTOM, pady=20)

        # Save directory
        self.save_dir = "result_images/"

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            original_image = Image.open(file_path)

            max_width = 600
            max_height = 600

            original_image.thumbnail((max_width, max_height), Image.LANCZOS)
            original_photo = ImageTk.PhotoImage(original_image)

            self.image_label.config(image=original_photo)
            self.image_label.image = original_photo

            threading.Thread(target=self.colorize_image_thread, args=(file_path,)).start()

    def colorize_image_thread(self, file_path):
        # Start the progress bar animation
        self.progress_bar.start()

        # Colorize the image
        colorized_image = self.colorizer.get_transformed_image(
            path=file_path, render_factor=24, watermarked=False
        )

        colorized_image.thumbnail((600, 600), Image.LANCZOS)
        self.colorized_photo = colorized_image  # Store the colorized image

        # Update GUI in the main thread
        self.root.after(1500, lambda: self.update_colorized_image())

    def update_colorized_image(self):
        colorized_photo = ImageTk.PhotoImage(self.colorized_photo)
        self.colorized_image_label.config(image=colorized_photo)
        self.colorized_image_label.image = colorized_photo
        print("Colorized image displayed successfully.")
        
        # Enable the save button after an image is colorized
        self.save_button.config(state=tk.NORMAL)

        # Stop the progress bar animation
        self.progress_bar.stop()

    def save_image(self):
        if hasattr(self, 'colorized_photo'):
            # Generate a unique file name using uuid
            file_name = str(uuid.uuid4()) + ".png"
            file_path = os.path.join(self.save_dir, file_name)

            try:
                # Save the colorized image
                self.colorized_photo.save(file_path)
                print(f"Colorized image saved successfully at {file_path}")
            except Exception as e:
                print(f"Error saving image: {e}")
        else:
            print("No colorized image available to save.")

if __name__ == "__main__":
    # fix Windows scaling issues
    if os.name == 'nt':
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        
    root = tk.Tk()
    colorizer = get_image_colorizer(artistic=True)
    app = CouleursApp(root, colorizer)
    root.mainloop()
