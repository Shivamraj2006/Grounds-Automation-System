import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
from tkinter import scrolledtext

class Ground:
    def __init__(self, name, capacity, sports, location, facilities=None, dimensions=None):
        self.name = name
        self.capacity = capacity
        self.sports = sports
        self.location = location
        self.facilities = facilities or []
        self.dimensions = dimensions or {}
        self.bookings = []  # List of {'date': date, 'time_slot': slot, 'event': event, 'organizer': organizer}

class GroundsAutomationSystem:
    def __init__(self):
        self.grounds = []
        self.time_slots = ["Morning (6AM-10AM)", "Afternoon (10AM-2PM)", 
                           "Evening (2PM-6PM)", "Night (6PM-10PM)"]
        self.load_data()

    def load_data(self):
        sample_grounds = [
            Ground("Central Park", 1000, ["Football", "Cricket"], "Downtown"),
            Ground("Sports Complex", 500, ["Basketball", "Volleyball"], "Uptown"),
            Ground("Community Field", 300, ["Football", "Athletics"], "Suburbs"),
            Ground("Olympic Arena", 2000, ["Athletics", "Football", "Rugby"], "City Center"),
            Ground("Tennis Club", 200, ["Tennis"], "West End")
        ]
        self.grounds.extend(sample_grounds)

    def get_all_grounds(self):
        return self.grounds

    def search_available_grounds(self, date, sport, capacity_required):
        available_grounds = []
        for ground in self.grounds:
            if (sport.lower() in [s.lower() for s in ground.sports] and
                ground.capacity >= capacity_required):
                available_slots = self.get_available_time_slots(ground, date)
                if available_slots:
                    ground.available_slots = available_slots
                    available_grounds.append(ground)

        return self._sort_grounds_by_capacity(available_grounds)

    def get_available_time_slots(self, ground, date):
        booked_slots = [booking['time_slot'] for booking in ground.bookings if booking['date'] == date]
        return [slot for slot in self.time_slots if slot not in booked_slots]

    def get_booking_history(self, ground=None):
        if ground:
            return sorted(ground.bookings, key=lambda x: x['date'], reverse=True)
        
        all_bookings = []
        for ground in self.grounds:
            for booking in ground.bookings:
                booking_info = booking.copy()
                booking_info['ground_name'] = ground.name
                all_bookings.append(booking_info)
        
        return sorted(all_bookings, key=lambda x: x['date'], reverse=True)

    def _sort_grounds_by_capacity(self, grounds):
        if len(grounds) <= 1:
            return grounds
        
        mid = len(grounds) // 2
        left = self._sort_grounds_by_capacity(grounds[:mid])
        right = self._sort_grounds_by_capacity(grounds[mid:])
        
        return self._merge(left, right)

    def _merge(self, left, right):
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i].capacity <= right[j].capacity:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def book_ground(self, ground, date, time_slot, event, organizer):
        if time_slot in self.get_available_time_slots(ground, date):
            ground.bookings.append({
                'date': date,
                'time_slot': time_slot,
                'event': event,
                'organizer': organizer
            })
            return True
        return False

class GroundsAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Grounds Automation System")
        self.system = GroundsAutomationSystem()
        self.setup_gui()

    def setup_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)

        # Create tabs
        self.search_tab = ttk.Frame(self.notebook)
        self.all_grounds_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.manage_grounds_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.search_tab, text="Search & Book")
        self.notebook.add(self.all_grounds_tab, text="All Grounds")
        self.notebook.add(self.history_tab, text="Booking History")
        self.notebook.add(self.manage_grounds_tab, text="Manage Grounds")

        self.setup_search_tab()
        self.setup_all_grounds_tab()
        self.setup_history_tab()
        self.setup_manage_grounds_tab()

    def setup_search_tab(self):
        # Search Frame
        search_frame = ttk.LabelFrame(self.search_tab, text="Search Grounds", padding="10")
        search_frame.pack(fill="x", padx=10, pady=5)

        # Date Selection
        ttk.Label(search_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(search_frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Sport Selection
        ttk.Label(search_frame, text="Sport:").grid(row=1, column=0, padx=5, pady=5)
        self.sport_var = tk.StringVar()
        sports = list(set([sport for ground in self.system.grounds for sport in ground.sports]))
        self.sport_combo = ttk.Combobox(search_frame, textvariable=self.sport_var, values=sorted(sports))
        self.sport_combo.grid(row=1, column=1, padx=5, pady=5)

        # Capacity Required
        ttk.Label(search_frame, text="Capacity:").grid(row=2, column=0, padx=5, pady=5)
        self.capacity_entry = ttk.Entry(search_frame)
        self.capacity_entry.grid(row=2, column=1, padx=5, pady=5)

        # Search Button
        ttk.Button(search_frame, text="Search", command=self.search_grounds).grid(row=3, column=0, columnspan=2, pady=10)

        # Results Frame
        results_frame = ttk.LabelFrame(self.search_tab, text="Available Grounds", padding="10")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Results Treeview
        self.results_tree = ttk.Treeview(results_frame, 
        columns=("Name", "Capacity", "Location", "Available Slots"),
        show="headings")
        self.results_tree.heading("Name", text="Ground Name")
        self.results_tree.heading("Capacity", text="Capacity")
        self.results_tree.heading("Location", text="Location")
        self.results_tree.heading("Available Slots", text="Available Slots")
        self.results_tree.pack(fill="both", expand=True, pady=5)
        self.results_tree.bind("<Double-1>", self.show_ground_details)

        # Booking Frame
        booking_frame = ttk.LabelFrame(self.search_tab, text="Book Ground", padding="10")
        booking_frame.pack(fill="x", padx=10, pady=5)

        # Time Slot Selection
        ttk.Label(booking_frame, text="Time Slot:").grid(row=0, column=0, padx=5, pady=5)
        self.time_slot_var = tk.StringVar()
        self.time_slot_combo = ttk.Combobox(booking_frame, textvariable=self.time_slot_var,
            values=self.system.time_slots)
        self.time_slot_combo.grid(row=0, column=1, padx=5, pady=5)

        # Event Name
        ttk.Label(booking_frame, text="Event:").grid(row=1, column=0, padx=5, pady=5)
        self.event_entry = ttk.Entry(booking_frame)
        self.event_entry.grid(row=1, column=1, padx=5, pady=5)

        # Organizer Name
        ttk.Label(booking_frame, text="Organizer:").grid(row=2, column=0, padx=5, pady=5)
        self.organizer_entry = ttk.Entry(booking_frame)
        self.organizer_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(booking_frame, text="Book Selected Ground", 
        command=self.book_ground).grid(row=3, column=0, columnspan=2, pady=10)

    def search_grounds(self):
        try:
            date = self.date_entry.get()
            sport = self.sport_var.get()
            capacity = int(self.capacity_entry.get())

            # Clear previous results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)

            # Search and display results
            available_grounds = self.system.search_available_grounds(date, sport, capacity)
            for ground in available_grounds:
                self.results_tree.insert("", "end", values=(
                    ground.name,
                    ground.capacity,
                    ground.location,
                    ", ".join(ground.available_slots)
                ))

        except ValueError:
            messagebox.showerror("Error", "Please enter valid capacity (number)")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def book_ground(self):
        selected_item = self.results_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a ground to book")
            return

        # Validate all required fields
        if not self.time_slot_var.get():
            messagebox.showwarning("Warning", "Please select a time slot")
            return

        if not self.event_entry.get():
            messagebox.showwarning("Warning", "Please enter an event name")
            return

        if not self.organizer_entry.get():
            messagebox.showwarning("Warning", "Please enter organizer name")
            return

        ground_name = self.results_tree.item(selected_item)['values'][0]
        date = self.date_entry.get()
        time_slot = self.time_slot_var.get()
        event = self.event_entry.get()
        organizer = self.organizer_entry.get()

        # Find the selected ground
        selected_ground = next((g for g in self.system.grounds if g.name == ground_name), None)

        if selected_ground and self.system.book_ground(selected_ground, date, time_slot, event, organizer):
            messagebox.showinfo("Success", 
            f"Successfully booked {ground_name}\nDate: {date}\nTime: {time_slot}")
            # Refresh all views
            self.search_grounds()
            self.refresh_history()
            # Clear booking form
            self.time_slot_var.set("")
            self.event_entry.delete(0, tk.END)
            self.organizer_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", 
            "Unable to book the ground for the selected time slot")

    def setup_all_grounds_tab(self):
        # All Grounds Treeview
        self.all_grounds_tree = ttk.Treeview(self.all_grounds_tab,
            columns=("Name", "Capacity", "Sports", "Location"),
            show="headings")
        self.all_grounds_tree.heading("Name", text="Ground Name")
        self.all_grounds_tree.heading("Capacity", text="Capacity")
        self.all_grounds_tree.heading("Sports", text="Sports")
        self.all_grounds_tree.heading("Location", text="Location")
        self.all_grounds_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.all_grounds_tree.bind("<Double-1>", self.show_ground_details)

        # Populate all grounds
        self.refresh_all_grounds()

    def setup_history_tab(self):
        # History Treeview
        self.history_tree = ttk.Treeview(self.history_tab,
        columns=("Date", "Ground", "Time Slot", "Event", "Organizer"),
        show="headings")
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Ground", text="Ground")
        self.history_tree.heading("Time Slot", text="Time Slot")
        self.history_tree.heading("Event", text="Event")
        self.history_tree.heading("Organizer", text="Organizer")
        self.history_tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Refresh button
        ttk.Button(self.history_tab, text="Refresh History",
        command=self.refresh_history).pack(pady=5)

        # Initial population
        self.refresh_history()

    def setup_manage_grounds_tab(self):
        # Create main frame
        manage_frame = ttk.LabelFrame(self.manage_grounds_tab, text="Add New Ground", padding="10")
        manage_frame.pack(fill="x", padx=10, pady=5)

        # Ground Name
        ttk.Label(manage_frame, text="Ground Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_ground_name = ttk.Entry(manage_frame, width=40)
        self.new_ground_name.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        # Capacity
        ttk.Label(manage_frame, text="Capacity:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.new_ground_capacity = ttk.Entry(manage_frame, width=20)
        self.new_ground_capacity.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        # Location
        ttk.Label(manage_frame, text="Location:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.new_ground_location = ttk.Entry(manage_frame, width=40)
        self.new_ground_location.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        # Sports (Multiple selection)
        ttk.Label(manage_frame, text="Sports:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.sports_frame = ttk.Frame(manage_frame)
        self.sports_frame.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        self.sports_vars = {}
        sports = ["Football", "Cricket", "Basketball", "Volleyball", "Tennis", "Athletics", "Rugby"]
        for i, sport in enumerate(sports):
            var = tk.BooleanVar()
            self.sports_vars[sport] = var
            ttk.Checkbutton(self.sports_frame, text=sport, variable=var).grid(row=i//3, column=i%3, padx=5, sticky="w")

        # Submit Button
        ttk.Button(manage_frame, text="Add Ground", 
                   command=self.add_new_ground).grid(row=4, column=0, columnspan=4, pady=20)

        # Separator
        ttk.Separator(self.manage_grounds_tab, orient='horizontal').pack(fill='x', padx=10, pady=10)

        # Delete Ground Section
        delete_frame = ttk.LabelFrame(self.manage_grounds_tab, text="Delete Ground", padding="10")
        delete_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(delete_frame, text="Select Ground:").pack(side="left", padx=5)
        self.delete_ground_var = tk.StringVar()
        self.delete_ground_combo = ttk.Combobox(delete_frame, textvariable=self.delete_ground_var)
        self.delete_ground_combo.pack(side="left", padx=5)

        ttk.Button(delete_frame, text="Delete Ground", 
                   command=self.delete_ground).pack(side="left", padx=5)

        # Update ground list
        self.update_delete_ground_list()    
    
    def show_ground_details(self, event):
        selected_item = event.widget.selection()
        if not selected_item:
            return

        ground_name = event.widget.item(selected_item)['values'][0]
        ground = next((g for g in self.system.grounds if g.name == ground_name), None)

        if ground:
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Ground Details - {ground.name}")
            details_window.geometry("400x500")

            # Create details text
            details_text = scrolledtext.ScrolledText(details_window, wrap=tk.WORD, width=45, height=25)
            details_text.pack(padx=10, pady=10, fill="both", expand=True)

            # Format details
            details = f"""Ground Name: {ground.name}
Location: {ground.location}
Capacity: {ground.capacity}
Sports: {', '.join(ground.sports)}

Current Bookings:
"""
            if ground.bookings:
                for booking in ground.bookings:
                    details += f"\n{booking['date']} - {booking['time_slot']}\n"
                    details += f"Event: {booking['event']}\n"
                    details += f"Organizer: {booking['organizer']}\n"
            else:
                details += "\nNo current bookings"

            details_text.insert(tk.END, details)
            details_text.configure(state='disabled')

    def refresh_all_grounds(self):
        # Clear existing items
        for item in self.all_grounds_tree.get_children():
            self.all_grounds_tree.delete(item)

        # Populate with all grounds
        for ground in self.system.grounds:
            self.all_grounds_tree.insert("", "end", values=(
                ground.name,
                ground.capacity,
                ", ".join(ground.sports),
                ground.location
            ))

    def refresh_history(self):
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Get all booking history
        bookings = self.system.get_booking_history()

        # Populate history
        for booking in bookings:
            self.history_tree.insert("", "end", values=(
                booking['date'],
                booking.get('ground_name', 'Unknown'),
                booking['time_slot'],
                booking['event'],
                booking['organizer']
            ))

    def add_new_ground(self):
        try:
            # Validate required fields
            if not self.new_ground_name.get():
                messagebox.showerror("Error", "Ground Name is required")
                return

            # Get sports
            selected_sports = [sport for sport, var in self.sports_vars.items() if var.get()]
            if not selected_sports:
                messagebox.showerror("Error", "Select at least one sport")
                return

            # Create new ground
            new_ground = Ground(
                name=self.new_ground_name.get(),
                capacity=int(self.new_ground_capacity.get()),
                sports=selected_sports,
                location=self.new_ground_location.get()
            )

            # Add to system
            self.system.grounds.append(new_ground)

            # Refresh views
            self.refresh_all_grounds()
            self.update_delete_ground_list()

            # Clear form
            self.new_ground_name.delete(0, tk.END)
            self.new_ground_capacity.delete(0, tk.END)
            self.new_ground_location.delete(0, tk.END)
            
            # Reset sports checkboxes
            for var in self.sports_vars.values():
                var.set(False)

            messagebox.showinfo("Success", "Ground added successfully")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid capacity")
        except Exception as e:
            messagebox.showerror("Error", str(e))    
    
    def update_delete_ground_list(self):
        # Update ground names for deletion
        ground_names = [ground.name for ground in self.system.grounds]
        self.delete_ground_combo['values'] = ground_names

    def delete_ground(self):
        ground_name = self.delete_ground_var.get()
        if not ground_name:
            messagebox.showwarning("Warning", "Please select a ground to delete")
            return

        # Find and remove the ground
        self.system.grounds = [ground for ground in self.system.grounds if ground.name != ground_name]

        # Refresh views
        self.refresh_all_grounds()
        self.update_delete_ground_list()

        messagebox.showinfo("Success", f"Ground '{ground_name}' deleted successfully")

def main():
    root = tk.Tk()
    root.title("Grounds Automation System")
    root.geometry("800x600")
    app = GroundsAutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
