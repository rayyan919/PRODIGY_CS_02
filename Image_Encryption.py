import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
import os
import numpy as np
import threading

class ImageProcessorApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Processor")
        self.geometry("1980x900")
        
        self.label = tk.Label(self, text="Drag and drop an image file or click 'Browse' to upload from file explorer.", font='ComicSansMS')
        self.label.place(relx=0.5, rely=0.1, anchor="center")
        
        self.browse_button = tk.Button(self, text="Browse", command=self.browse_file, bg='#2971e6', fg='white', font='Helvetica')
        self.browse_button.place(relx=0.5, rely=0.2, anchor="center")
        
        self.encrypt_button = tk.Button(self, text="Encrypt", command=lambda: self.start_processing(encrypt=True), bg='#37804a', fg='white', font='Helvetica')
        self.encrypt_button.place(relx=0.3, rely=0.6, anchor='center')
        
        self.decrypt_button = tk.Button(self, text="Decrypt", command=lambda: self.start_processing(encrypt=False), bg='#611a26', fg='white', font='Helvetica')
        self.decrypt_button.place(relx=0.7, rely=0.6, anchor='center')
        
        self.download_button = tk.Button(self, text="Download Processed Image", command=self.save_image, bg='#0cfa4c', fg='white', font='Helvetica')
        self.download_button.place(relx=0.5, rely=0.8, anchor='center')
        self.download_button.config(state=tk.DISABLED)
        
        self.processed_image = None
        self.original_image = None
        
        self.register_drop_target()
        
    def register_drop_target(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop)
        
    def drop(self, event):
        file_path = event.data
        self.load_image(file_path.strip('{}'))
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if file_path:
            self.load_image(file_path)
            
    def load_image(self, file_path):
        try:
            self.original_image = Image.open(file_path)
            self.label.config(text="Image loaded successfully!")
            self.download_button.config(state=tk.DISABLED)
        except Exception as e:
            self.label.config(text=f"Error loading image: {e}")
            self.download_button.config(state=tk.DISABLED)
    
    def start_processing(self, encrypt=True):
        if self.original_image is None:
            messagebox.showerror("Error", "No image loaded to process.")
            return
        self.label.config(text="Processing image, please wait...")
        threading.Thread(target=self.process_image, args=(encrypt,)).start()
    
    def process_image(self, encrypt=True):
        try:
            self.processed_image = self.encrypt_decrypt_image(self.original_image, encrypt)
            self.label.config(text="Image processed successfully!")
            self.download_button.config(state=tk.NORMAL)
        except Exception as e:
            self.label.config(text=f"Error processing image: {e}")
            self.download_button.config(state=tk.DISABLED)
    
    def encrypt_decrypt_image(self, image, encrypt=True):
        pixel_matrix = np.array(image)
        
        shift = 5 if encrypt else -5
        
        # Flatten the image array for operations
        flat_pixels = pixel_matrix.flatten()
        
        # Invert pixels if encrypting
        if encrypt:
            processed_flat_pixels = (flat_pixels + shift) % 256
            processed_flat_pixels = 255 - processed_flat_pixels
        else:
            flat_pixels = 255 - flat_pixels
            processed_flat_pixels = (flat_pixels + shift) % 256
        
        # Perform pixel swaps in pairs
        for i in range(0, len(processed_flat_pixels) - 1, 2):
            processed_flat_pixels[i], processed_flat_pixels[i + 1] = processed_flat_pixels[i + 1], processed_flat_pixels[i]
        
        # Reshape the processed flat pixels back to the original shape
        processed_pixels = processed_flat_pixels.reshape(pixel_matrix.shape)
        
        processed_image = Image.fromarray(processed_pixels.astype('uint8'))
        return processed_image
    
    def save_image(self):
        if self.processed_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), 
                                                                ("JPEG files", "*.jpg"), 
                                                                ("BMP files", "*.bmp"), 
                                                                ("GIF files", "*.gif")],
                                                     title="Save processed image")
            if file_path:
                try:
                    self.processed_image.save(file_path)
                    messagebox.showinfo("Success", f"Image saved successfully as {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error saving image: {e}")
            else:
                self.label.config(text="Save cancelled.")
        else:
            messagebox.showerror("Error", "No processed image to save.")
            
if __name__ == "__main__":
    app = ImageProcessorApp()
    app.mainloop()


