import phonenumbers
from phonenumbers import timezone, geocoder, carrier
import folium
from opencage.geocoder import OpenCageGeocode
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from PIL import Image, ImageTk
import os
import time
import requests
from io import BytesIO
import sv_ttk  # Modern theme

class SecurePhoneLocatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 EDUCATIONAL Phone Locator")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)
        
        # Legal disclaimer configuration
        self.disclaimer_shown = False
        self.show_disclaimer()
        
        # Custom colors
        self.bg_color = "#1e1e2e"
        self.card_color = "#2a2a3a"
        self.accent_color = "#6c5ce7"
        self.text_color = "#ffffff"
        self.secondary_color = "#4a4a5a"
        self.warning_color = "#ff6b6b"
        
        # API Key
        self.key = "74617eed02624a779cb4e75f54f67288"
        self.map_file = "Location.html"
        
        # Configure styles
        self.setup_styles()
        
        # Setup UI
        self.create_widgets()
        
        # Apply modern theme
        sv_ttk.set_theme("dark")
        
    def show_disclaimer(self):
        disclaimer_text = """
        LEGAL DISCLAIMER & USE AGREEMENT
        
        THIS APPLICATION IS FOR EDUCATIONAL PURPOSES ONLY.
        
        By using this tool, you AGREE TO:
        1. Only test with phone numbers you own or have explicit permission to track
        2. Never use this to locate others without their consent
        3. Comply with all privacy laws in your jurisdiction
        4. Accept full legal responsibility for any misuse
        
        UNAUTHORIZED USE MAY RESULT IN:
        - Criminal prosecution under privacy laws
        - Civil lawsuits for invasion of privacy
        - Permanent banning from this application
        
        [ACCEPT] to continue | [EXIT] to decline
        """
        
        if not self.disclaimer_shown:
            accept = messagebox.askokcancel(
                "LEGAL AGREEMENT REQUIRED", 
                disclaimer_text,
                icon='warning'
            )
            if not accept:
                self.root.destroy()
                exit()
            self.disclaimer_shown = True
            
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure colors
        self.root.configure(bg=self.bg_color)
        
        # Custom font
        self.title_font = ("Segoe UI", 16, "bold")
        self.text_font = ("Segoe UI", 10)
        self.button_font = ("Segoe UI", 10, "bold")
        
        # Configure ttk widgets
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=self.text_font)
        style.configure('TButton', font=self.button_font, padding=6)
        style.configure('TEntry', font=self.text_font, padding=5)
        style.configure('TLabelFrame', background=self.bg_color, foreground=self.accent_color, font=self.title_font)
        style.configure('Warning.TFrame', background='#2a1e1e')
        style.configure('Warning.TLabel', background='#2a1e1e', foreground=self.warning_color)
        
        # Custom card style
        style.configure('Card.TFrame', background=self.card_color, borderwidth=2, relief='solid', bordercolor=self.secondary_color)
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Warning banner
        warning_frame = ttk.Frame(main_frame, style='Warning.TFrame')
        ttk.Label(
            warning_frame, 
            text="⚠️ EDUCATIONAL USE ONLY - TEST ONLY WITH YOUR OWN NUMBER",
            style='Warning.TLabel',
            font=("Segoe UI", 10, "bold")
        ).pack(pady=5)
        warning_frame.pack(fill=tk.X, pady=(0,20))
        
        # Input card
        input_card = ttk.Frame(main_frame, style='Card.TFrame')
        input_card.pack(fill=tk.X, pady=(0, 20), ipadx=10, ipady=10)
        
        ttk.Label(input_card, text="ENTER YOUR TEST NUMBER", font=self.title_font).pack(anchor=tk.W, pady=(0, 10))
        
        input_row = ttk.Frame(input_card)
        input_row.pack(fill=tk.X)
        
        self.phone_number = tk.StringVar()
        phone_entry = ttk.Entry(input_row, textvariable=self.phone_number, width=30, font=("Segoe UI", 12))
        phone_entry.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        phone_entry.focus()
        
        locate_btn = ttk.Button(input_row, text="📍 LOCATE", command=self.validate_and_locate, style='Accent.TButton')
        locate_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(input_row, text="🔄 CLEAR", command=self.clear_fields)
        clear_btn.pack(side=tk.LEFT)
        
        # Results and Map container
        results_map_container = ttk.Frame(main_frame)
        results_map_container.pack(fill=tk.BOTH, expand=True)
        
        # Results card
        results_card = ttk.Frame(results_map_container, style='Card.TFrame')
        results_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), ipadx=10, ipady=10)
        
        ttk.Label(results_card, text="LOCATION DETAILS", font=self.title_font).pack(anchor=tk.W, pady=(0, 10))
        
        self.result_text = scrolledtext.ScrolledText(
            results_card,
            height=10,
            wrap=tk.WORD,
            bg=self.card_color,
            fg=self.text_color,
            font=self.text_font,
            insertbackground=self.text_color,
            selectbackground=self.accent_color,
            borderwidth=0,
            highlightthickness=0
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Map card
        map_card = ttk.Frame(results_map_container, style='Card.TFrame')
        map_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, ipadx=10, ipady=10)
        
        ttk.Label(map_card, text="LOCATION MAP", font=self.title_font).pack(anchor=tk.W, pady=(0, 10))
        
        self.map_canvas = tk.Canvas(map_card, bg=self.card_color, highlightthickness=0)
        self.map_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.map_placeholder = self.map_canvas.create_text(150, 100, text="Map will appear here", 
                                                         fill=self.text_color, font=("Segoe UI", 12))
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="🌐 OPEN IN BROWSER", command=self.open_map_in_browser).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 SAVE MAP", command=self.save_map_as).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📤 EXPORT RESULTS", command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Legal footer
        ttk.Label(
            main_frame,
            text="By using this tool, you confirm you're testing with your own number for educational purposes",
            style='TLabel',
            font=("Segoe UI", 8)
        ).pack(side=tk.BOTTOM, pady=10)
        
    def validate_and_locate(self):
        number = self.phone_number.get().strip()
        
        if not number:
            messagebox.showerror("Error", "Please enter a phone number", parent=self.root)
            return
            
        if not self.confirm_ownership(number):
            return
            
        self.locate_number(number)
        
    def confirm_ownership(self, number):
        confirmation = f"You are about to locate: {number}\n\n" \
                      "You must confirm this is YOUR OWN number\n" \
                      "for educational testing purposes only."
        
        return messagebox.askyesno(
            "Ownership Verification",
            confirmation,
            icon='question',
            parent=self.root
        )
        
    def locate_number(self, number):
        try:
            # Clear previous results
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "🔄 Processing your number...\n")
            self.root.update()
            
            # Parse phone number
            phoneNumber = phonenumbers.parse(number)
            
            # Get timezone
            timeZone = timezone.time_zones_for_number(phoneNumber)
            self.result_text.insert(tk.END, f"⏰ Timezone: {timeZone}\n")
            
            # Get location
            geolocation = geocoder.description_for_number(phoneNumber, "en")
            self.result_text.insert(tk.END, f"📍 Location: {geolocation}\n")
            
            # Get service provider
            service = carrier.name_for_number(phoneNumber, "en")
            self.result_text.insert(tk.END, f"📱 Service Provider: {service}\n")
            
            # Get coordinates
            geocoder_api = OpenCageGeocode(self.key)
            query = str(geolocation)
            results = geocoder_api.geocode(query)
            
            if results and len(results):
                lat = results[0]['geometry']['lat']
                lng = results[0]['geometry']['lng']
                self.result_text.insert(tk.END, f"🌍 Coordinates: Latitude {lat}, Longitude {lng}\n\n")
                
                # Add legal notice to results
                self.result_text.insert(tk.END, 
                    "LEGAL NOTICE:\n"
                    "This information is for your educational use only.\n"
                    "Unauthorized tracking of others is prohibited by law.\n"
                    f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # Create map
                myMap = folium.Map(location=[lat, lng], zoom_start=9, tiles="cartodbpositron")
                folium.Marker(
                    [lat, lng], 
                    popup=f"Your Test Location: {geolocation}",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(myMap)
                myMap.save(self.map_file)
                
                # Display static map preview
                self.display_static_map(lat, lng)
            else:
                self.result_text.insert(tk.END, "❌ Could not get coordinates for this location\n")
                
            self.result_text.config(state='disabled')
                
        except phonenumbers.phonenumberutil.NumberParseException as e:
            messagebox.showerror("Error", f"Invalid phone number format: {str(e)}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}", parent=self.root)
    
    def display_static_map(self, lat, lng):
        try:
            # Using Mapbox Static API
            access_token = "pk.eyJ1IjoibHdhbmRvLW4iLCJhIjoiY205Z3d0ZTF3MWF2azJxcjdjY3pubTN3dSJ9.ieyhTgCFG1kwM31Yg7rs7g"  # Replace with your token
            style_id = "streets-v11"
            width, height = 400, 300
            
            url = f"https://api.mapbox.com/styles/v1/mapbox/{style_id}/static/pin-s+ff0000({lng},{lat})/{lng},{lat},10/{width}x{height}?access_token={access_token}"
            
            response = requests.get(url)
            img_data = response.content
            
            img = Image.open(BytesIO(img_data))
            img = img.resize((width, height), Image.LANCZOS)
            self.map_photo = ImageTk.PhotoImage(img)
            
            # Clear previous map
            self.map_canvas.delete("all")
            self.map_canvas.create_image(width//2, height//2, image=self.map_photo)
            
        except Exception as e:
            self.map_canvas.delete("all")
            self.map_canvas.create_text(150, 100, text=f"Map preview error: {str(e)}", 
                                      fill="red", font=("Segoe UI", 10))
    
    def open_map_in_browser(self):
        if os.path.exists(self.map_file):
            webbrowser.open_new_tab(f"file://{os.path.abspath(self.map_file)}")
        else:
            messagebox.showwarning("Warning", "No map file found. Please locate a number first.", parent=self.root)
    
    def save_map_as(self):
        if os.path.exists(self.map_file):
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
                initialfile="my_educational_test_location.html",
                parent=self.root
            )
            if file_path:
                try:
                    with open(self.map_file, 'r') as src, open(file_path, 'w') as dst:
                        dst.write(src.read())
                    messagebox.showinfo("Success", f"Map saved successfully to {file_path}", parent=self.root)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save map: {str(e)}", parent=self.root)
        else:
            messagebox.showwarning("Warning", "No map file found. Please locate a number first.", parent=self.root)
    
    def export_results(self):
        content = self.result_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Warning", "No results to export", parent=self.root)
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=f"my_educational_test_{time.strftime('%Y%m%d_%H%M%S')}",
            parent=self.root
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Results exported successfully to {file_path}", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}", parent=self.root)
    
    def clear_fields(self):
        self.phone_number.set("")
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state='disabled')
        self.map_canvas.delete("all")
        self.map_canvas.create_text(150, 100, text="Map will appear here", 
                                  fill=self.text_color, font=("Segoe UI", 12))

if __name__ == "__main__":
    root = tk.Tk()
    app = SecurePhoneLocatorApp(root)
    root.mainloop()