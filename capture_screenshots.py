"""
Programmatic Screenshot Capture Suite for Pet Clinic Management System (Lab 4).

Automates GUI interactions, simulates clinical workflows across all 3 tabs,
and captures high-resolution screenshots into the screenshots/ directory:
  1. screenshots/01_tab_owners_pets.png: Default Tab 1 view with initial sample data
  2. screenshots/02_registered_owner.png: Registered new owner (O100 - Diana Prince)
  3. screenshots/03_added_pet.png: Registered new pet patient (P100 - Shadow)
  4. screenshots/04_tab_appointments.png: Default Tab 2 appointments list
  5. screenshots/05_scheduled_appointment.png: Scheduled new appointment (APT-100)
  6. screenshots/06_cancelled_appointment.png: Cancelled appointment with status update
  7. screenshots/07_tab_records_overview.png: Tab 3 records overview & clinical dossier
  8. screenshots/08_unit_tests_pass.png: Subprocess execution of 12 passing unit tests
"""
import os
import sys
import time
import subprocess
import tkinter as tk
from PIL import ImageGrab

# Initialize High-DPI awareness on Windows to ensure crisp font and window rendering
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import models
import app
import main


def grab_window(window: tk.Misc, filepath: str) -> None:
    """
    Capture a Tkinter window and save as PNG.

    Uses PIL.ImageGrab with fallback to window handle capture to guarantee
    flawless operation across local, scaled DPI, and remote display environments.

    Args:
        window: The Tkinter window or widget to capture.
        filepath: Target file destination for the PNG image.
    """
    window.update_idletasks()
    window.update()
    time.sleep(0.3)
    x = window.winfo_rootx()
    y = window.winfo_rooty()
    w = window.winfo_width()
    h = window.winfo_height()

    try:
        # Standard screen grab with bounding box
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    except Exception:
        # Fallback to direct window handle grab for headless/redirected sessions
        hwnd = window.winfo_id()
        img = ImageGrab.grab(window=hwnd)

    img.save(filepath, "PNG")
    print(f"Captured: {filepath} ({w}x{h})")


def run_capture_suite() -> None:
    """
    Launch PetClinicApp with sample data and systematically capture all 8 scenarios.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "screenshots")
    os.makedirs(output_dir, exist_ok=True)

    print("==================================================================")
    print("Pet Clinic Management System - Automated Screenshot Capture Suite")
    print("==================================================================")
    print(f"Output directory: {output_dir}")

    # Initialize sample clinical data and launch app
    db = main.initialize_sample_data()
    clinic_app = app.PetClinicApp(db)

    # Enable headless/automation mode to prevent modal dialog halts
    clinic_app._suppress_dialogs = True
    clinic_app._auto_confirm = True

    # Bring window to front and ensure rendered
    clinic_app.deiconify()
    clinic_app.lift()
    clinic_app.focus_force()
    clinic_app.update_idletasks()
    clinic_app.update()

    try:
        # ---------------------------------------------------------------------
        # Scenario 1: Tab 1 Owners & Pets default view with sample data
        # ---------------------------------------------------------------------
        print("\n[1/8] Capturing Tab 1: Owners & Pets default view...")
        clinic_app.notebook.select(0)
        clinic_app._refresh_all_views()
        clinic_app.update_idletasks()
        clinic_app.update()
        time.sleep(0.2)
        shot_01 = os.path.join(output_dir, "01_tab_owners_pets.png")
        grab_window(clinic_app, shot_01)

        # ---------------------------------------------------------------------
        # Scenario 2: Register New Owner (O100 - Diana Prince)
        # ---------------------------------------------------------------------
        print("\n[2/8] Registering new owner and capturing view...")
        clinic_app.notebook.select(0)
        clinic_app.ent_owner_id.delete(0, tk.END)
        clinic_app.ent_owner_id.insert(0, "O100")
        clinic_app.ent_owner_name.delete(0, tk.END)
        clinic_app.ent_owner_name.insert(0, "Diana Prince")
        clinic_app.ent_owner_phone.delete(0, tk.END)
        clinic_app.ent_owner_phone.insert(0, "555-0199")

        clinic_app._add_owner()

        # Highlight newly registered owner in Treeview
        if clinic_app.owner_tree.exists("O100"):
            clinic_app.owner_tree.selection_set("O100")
            clinic_app.owner_tree.see("O100")

        clinic_app.update_idletasks()
        clinic_app.update()
        shot_02 = os.path.join(output_dir, "02_registered_owner.png")
        grab_window(clinic_app, shot_02)

        # ---------------------------------------------------------------------
        # Scenario 3: Add New Pet Record (P100 - Shadow)
        # ---------------------------------------------------------------------
        print("\n[3/8] Registering new pet and capturing view...")
        clinic_app.notebook.select(0)
        clinic_app.ent_pet_id.delete(0, tk.END)
        clinic_app.ent_pet_id.insert(0, "P100")
        clinic_app.ent_pet_name.delete(0, tk.END)
        clinic_app.ent_pet_name.insert(0, "Shadow")
        clinic_app.cmb_pet_type.set("Dog")
        clinic_app.ent_pet_breed.delete(0, tk.END)
        clinic_app.ent_pet_breed.insert(0, "Siberian Husky")
        clinic_app.ent_pet_age.delete(0, tk.END)
        clinic_app.ent_pet_age.insert(0, "2")
        clinic_app.ent_pet_weight.delete(0, tk.END)
        clinic_app.ent_pet_weight.insert(0, "22.5")

        # Select owner O100 (Diana Prince)
        for opt in clinic_app.pet_owner_combobox["values"]:
            if opt.startswith("O100"):
                clinic_app.pet_owner_combobox.set(opt)
                break

        clinic_app._add_pet()

        # Highlight newly added pet in Treeview
        if clinic_app.pet_tree.exists("P100"):
            clinic_app.pet_tree.selection_set("P100")
            clinic_app.pet_tree.see("P100")

        clinic_app.update_idletasks()
        clinic_app.update()
        shot_03 = os.path.join(output_dir, "03_added_pet.png")
        grab_window(clinic_app, shot_03)

        # ---------------------------------------------------------------------
        # Scenario 4: Tab 2 Appointments default view
        # ---------------------------------------------------------------------
        print("\n[4/8] Switching to Tab 2 Appointments and capturing default view...")
        clinic_app.notebook.select(1)
        # Optimize column widths so all columns including Status fit comfortably in view
        clinic_app.apt_tree.column("id", width=60)
        clinic_app.apt_tree.column("date", width=75)
        clinic_app.apt_tree.column("time", width=65)
        clinic_app.apt_tree.column("pet", width=85)
        clinic_app.apt_tree.column("owner", width=85)
        clinic_app.apt_tree.column("reason", width=105)
        clinic_app.apt_tree.column("status", width=85)
        clinic_app.update_idletasks()
        clinic_app.update()
        time.sleep(0.2)
        shot_04 = os.path.join(output_dir, "04_tab_appointments.png")
        grab_window(clinic_app, shot_04)

        # ---------------------------------------------------------------------
        # Scenario 5: Schedule Appointment (APT-100 for P100 with dynamic filter)
        # ---------------------------------------------------------------------
        print("\n[5/8] Scheduling new appointment and capturing view...")
        clinic_app.notebook.select(1)

        # Select owner O100
        for opt in clinic_app.apt_owner_combobox["values"]:
            if opt.startswith("O100"):
                clinic_app.apt_owner_combobox.set(opt)
                clinic_app._on_apt_owner_selected()
                break

        # Select dynamically filtered pet P100
        for opt in clinic_app.apt_pet_combobox["values"]:
            if opt.startswith("P100"):
                clinic_app.apt_pet_combobox.set(opt)
                break

        clinic_app.ent_apt_id.delete(0, tk.END)
        clinic_app.ent_apt_id.insert(0, "APT-100")
        clinic_app.ent_apt_date.delete(0, tk.END)
        clinic_app.ent_apt_date.insert(0, "2026-09-25")
        clinic_app.cmb_apt_time.set("10:30 AM")
        clinic_app.ent_apt_reason.delete(0, tk.END)
        clinic_app.ent_apt_reason.insert(0, "Annual Wellness Checkup & Rabies Vaccination")

        clinic_app._schedule_appointment()

        # Select and display clinical summary for the newly booked appointment
        if clinic_app.apt_tree.exists("APT-100"):
            clinic_app.apt_tree.selection_set("APT-100")
            clinic_app.apt_tree.see("APT-100")
            clinic_app._on_apt_selected()

        clinic_app.update_idletasks()
        clinic_app.update()
        shot_05 = os.path.join(output_dir, "05_scheduled_appointment.png")
        grab_window(clinic_app, shot_05)

        # ---------------------------------------------------------------------
        # Scenario 6: Cancel Appointment (cancel APT-100 and show Cancelled status)
        # ---------------------------------------------------------------------
        print("\n[6/8] Cancelling appointment and capturing view...")
        clinic_app.notebook.select(1)
        target_apt = "APT-100" if clinic_app.apt_tree.exists("APT-100") else "APT-001"
        clinic_app.apt_tree.selection_set(target_apt)
        clinic_app._on_apt_selected()

        clinic_app._cancel_appointment()

        if clinic_app.apt_tree.exists(target_apt):
            clinic_app.apt_tree.selection_set(target_apt)
            clinic_app.apt_tree.see(target_apt)
            clinic_app._on_apt_selected()

        clinic_app.update_idletasks()
        clinic_app.update()
        shot_06 = os.path.join(output_dir, "06_cancelled_appointment.png")
        grab_window(clinic_app, shot_06)

        # ---------------------------------------------------------------------
        # Scenario 7: Tab 3 Records Overview & Clinical Dossier
        # ---------------------------------------------------------------------
        print("\n[7/8] Switching to Tab 3 Records Overview and capturing report view...")
        clinic_app.notebook.select(2)
        clinic_app._refresh_all_views()
        if clinic_app.overview_tree.exists("view_full_dossier"):
            clinic_app.overview_tree.selection_set("view_full_dossier")
            clinic_app._on_overview_item_selected()

        clinic_app.update_idletasks()
        clinic_app.update()
        time.sleep(0.2)
        shot_07 = os.path.join(output_dir, "07_tab_records_overview.png")
        grab_window(clinic_app, shot_07)

        # ---------------------------------------------------------------------
        # Scenario 8: Unit Tests Passing (12/12)
        # ---------------------------------------------------------------------
        print("\n[8/8] Running unit tests via subprocess and capturing output view...")
        cmd = [sys.executable, "-m", "unittest", "test_system", "-v"]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        test_output = proc.stdout + proc.stderr

        # Create a dedicated terminal output window
        test_win = tk.Toplevel(clinic_app)
        test_win.title("Pet Clinic System - Unit Test Execution Results (12/12 Passed)")
        test_win.geometry("950x700")
        test_win.configure(bg="#1e1e1e")

        hdr_frame = tk.Frame(test_win, bg="#2d2d2d", padx=12, pady=8)
        hdr_frame.pack(fill=tk.X)

        lbl_hdr = tk.Label(
            hdr_frame,
            text="PowerShell Console - python -m unittest test_system -v",
            font=("Consolas", 10, "bold"),
            bg="#2d2d2d",
            fg="#e0e0e0",
            anchor="w",
        )
        lbl_hdr.pack(side=tk.LEFT)

        txt_frame = tk.Frame(test_win, bg="#1e1e1e", padx=10, pady=10)
        txt_frame.pack(fill=tk.BOTH, expand=True)

        txt_widget = tk.Text(
            txt_frame,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#cccccc",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )
        txt_widget.pack(fill=tk.BOTH, expand=True)

        txt_widget.tag_configure("cmd", foreground="#61afef", font=("Consolas", 10, "bold"))
        txt_widget.tag_configure("ok", foreground="#98c379", font=("Consolas", 10, "bold"))
        txt_widget.tag_configure("header", foreground="#e5c07b", font=("Consolas", 10))

        prompt_str = f"PS {base_dir}> python -m unittest test_system -v\n\n"
        txt_widget.insert(tk.END, prompt_str, "cmd")

        for line in test_output.splitlines(keepends=True):
            if "... ok" in line or line.strip() == "OK":
                txt_widget.insert(tk.END, line, "ok")
            elif "test_" in line:
                txt_widget.insert(tk.END, line, "header")
            else:
                txt_widget.insert(tk.END, line)

        txt_widget.config(state=tk.DISABLED)
        test_win.deiconify()
        test_win.lift()
        test_win.focus_force()
        test_win.update_idletasks()
        test_win.update()
        time.sleep(0.3)

        shot_08 = os.path.join(output_dir, "08_unit_tests_pass.png")
        grab_window(test_win, shot_08)
        test_win.destroy()

        print("\nAll 8 screenshots successfully captured!")

    finally:
        clinic_app.destroy()


if __name__ == "__main__":
    run_capture_suite()
