from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence, ImageEnhance
from geopy.geocoders import Nominatim
from tkinter import messagebox
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
import threading

# Constants
API_KEY = "8c5a9876cd1a3a4459232911a0465a06"  # Replace with your actual API key
GEOCODE_TIMEOUT = 10
API_TIMEOUT = 10

# Function to get weather information
def get_weather():
    city = textfield.get().strip()
    if not city:
        messagebox.showerror("Error", "Please enter a city name")
        return
    
    # Show loading icon
    show_loading()

    def fetch_data():
        location = get_location(city)
        if location is None:
            hide_loading()
            return

        current_time = get_local_time(location)
        clock.config(text=current_time)
        name.config(text="CURRENT WEATHER")

        weather_data = fetch_weather_data(location)
        if weather_data:
            update_weather_info(weather_data)
        
        # Hide loading icon
        hide_loading()

    # Fetch data in a separate thread to keep the UI responsive
    threading.Thread(target=fetch_data).start()

# Function to get location details
def get_location(city):
    geolocator = Nominatim(user_agent="weather_app")
    try:
        location = geolocator.geocode(city, timeout=GEOCODE_TIMEOUT)
        if location is None:
            raise ValueError("City not found")
        return location
    except Exception as e:
        messagebox.showerror("Error", f"Geocoding error: {e}")
        return None

# Function to get local time
def get_local_time(location):
    obj = TimezoneFinder()
    result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
    home = pytz.timezone(result)
    local_time = datetime.now(home)
    return local_time.strftime("%I:%M %p")

# Function to fetch weather data
def fetch_weather_data(location):
    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={location.latitude}&lon={location.longitude}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(api_url, timeout=API_TIMEOUT)
        response.raise_for_status()
        json_data = response.json()
        if 'weather' not in json_data:
            raise ValueError("Weather data not available")
        return json_data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Weather API error: {e}")
    except ValueError as e:
        messagebox.showerror("Error", f"Weather data error: {e}")
    return None

# Function to update weather information in the UI
def update_weather_info(data):
    condition = data['weather'][0]['main']
    description = data['weather'][0]['description']
    temp = int(data['main']['temp'])
    pressure = data['main']['pressure']
    humidity = data['main']['humidity']
    wind = data['wind']['speed']

    t.config(text=f"{temp} °C")
    c.config(text=f"{condition} | FEELS LIKE {temp} °C")
    w.config(text=f"{wind} m/s")
    h.config(text=f"{humidity}%")
    d.config(text=description)
    p.config(text=f"{pressure} hPa")

# Functions to show and hide loading icon
def show_loading():
    # Calculate center position for the loading icon
    loading_width = frames[0].width()
    loading_height = frames[0].height()
    x = (root.winfo_width() // 2) - (loading_width // 2)
    y = (root.winfo_height() // 2) - (loading_height // 2)
    loading_label.place(x=x, y=y)
    animate_loading()

def hide_loading():
    loading_label.place_forget()

def animate_loading(counter=0):
    frame = frames[counter % len(frames)]
    loading_label.configure(image=frame)
    root.after(50, animate_loading, counter + 1)

# Tkinter setup
root = Tk()
root.title("Weather App")
root.geometry("800x500+300+200")
root.resizable(False, False)

# Load images
def load_image(image_path, width, height):
    original_image = Image.open(image_path)
    resized_image = original_image.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(resized_image)

Search_image = PhotoImage(file="search.png")
search_icon = PhotoImage(file="search_icon.png")
logo_image = load_image("logoicon.png", 244, 232)
frame_image = PhotoImage(file="box.png")

# Load the loading GIF with transparency
loading_gif = Image.open("spin.gif")
# Enhance alpha channel to ensure transparency
frames = []
for frame in ImageSequence.Iterator(loading_gif):
    frame = frame.convert("RGBA")
    r, g, b, a = frame.split()
    a = ImageEnhance.Brightness(a).enhance(0.5)
    frame = Image.merge("RGBA", (r, g, b, a))
    frames.append(ImageTk.PhotoImage(frame))

# UI Elements
Label(root, image=Search_image).place(x=20, y=20)
textfield = tk.Entry(root, justify="center", width=17, font=("poppins", 25, "bold"), bg="#404040", border=0, fg="white")
textfield.place(x=50, y=35, width=280, height=50)
Button(root, image=search_icon, borderwidth=0, cursor="hand2", bg="#404040", command=get_weather).place(x=410, y=35, width=50, height=50)
Label(root, image=logo_image).place(x=150, y=110)
Label(root, image=frame_image).place(x=9, y=350)

name = Label(root, font=("arial", 15, "bold"))
name.place(x=30, y=100)
clock = Label(root, font=("Helvetica", 20))
clock.place(x=30, y=130)

Label(root, text="WIND", font=("Helvetica", 15, 'bold'), fg="white", bg="#1ab5ef").place(x=70, y=375)
Label(root, text="HUMIDITY", font=("Helvetica", 15, 'bold'), fg="white", bg="#1ab5ef").place(x=210, y=375)
Label(root, text="DESCRIPTION", font=("Helvetica", 15, 'bold'), fg="white", bg="#1ab5ef").place(x=380, y=375)
Label(root, text="PRESSURE", font=("Helvetica", 15, 'bold'), fg="white", bg="#1ab5ef").place(x=600, y=375)

t = Label(font=("arial", 50, "bold"), fg="#ee666d")
t.place(x=400, y=150)
c = Label(font=("arial", 20, "bold"))
c.place(x=400, y=250)

w = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
w.place(x=80, y=400)
h = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
h.place(x=240, y=400)
d = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
d.place(x=400, y=400)
p = Label(text="...", font=("arial", 20, "bold"), bg="#1ab5ef")
p.place(x=610, y=400)

# Loading icon
loading_label = Label(root)
loading_label.place_forget()

root.mainloop()
