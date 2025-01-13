import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import math
from typing import List, Tuple


class VideoBrushApp:
    def __init__(self, root):
        # Brush properties
        self.frames: List[Image] = []
        self.current_frame_index = 0
        self.previous_position: Tuple[int, int] = None
        self.actions: List[Tuple[Image, int, int, int]] = []
        self.drawing_mode = False  # Track whether drawing is active
        self.frame_spacing_at_load = 1

        self.root = root
        self.root.title("2024")

        # Remove extra window padding and border
        width = 1500
        height = 500
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg="white")  # Set background to white
        self.root.overrideredirect(False)  # Set to True if you want to remove the title bar

        # Canvas for drawing
        self.canvas = tk.Canvas(
            root,
            bg="white",
            width=width,
            height=height,
            highlightthickness=0  # Remove the gray border around the canvas
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.canvas.bind("<Motion>", self.paint)

        self.root.bind("d", self.toggle_drawing_mode)

        # Open controls window
        self.open_controls_window()

    def toggle_drawing_mode(self, event=None):
        """Toggle drawing mode."""
        self.drawing_mode = not self.drawing_mode
        if self.drawing_mode:
            print("Drawing mode enabled.")
        else:
            print("Drawing mode disabled.")
            self.previous_position = None  # Reset previous position when toggling off

    def open_controls_window(self):
        """Create a separate window for controls."""
        self.controls_window = tk.Toplevel(self.root)
        self.controls_window.title("Controls")
        self.controls_window.geometry("300x400")

        self.video_button = tk.Button(self.controls_window, text="Choose Video", command=self.choose_videos)
        self.video_button.pack(fill=tk.X, padx=5, pady=5)

        self.clear_button = tk.Button(self.controls_window, text="Clear", command=self.clear_canvas)
        self.clear_button.pack(fill=tk.X, padx=5, pady=5)

        self.export_button = tk.Button(self.controls_window, text="Export", command=self.export_canvas)
        self.export_button.pack(fill=tk.X, padx=5, pady=5)

        self.frame_spacing_at_load_label = tk.Label(self.controls_window, text="Frame Spacing at Load:")
        self.frame_spacing_at_load_fn = tk.Scale(self.controls_window, from_=1, to=50, orient=tk.HORIZONTAL, command=self.set_frame_spacing_at_load)
        self.frame_spacing_at_load_label.pack(fill=tk.X, padx=5, pady=5)
        self.frame_spacing_at_load_fn.pack(fill=tk.X, padx=5, pady=5)

        self.brush_size_label = tk.Label(self.controls_window, text="Brush Size:")
        self.brush_size_fn = tk.Entry(self.controls_window)
        self.brush_size_fn.insert(0, "100")
        self.brush_size_label.pack(fill=tk.X, padx=5, pady=5)
        self.brush_size_fn.pack(fill=tk.X, padx=5, pady=5)

        self.min_spacing_label = tk.Label(self.controls_window, text="Min Spacing:")
        self.min_spacing_fn = tk.Entry(self.controls_window)
        self.min_spacing_fn.insert(0, "1")
        self.min_spacing_label.pack(fill=tk.X, padx=5, pady=5)
        self.min_spacing_fn.pack(fill=tk.X, padx=5, pady=5)

        self.frame_spacing_label = tk.Label(self.controls_window, text="Frame Spacing:")
        self.frame_spacing_fn = tk.Entry(self.controls_window)
        self.frame_spacing_fn.insert(0, "1")
        self.frame_spacing_label.pack(fill=tk.X, padx=5, pady=5)
        self.frame_spacing_fn.pack(fill=tk.X, padx=5, pady=5)

        self.saturate_label = tk.Label(self.controls_window, text="Saturate:")
        self.saturate_fn = tk.Entry(self.controls_window)
        self.saturate_fn.insert(0, "1")
        self.saturate_label.pack(fill=tk.X, padx=5, pady=5)
        self.saturate_fn.pack(fill=tk.X, padx=5, pady=5)

        # Close the app when the controls window is closed
        self.controls_window.protocol("WM_DELETE_WINDOW", self.on_controls_window_close)

    def on_controls_window_close(self):
        """Handle closing the controls window."""
        self.controls_window.destroy()
        self.root.destroy()

    def choose_videos(self):
        """Open a file dialog to choose multiple videos."""
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.load_videos_frames(file_paths)

    def load_videos_frames(self, video_path: List[str]):
        """Load video frames from a video file."""
        self.frames.clear()
        for path in video_path:
            cap = cv2.VideoCapture(path)
            count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if count % self.frame_spacing_at_load == 0:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.frames.append(frame)
                count += 1
            cap.release()
        print(f"Loaded {len(self.frames)} frames.")
            
    def set_frame_spacing_at_load(self, event):
        self.frame_spacing_at_load = int(self.frame_spacing_at_load_fn.get())

    def get_brush_size(self):
        return int(self.brush_size_fn.get())

    def get_min_spacing(self):
        return int(self.min_spacing_fn.get())

    def get_frame_spacing(self):
        return int(self.frame_spacing_fn.get())

    def get_saturate(self):
        return float(self.saturate_fn.get())

    def paint(self, event):
        if not self.drawing_mode:
            return
        
        if len(self.frames) == 0:
            print("No frames loaded.")
            return

        if self.previous_position is None:
            self.previous_position = (event.x, event.y)

        prev_x, prev_y = self.previous_position
        distance = math.sqrt((event.x - prev_x) ** 2 + (event.y - prev_y) ** 2)

        if distance < self.get_min_spacing():
            return

        self.current_frame_index += self.get_frame_spacing()
        self.current_frame_index %= len(self.frames)
        frame = self.frames[self.current_frame_index]

        brush_size = self.get_brush_size()
        aspect_ratio = frame.shape[1] / frame.shape[0]
        width = brush_size * 2
        height = int(width / aspect_ratio)
        frame = cv2.resize(frame, (width, height))


        saturate = self.get_saturate()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        frame[:, :, 1] = frame[:, :, 1] * saturate
        frame = cv2.cvtColor(frame, cv2.COLOR_HSV2RGB)

        image = Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=image)

        x = event.x - brush_size
        y = event.y - brush_size
        self.canvas.create_image(x, y, anchor=tk.NW, image=img)
        self.actions.append((frame, x, y, brush_size))

        if not hasattr(self, "image_refs"):
            self.image_refs = []
        self.image_refs.append(img)

        self.previous_position = (event.x, event.y)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.actions.clear()

    def export_canvas(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")]
        )
        if file_path:
            print(f"Exporting canvas to {file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoBrushApp(root)
    root.mainloop()