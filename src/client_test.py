import tkinter as tk
import math

class CircleApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Circle App")

        self.canvas = tk.Canvas(self.master, width=400, height=400, bg="white")
        self.canvas.pack()

        self.radius = 150
        self.center_x = 200
        self.center_y = 200

        # Draw the bounding box (circle)
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline="black"
        )

        # Draw lines from center to each corner (you can remove these as needed)
        self.canvas.create_line(self.center_x, self.center_y, self.center_x - self.radius, self.center_y - self.radius, fill="black")
        self.canvas.create_line(self.center_x, self.center_y, self.center_x + self.radius, self.center_y - self.radius, fill="black")
        self.canvas.create_line(self.center_x, self.center_y, self.center_x - self.radius, self.center_y + self.radius, fill="black")
        self.canvas.create_line(self.center_x, self.center_y, self.center_x + self.radius, self.center_y + self.radius, fill="black")

        # Draw the coordinate system inside the circle
        self.canvas.create_line(self.center_x, self.center_y - self.radius, self.center_x, self.center_y + self.radius, fill="black")  # Vertical line (Y-axis)
        self.canvas.create_line(self.center_x - self.radius, self.center_y, self.center_x + self.radius, self.center_y, fill="black")  # Horizontal line (X-axis)

        # Draw markers for reference (you can remove these as needed)
        # Middle marker
        self.draw_marker(self.center_x, self.center_y, "Middle")

        # Corner markers
        self.draw_marker(self.center_x - self.radius, self.center_y - self.radius, "Top Left")
        self.draw_marker(self.center_x + self.radius, self.center_y - self.radius, "Top Right")
        self.draw_marker(self.center_x - self.radius, self.center_y + self.radius, "Bottom Left")
        self.draw_marker(self.center_x + self.radius, self.center_y + self.radius, "Bottom Right")

        # Side markers
        self.draw_marker(self.center_x, self.center_y - self.radius, "Top")
        self.draw_marker(self.center_x, self.center_y + self.radius, "Bottom")
        self.draw_marker(self.center_x - self.radius, self.center_y, "Left")
        self.draw_marker(self.center_x + self.radius, self.center_y, "Right")

        # Draw the marker
        self.marker_size = 10
        self.marker = self.canvas.create_oval(
            self.center_x - self.marker_size // 2,
            self.center_y - self.marker_size // 2,
            self.center_x + self.marker_size // 2,
            self.center_y + self.marker_size // 2,
            fill="red"
        )

        # Bind mouse events
        self.canvas.bind("<B1-Motion>", self.move_marker)

    def draw_marker(self, x, y, label):
        # Draw a marker at the specified position with a label
        marker_size = 5
        self.canvas.create_oval(
            x - marker_size,
            y - marker_size,
            x + marker_size,
            y + marker_size,
            fill="blue"
        )
        self.canvas.create_text(x, y - marker_size - 10, text=label, fill="blue")

    def move_marker(self, event):
        # Calculate the new position based on mouse coordinates
        new_x = event.x
        new_y = event.y

        # Calculate the angle and distance even when clicked outside the circle
        angle = math.atan2(new_y - self.center_y, new_x - self.center_x)
        distance = min(self.radius, math.sqrt((new_x - self.center_x)**2 + (new_y - self.center_y)**2))

        # Calculate new coordinates
        new_x = self.center_x + distance * math.cos(angle)
        new_y = self.center_y + distance * math.sin(angle)

        # Update the marker position
        self.canvas.coords(
            self.marker,
            new_x - self.marker_size // 2,
            new_y - self.marker_size // 2,
            new_x + self.marker_size // 2,
            new_y + self.marker_size // 2
        )

        # Print the polar coordinates
        polar_radius = math.sqrt((new_x - self.center_x)**2 + (new_y - self.center_y)**2)
        polar_angle = math.degrees(math.atan2(new_y - self.center_y, new_x - self.center_x))
        print(f"Marker position: ({polar_radius:.2f}, {polar_angle:.2f} degrees)")

if __name__ == "__main__":
    root = tk.Tk()
    app = CircleApp(root)
    root.mainloop()
