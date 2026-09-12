"""
Pet Clinic Management System - GUI Application
Subclasses tk.Tk and implements a multi-tabbed clinical management interface.
Recycles layout, styling, and widget paradigms from Lab3 Food Delivery System.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Tuple, Any

from models import (
    Owner,
    Pet,
    Appointment,
    AppointmentStatus,
    ClinicDatabase,
    PetFactory,
)


class PetClinicApp(tk.Tk):
    """
    Main GUI application window for the Pet Clinic Management System.

    Features:
        - Tab 1: Owners & Pets (Registration forms and dual Treeviews)
        - Tab 2: Appointments (Booking with dynamic owner-filtered pets & management actions)
        - Tab 3: Records Overview (Summary statistics cards & master-detail monospace clinical dossier)
    """

    def __init__(self, database: Optional[ClinicDatabase] = None) -> None:
        """
        Initialize the Pet Clinic GUI application.

        Args:
            database: Optional ClinicDatabase instance. Defaults to the singleton.
        """
        super().__init__()
        self.title("Pet Clinic Management System")
        self.geometry("950x700")
        self.minsize(850, 600)

        # Automation and non-blocking test flags
        self._suppress_dialogs: bool = False
        self._auto_confirm: bool = False
        self._last_dialog: Optional[Tuple[str, str, str]] = None

        # Connect to singleton database
        self.db: ClinicDatabase = database if database is not None else ClinicDatabase()

        # ID Generation counters
        self._sync_id_counters()

        # Setup styling and user interface
        self._setup_style()
        self._build_ui()

        # Initial data population into all widgets
        self._refresh_all_views()

    # =========================================================================
    # DIALOG HELPERS (Headless / Automation Friendly)
    # =========================================================================
    def _show_info(self, title: str, message: str) -> None:
        """Display information messagebox (non-blocking when suppressed)."""
        if getattr(self, "_suppress_dialogs", False):
            self._last_dialog = ("info", title, message)
            return
        messagebox.showinfo(title, message)

    def _show_warning(self, title: str, message: str) -> None:
        """Display warning messagebox (non-blocking when suppressed)."""
        if getattr(self, "_suppress_dialogs", False):
            self._last_dialog = ("warning", title, message)
            return
        messagebox.showwarning(title, message)

    def _show_error(self, title: str, message: str) -> None:
        """Display error messagebox (non-blocking when suppressed)."""
        if getattr(self, "_suppress_dialogs", False):
            self._last_dialog = ("error", title, message)
            return
        messagebox.showerror(title, message)

    def _confirm(self, title: str, message: str) -> bool:
        """Display confirmation dialog (returns True immediately if auto_confirm is enabled)."""
        if getattr(self, "_auto_confirm", False):
            return True
        return messagebox.askyesno(title, message)

    # =========================================================================
    # ID GENERATION & STYLING
    # =========================================================================
    def _sync_id_counters(self) -> None:
        """Synchronize internal ID generation counters with database contents."""
        owner_ids = [o.owner_id for o in self.db.get_all_owners()]
        self.owner_counter = self._extract_max_id_num("OWN", owner_ids) + 1

        pet_ids = [p.pet_id for p in self.db.get_all_pets()]
        self.pet_counter = self._extract_max_id_num("PET", pet_ids) + 1

        apt_ids = [a.appointment_id for a in self.db.get_all_appointments()]
        self.apt_counter = self._extract_max_id_num("APT", apt_ids) + 1

    @staticmethod
    def _extract_max_id_num(prefix: str, ids: List[str]) -> int:
        """Extract highest numerical identifier with given prefix."""
        max_num = 0
        for item_id in ids:
            parts = item_id.split("-")
            if len(parts) == 2 and parts[1].isdigit():
                max_num = max(max_num, int(parts[1]))
        if max_num == 0:
            return len(ids)
        return max_num

    def _setup_style(self) -> None:
        """Configure ttk styles and clam theme to match Lab3 aesthetics."""
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        # Typography and widget styling
        self.style.configure("TLabel", font=("Arial", 9))
        self.style.configure("TButton", font=("Arial", 9))
        self.style.configure("Header.TLabel", font=("Arial", 11, "bold"))
        self.style.configure("StatTitle.TLabel", font=("Arial", 9, "bold"), foreground="#4a5568")
        self.style.configure("StatValue.TLabel", font=("Arial", 16, "bold"), foreground="#2b6cb0")
        self.style.configure("Treeview.Heading", font=("Arial", 9, "bold"))
        self.style.configure("Treeview", font=("Arial", 9), rowheight=22)

    # =========================================================================
    # UI CONSTRUCTION
    # =========================================================================
    def _build_ui(self) -> None:
        """Construct the main notebook and individual application tabs."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Tab 1: Owners & Pets
        self.tab_owners_pets = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_owners_pets, text="  Owners & Pets  ")
        self._build_owners_pets_tab()

        # Tab 2: Appointments
        self.tab_appointments = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_appointments, text="  Appointments  ")
        self._build_appointments_tab()

        # Tab 3: Records Overview
        self.tab_overview = ttk.Frame(self.notebook)
        self.tab_records_overview = self.tab_overview  # Alias
        self.notebook.add(self.tab_records_overview, text="  Records Overview  ")
        self._build_records_overview_tab()

        # Listen for tab changes
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    # =========================================================================
    # TAB 1: Owners & Pets
    # =========================================================================
    def _build_owners_pets_tab(self) -> None:
        """Construct Tab 1 with horizontal PanedWindow dividing Owners and Pets."""
        paned = ttk.PanedWindow(self.tab_owners_pets, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # ----------------- Left Pane: Owners -----------------
        left_pane = ttk.Frame(paned, padding=4)
        paned.add(left_pane, weight=1)

        # Owner Registration Form
        owner_form = ttk.LabelFrame(left_pane, text="Register Pet Owner", padding=10)
        owner_form.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(owner_form, text="Owner ID:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.ent_owner_id = ttk.Entry(owner_form, width=24)
        self.ent_owner_id.grid(row=0, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        ttk.Label(owner_form, text="Full Name:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.ent_owner_name = ttk.Entry(owner_form, width=24)
        self.ent_owner_name.grid(row=1, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        ttk.Label(owner_form, text="Contact No:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.ent_owner_phone = ttk.Entry(owner_form, width=24)
        self.ent_owner_phone.grid(row=2, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        owner_form.columnconfigure(1, weight=1)

        self.btn_register_owner = ttk.Button(
            owner_form, text="Register Owner", command=self._add_owner
        )
        self.btn_register_owner.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(8, 2))

        # Owners Treeview
        owner_table_frame = ttk.LabelFrame(left_pane, text="Registered Owners", padding=6)
        owner_table_frame.pack(fill=tk.BOTH, expand=True)

        owner_cols = ("id", "name", "contact", "pets")
        self.owner_tree = ttk.Treeview(
            owner_table_frame, columns=owner_cols, show="headings", selectmode="browse"
        )
        self.owner_tree.heading("id", text="Owner ID")
        self.owner_tree.heading("name", text="Name")
        self.owner_tree.heading("contact", text="Contact")
        self.owner_tree.heading("pets", text="Pets")

        self.owner_tree.column("id", width=75, anchor=tk.CENTER)
        self.owner_tree.column("name", width=120)
        self.owner_tree.column("contact", width=105)
        self.owner_tree.column("pets", width=45, anchor=tk.CENTER)

        owner_scroll = ttk.Scrollbar(
            owner_table_frame, orient=tk.VERTICAL, command=self.owner_tree.yview
        )
        self.owner_tree.configure(yscrollcommand=owner_scroll.set)
        self.owner_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        owner_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.owner_tree.bind("<<TreeviewSelect>>", self._on_owner_selected)

        # ----------------- Right Pane: Pets -----------------
        right_pane = ttk.Frame(paned, padding=4)
        paned.add(right_pane, weight=1)

        # Pet Registration Form
        pet_form = ttk.LabelFrame(right_pane, text="Register Pet Patient", padding=10)
        pet_form.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(pet_form, text="Pet ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ent_pet_id = ttk.Entry(pet_form, width=22)
        self.ent_pet_id.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(pet_form, text="Pet Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ent_pet_name = ttk.Entry(pet_form, width=22)
        self.ent_pet_name.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(pet_form, text="Pet Type:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.cmb_pet_type = ttk.Combobox(
            pet_form,
            values=PetFactory.get_supported_types(),
            state="readonly",
            width=20,
        )
        self.cmb_pet_type.set("Dog")
        self.cmb_pet_type.grid(row=2, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(pet_form, text="Breed:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.ent_pet_breed = ttk.Entry(pet_form, width=22)
        self.ent_pet_breed.grid(row=3, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(pet_form, text="Age (years):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.ent_pet_age = ttk.Entry(pet_form, width=22)
        self.ent_pet_age.insert(0, "1")
        self.ent_pet_age.grid(row=4, column=1, sticky=tk.EW, pady=2, padx=(5, 0))
        self.spn_pet_age = self.ent_pet_age  # Compatibility alias

        ttk.Label(pet_form, text="Weight (kg):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.ent_pet_weight = ttk.Entry(pet_form, width=22)
        self.ent_pet_weight.grid(row=5, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(pet_form, text="Select Owner:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.pet_owner_combobox = ttk.Combobox(pet_form, state="readonly", width=20)
        self.pet_owner_combobox.grid(row=6, column=1, sticky=tk.EW, pady=2, padx=(5, 0))
        self.cmb_pet_owner = self.pet_owner_combobox  # Compatibility alias

        pet_form.columnconfigure(1, weight=1)

        self.btn_add_pet = ttk.Button(
            pet_form, text="Add Pet Record", command=self._add_pet
        )
        self.btn_add_pet.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=(6, 2))
        self.btn_register_pet = self.btn_add_pet  # Compatibility alias

        # Pets Treeview
        pet_table_frame = ttk.LabelFrame(right_pane, text="Registered Pets", padding=6)
        pet_table_frame.pack(fill=tk.BOTH, expand=True)

        pet_cols = ("id", "name", "type", "breed", "age", "weight", "owner")
        self.pet_tree = ttk.Treeview(
            pet_table_frame, columns=pet_cols, show="headings", selectmode="browse"
        )
        self.pet_tree.heading("id", text="Pet ID")
        self.pet_tree.heading("name", text="Name")
        self.pet_tree.heading("type", text="Type")
        self.pet_tree.heading("breed", text="Breed")
        self.pet_tree.heading("age", text="Age")
        self.pet_tree.heading("weight", text="Weight (kg)")
        self.pet_tree.heading("owner", text="Owner ID")

        self.pet_tree.column("id", width=65, anchor=tk.CENTER)
        self.pet_tree.column("name", width=85)
        self.pet_tree.column("type", width=60, anchor=tk.CENTER)
        self.pet_tree.column("breed", width=95)
        self.pet_tree.column("age", width=40, anchor=tk.CENTER)
        self.pet_tree.column("weight", width=65, anchor=tk.E)
        self.pet_tree.column("owner", width=75, anchor=tk.CENTER)

        pet_scroll = ttk.Scrollbar(
            pet_table_frame, orient=tk.VERTICAL, command=self.pet_tree.yview
        )
        self.pet_tree.configure(yscrollcommand=pet_scroll.set)
        self.pet_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pet_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # =========================================================================
    # TAB 2: Appointments
    # =========================================================================
    def _build_appointments_tab(self) -> None:
        """Construct Tab 2 with appointment booking and management."""
        paned = ttk.PanedWindow(self.tab_appointments, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # ----------------- Left Pane: Booking Form -----------------
        left_pane = ttk.Frame(paned, padding=4)
        paned.add(left_pane, weight=1)

        booking_form = ttk.LabelFrame(left_pane, text="Schedule New Appointment", padding=10)
        booking_form.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(booking_form, text="Appointment ID:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.ent_apt_id = ttk.Entry(booking_form, width=24)
        self.ent_apt_id.grid(row=0, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        ttk.Label(booking_form, text="Select Owner:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.apt_owner_combobox = ttk.Combobox(booking_form, state="readonly", width=22)
        self.apt_owner_combobox.grid(row=1, column=1, sticky=tk.EW, pady=3, padx=(5, 0))
        self.apt_owner_combobox.bind("<<ComboboxSelected>>", self._on_apt_owner_selected)
        self.cmb_apt_owner = self.apt_owner_combobox  # Compatibility alias

        ttk.Label(booking_form, text="Select Pet:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.apt_pet_combobox = ttk.Combobox(booking_form, state="readonly", width=22)
        self.apt_pet_combobox.grid(row=2, column=1, sticky=tk.EW, pady=3, padx=(5, 0))
        self.cmb_apt_pet = self.apt_pet_combobox  # Compatibility alias

        self.lbl_pet_hint = ttk.Label(booking_form, text="", font=("Arial", 8))
        self.lbl_pet_hint.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 3))

        ttk.Label(booking_form, text="Date (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.ent_apt_date = ttk.Entry(booking_form, width=24)
        self.ent_apt_date.insert(0, "2026-09-15")
        self.ent_apt_date.grid(row=4, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        ttk.Label(booking_form, text="Time Slot:").grid(row=5, column=0, sticky=tk.W, pady=3)
        time_slots = [
            "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM",
            "11:15 AM", "01:30 PM", "02:00 PM", "02:15 PM", "02:30 PM",
            "03:00 PM", "03:30 PM", "04:00 PM"
        ]
        self.cmb_apt_time = ttk.Combobox(booking_form, values=time_slots, state="readonly", width=22)
        self.cmb_apt_time.set("10:00 AM")
        self.cmb_apt_time.grid(row=5, column=1, sticky=tk.EW, pady=3, padx=(5, 0))
        self.ent_apt_time = self.cmb_apt_time  # Compatibility alias

        ttk.Label(booking_form, text="Clinical Reason:").grid(row=6, column=0, sticky=tk.W, pady=3)
        self.ent_apt_reason = ttk.Entry(booking_form, width=24)
        self.ent_apt_reason.grid(row=6, column=1, sticky=tk.EW, pady=3, padx=(5, 0))

        booking_form.columnconfigure(1, weight=1)

        self.btn_schedule_apt = ttk.Button(
            booking_form, text="Schedule Appointment", command=self._schedule_appointment
        )
        self.btn_schedule_apt.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=(10, 2))

        # Selected Appointment Clinical Summary Preview
        preview_frame = ttk.LabelFrame(left_pane, text="Selected Appointment Summary", padding=6)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        self.apt_summary_txt = tk.Text(
            preview_frame, height=8, width=32, wrap=tk.WORD, font=("Courier New", 9)
        )
        self.apt_summary_txt.pack(fill=tk.BOTH, expand=True)
        self.apt_summary_txt.insert(
            tk.END, "Select an appointment from the table to view its clinical summary."
        )
        self.apt_summary_txt.config(state=tk.DISABLED)

        # ----------------- Right Pane: Appointments Treeview -----------------
        right_pane = ttk.Frame(paned, padding=4)
        paned.add(right_pane, weight=2)

        apt_table_frame = ttk.LabelFrame(right_pane, text="Scheduled Clinic Appointments", padding=6)
        apt_table_frame.pack(fill=tk.BOTH, expand=True)

        apt_cols = ("id", "date", "time", "pet", "owner", "reason", "status")
        self.apt_tree = ttk.Treeview(
            apt_table_frame, columns=apt_cols, show="headings", selectmode="browse"
        )
        self.apt_tree.heading("id", text="APT ID")
        self.apt_tree.heading("date", text="Date")
        self.apt_tree.heading("time", text="Time")
        self.apt_tree.heading("pet", text="Pet")
        self.apt_tree.heading("owner", text="Owner")
        self.apt_tree.heading("reason", text="Reason / Note")
        self.apt_tree.heading("status", text="Status")

        self.apt_tree.column("id", width=70, anchor=tk.CENTER)
        self.apt_tree.column("date", width=85, anchor=tk.CENTER)
        self.apt_tree.column("time", width=75, anchor=tk.CENTER)
        self.apt_tree.column("pet", width=105)
        self.apt_tree.column("owner", width=110)
        self.apt_tree.column("reason", width=160)
        self.apt_tree.column("status", width=85, anchor=tk.CENTER)

        apt_scroll = ttk.Scrollbar(
            apt_table_frame, orient=tk.VERTICAL, command=self.apt_tree.yview
        )
        self.apt_tree.configure(yscrollcommand=apt_scroll.set)
        self.apt_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        apt_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.apt_tree.bind("<<TreeviewSelect>>", self._on_apt_selected)

        # Management Action Buttons
        btn_bar = ttk.Frame(right_pane, padding=4)
        btn_bar.pack(fill=tk.X, pady=(4, 0))

        self.btn_complete_apt = ttk.Button(
            btn_bar, text="Mark Completed", command=self._complete_appointment
        )
        self.btn_complete_apt.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_cancel_apt = ttk.Button(
            btn_bar, text="Cancel Appointment", command=self._cancel_appointment
        )
        self.btn_cancel_apt.pack(side=tk.LEFT, padx=6)

    # =========================================================================
    # TAB 3: Records Overview
    # =========================================================================
    def _build_records_overview_tab(self) -> None:
        """Construct Tab 3 with executive statistics cards and monospace clinical dossier."""
        # Top Container: Statistics Cards
        stats_frame = ttk.LabelFrame(self.tab_records_overview, text="Clinic Summary Statistics", padding=8)
        stats_frame.pack(fill=tk.X, padx=8, pady=(6, 4))

        for c in range(4):
            stats_frame.columnconfigure(c, weight=1, uniform="stat_card")

        # Card 1: Registered Owners
        card_owners = ttk.Frame(stats_frame, relief=tk.RIDGE, borderwidth=1, padding=8)
        card_owners.grid(row=0, column=0, padx=4, pady=2, sticky=tk.NSEW)
        ttk.Label(card_owners, text="REGISTERED OWNERS", style="StatTitle.TLabel").pack()
        self.lbl_stat_owners = ttk.Label(card_owners, text="0", style="StatValue.TLabel")
        self.lbl_stat_owners.pack(pady=2)

        # Card 2: Registered Patients
        card_pets = ttk.Frame(stats_frame, relief=tk.RIDGE, borderwidth=1, padding=8)
        card_pets.grid(row=0, column=1, padx=4, pady=2, sticky=tk.NSEW)
        ttk.Label(card_pets, text="REGISTERED PATIENTS", style="StatTitle.TLabel").pack()
        self.lbl_stat_pets = ttk.Label(card_pets, text="0", style="StatValue.TLabel")
        self.lbl_stat_pets.pack(pady=2)
        self.lbl_stat_pets_detail = ttk.Label(
            card_pets, text="Dogs: 0 | Cats: 0 | Birds: 0 | Rabbits: 0", font=("Arial", 8)
        )
        self.lbl_stat_pets_detail.pack()
        self.lbl_stat_species = self.lbl_stat_pets_detail  # Compatibility alias
        self.lbl_stat_types = self.lbl_stat_pets_detail    # Compatibility alias

        # Card 3: Total Appointments
        card_apts = ttk.Frame(stats_frame, relief=tk.RIDGE, borderwidth=1, padding=8)
        card_apts.grid(row=0, column=2, padx=4, pady=2, sticky=tk.NSEW)
        ttk.Label(card_apts, text="TOTAL APPOINTMENTS", style="StatTitle.TLabel").pack()
        self.lbl_stat_apts = ttk.Label(card_apts, text="0", style="StatValue.TLabel")
        self.lbl_stat_apts.pack(pady=2)
        self.lbl_stat_appointments = self.lbl_stat_apts  # Compatibility alias

        # Card 4: Appointments Status Breakdown
        card_status = ttk.Frame(stats_frame, relief=tk.RIDGE, borderwidth=1, padding=8)
        card_status.grid(row=0, column=3, padx=4, pady=2, sticky=tk.NSEW)
        ttk.Label(card_status, text="APPOINTMENT STATUS", style="StatTitle.TLabel").pack()
        self.lbl_stat_status = ttk.Label(card_status, text="0 Active", style="StatValue.TLabel")
        self.lbl_stat_status.pack(pady=2)
        self.lbl_stat_statuses = self.lbl_stat_status    # Compatibility alias
        self.lbl_stat_status_detail = ttk.Label(
            card_status, text="Sched: 0 | Comp: 0 | Canc: 0", font=("Arial", 8)
        )
        self.lbl_stat_status_detail.pack()

        # Bottom Container: Master-Detail Monospace Clinical Dossier
        bottom_paned = ttk.PanedWindow(self.tab_records_overview, orient=tk.HORIZONTAL)
        bottom_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 6))

        # Master Selection Pane
        master_frame = ttk.LabelFrame(bottom_paned, text="Clinical Directory (Master)", padding=6)
        bottom_paned.add(master_frame, weight=1)

        self.overview_tree = ttk.Treeview(master_frame, show="tree", selectmode="browse")
        self.records_tree = self.overview_tree  # Compatibility alias
        overview_scroll = ttk.Scrollbar(
            master_frame, orient=tk.VERTICAL, command=self.overview_tree.yview
        )
        self.overview_tree.configure(yscrollcommand=overview_scroll.set)
        self.overview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        overview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.overview_tree.bind("<<TreeviewSelect>>", self._on_overview_item_selected)

        # Refresh button below master list
        self.btn_refresh_report = ttk.Button(
            master_frame, text="Refresh Report", command=self._refresh_all_views
        )
        self.btn_refresh_report.pack(fill=tk.X, pady=(4, 0))

        # Detail Monospace Text Pane
        detail_frame = ttk.LabelFrame(
            bottom_paned, text="Master-Detail Clinical Dossier & Audit Log", padding=6
        )
        bottom_paned.add(detail_frame, weight=3)

        self.dossier_txt = tk.Text(
            detail_frame, wrap=tk.NONE, font=("Courier New", 9), bg="#fafafa", fg="#1a202c"
        )
        self.report_txt = self.dossier_txt  # Compatibility alias
        self.txt_dossier = self.dossier_txt # Compatibility alias

        dossier_y_scroll = ttk.Scrollbar(
            detail_frame, orient=tk.VERTICAL, command=self.dossier_txt.yview
        )
        dossier_x_scroll = ttk.Scrollbar(
            detail_frame, orient=tk.HORIZONTAL, command=self.dossier_txt.xview
        )
        self.dossier_txt.configure(
            yscrollcommand=dossier_y_scroll.set, xscrollcommand=dossier_x_scroll.set
        )

        dossier_y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        dossier_x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.dossier_txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.dossier_txt.config(state=tk.DISABLED)

    # =========================================================================
    # CONTROLLER METHODS: Data Refresh & UI Synchronization
    # =========================================================================
    def _refresh_all_views(self) -> None:
        """Synchronize all Treeviews, Comboboxes, and Overview reports with database."""
        self._sync_id_counters()
        self._refresh_owner_tree()
        self._refresh_pet_tree()
        self._refresh_appointment_tree()
        self._refresh_all_owner_dropdowns()
        self._refresh_overview()
        self._update_next_id_placeholders()

    def _refresh_overview(self) -> None:
        """Refresh Tab 3 stats cards, clinical directory, and active dossier view."""
        self._refresh_overview_stats()
        self._refresh_overview_directory()

    def _update_next_id_placeholders(self) -> None:
        """Pre-populate ID fields with auto-suggested sequential identifiers."""
        if not self.ent_owner_id.get().strip():
            self.ent_owner_id.delete(0, tk.END)
            self.ent_owner_id.insert(0, f"OWN-{self.owner_counter:03d}")

        if not self.ent_pet_id.get().strip():
            self.ent_pet_id.delete(0, tk.END)
            self.ent_pet_id.insert(0, f"PET-{self.pet_counter:03d}")

        if not self.ent_apt_id.get().strip():
            self.ent_apt_id.delete(0, tk.END)
            self.ent_apt_id.insert(0, f"APT-{self.apt_counter:03d}")

    def _refresh_owner_tree(self) -> None:
        """Reload all registered owners into the Owner Treeview."""
        for row in self.owner_tree.get_children():
            self.owner_tree.delete(row)

        for owner in self.db.get_all_owners():
            pet_count = len(self.db.get_pets_by_owner(owner.owner_id))
            self.owner_tree.insert(
                "",
                tk.END,
                iid=owner.owner_id,
                values=(owner.owner_id, owner.name, owner.contact_number, pet_count),
            )

    def _refresh_pet_tree(self) -> None:
        """Reload all registered pets into the Pet Treeview."""
        for row in self.pet_tree.get_children():
            self.pet_tree.delete(row)

        for pet in self.db.get_all_pets():
            self.pet_tree.insert(
                "",
                tk.END,
                iid=pet.pet_id,
                values=(
                    pet.pet_id,
                    pet.name,
                    pet.pet_type,
                    pet.breed,
                    pet.age,
                    f"{pet.weight:.1f}",
                    pet.owner_id,
                ),
            )

    def _refresh_appointment_tree(self) -> None:
        """Reload all appointments into the Appointments Treeview."""
        for row in self.apt_tree.get_children():
            self.apt_tree.delete(row)

        for apt in self.db.get_all_appointments():
            self.apt_tree.insert(
                "",
                tk.END,
                iid=apt.appointment_id,
                values=(
                    apt.appointment_id,
                    apt.date,
                    apt.time,
                    f"{apt.pet.name} ({apt.pet.pet_type})",
                    apt.owner.name,
                    apt.reason,
                    apt.status.value,
                ),
            )

    def _refresh_all_owner_dropdowns(self) -> None:
        """Synchronize owner comboboxes across Tab 1 and Tab 2 with database state."""
        owners = self.db.get_all_owners()
        owner_options = [f"{o.owner_id} - {o.name}" for o in owners]

        # 1. Update Tab 1 Pet Registration Owner Combobox
        current_pet_owner = self.pet_owner_combobox.get().strip()
        self.pet_owner_combobox["values"] = owner_options
        if owner_options:
            if current_pet_owner in owner_options:
                self.pet_owner_combobox.set(current_pet_owner)
            else:
                self.pet_owner_combobox.current(0)
        else:
            self.pet_owner_combobox.set("")

        # 2. Update Tab 2 Appointment Booking Owner Combobox
        current_apt_owner = self.apt_owner_combobox.get().strip()
        self.apt_owner_combobox["values"] = owner_options
        if owner_options:
            if current_apt_owner in owner_options:
                self.apt_owner_combobox.set(current_apt_owner)
            else:
                self.apt_owner_combobox.current(0)
            self._on_apt_owner_selected()
        else:
            self.apt_owner_combobox.set("")
            self.apt_pet_combobox["values"] = []
            self.apt_pet_combobox.set("")
            self.lbl_pet_hint.config(text="No owners registered yet", foreground="gray")

    def _get_selected_combobox_id(self, combobox: ttk.Combobox) -> Optional[str]:
        """Extract primary identifier from a 'ID - Description' combobox string."""
        val = combobox.get().strip()
        if not val or " - " not in val:
            return None
        return val.split(" - ")[0].strip()

    # =========================================================================
    # EVENT HANDLERS & DYNAMIC FILTERING
    # =========================================================================
    def _on_tab_changed(self, event=None) -> None:
        """Handle notebook tab switching to update overview statistics."""
        try:
            current_idx = self.notebook.index(self.notebook.select())
            if current_idx == 2:  # Records Overview Tab
                self._refresh_overview()
        except Exception:
            pass

    def _on_owner_selected(self, event=None) -> None:
        """Pre-select the clicked owner in Tab 1's pet-owner combobox."""
        selected = self.owner_tree.selection()
        if not selected:
            return
        owner_id = selected[0]
        for opt in self.pet_owner_combobox["values"]:
            if opt.startswith(f"{owner_id} -"):
                self.pet_owner_combobox.set(opt)
                break

    def _on_apt_owner_selected(self, event=None) -> None:
        """
        Dynamically filter pet combobox in Tab 2 to show only pets belonging to the selected owner.
        Implements Requirement R2 Tab 2 specification.
        """
        raw_owner = self.apt_owner_combobox.get().strip()
        if not raw_owner:
            self.apt_pet_combobox["values"] = []
            self.apt_pet_combobox.set("")
            self.lbl_pet_hint.config(text="Select an owner first", foreground="gray")
            return

        owner_id = self._get_selected_combobox_id(self.apt_owner_combobox)
        if not owner_id:
            self.apt_pet_combobox["values"] = []
            self.apt_pet_combobox.set("")
            return

        pets = self.db.get_pets_by_owner(owner_id)
        if pets:
            pet_options = [f"{p.pet_id} - {p.name} ({p.pet_type})" for p in pets]
            self.apt_pet_combobox["values"] = pet_options
            self.apt_pet_combobox.current(0)
            self.lbl_pet_hint.config(
                text=f"{len(pets)} pet(s) registered for this owner",
                foreground="#1e7e34"
            )
        else:
            self.apt_pet_combobox["values"] = []
            self.apt_pet_combobox.set("(No pets registered for owner)")
            self.lbl_pet_hint.config(
                text="No pets registered for this owner! Add pet in Tab 1 first.",
                foreground="#d9534f"
            )

    def _on_apt_selected(self, event=None) -> None:
        """Display clinical summary in the preview text area and update action button states."""
        selected = self.apt_tree.selection()
        if not selected:
            return

        apt_id = selected[0]
        apt = self.db.get_appointment(apt_id)
        if not apt:
            return

        self.apt_summary_txt.config(state=tk.NORMAL)
        self.apt_summary_txt.delete("1.0", tk.END)
        self.apt_summary_txt.insert(tk.END, apt.get_summary())
        self.apt_summary_txt.config(state=tk.DISABLED)

        # Contextual button states based on appointment status
        if apt.status == AppointmentStatus.SCHEDULED:
            self.btn_cancel_apt["state"] = tk.NORMAL
            self.btn_complete_apt["state"] = tk.NORMAL
        else:
            self.btn_cancel_apt["state"] = tk.DISABLED
            self.btn_complete_apt["state"] = tk.DISABLED

    def _refresh_overview_stats(self) -> None:
        """Update top summary statistics cards on Tab 3."""
        stats = self.db.get_statistics()
        self.lbl_stat_owners.config(text=str(stats["total_owners"]))
        self.lbl_stat_pets.config(text=str(stats["total_pets"]))

        by_type = stats.get("pets_by_type", {})
        type_str = f"Dog: {by_type.get('Dog', 0)} | Cat: {by_type.get('Cat', 0)} | Bird: {by_type.get('Bird', 0)} | Rabbit: {by_type.get('Rabbit', 0)}"
        self.lbl_stat_pets_detail.config(text=type_str)

        self.lbl_stat_apts.config(text=str(stats["total_appointments"]))

        by_status = stats.get("appointments_by_status", {})
        sched = by_status.get("Scheduled", 0)
        comp = by_status.get("Completed", 0)
        canc = by_status.get("Cancelled", 0)
        self.lbl_stat_status.config(text=f"{sched} Scheduled")
        self.lbl_stat_status_detail.config(text=f"Sched: {sched} | Comp: {comp} | Canc: {canc}")

    def _refresh_overview_directory(self) -> None:
        """Rebuild master clinical hierarchy on Tab 3."""
        selected_node = None
        current_selection = self.overview_tree.selection()
        if current_selection:
            selected_node = current_selection[0]

        for item in self.overview_tree.get_children():
            self.overview_tree.delete(item)

        # Global Views
        node_global = self.overview_tree.insert("", tk.END, "cat_global", text="Clinic System Reports", open=True)
        self.overview_tree.insert(node_global, tk.END, "view_full_dossier", text="★ Comprehensive Clinic Dossier")
        self.overview_tree.insert(node_global, tk.END, "view_all_owners", text="• All Registered Owners")
        self.overview_tree.insert(node_global, tk.END, "view_all_pets", text="• All Patient Pets")
        self.overview_tree.insert(node_global, tk.END, "view_all_apts", text="• All Scheduled Appointments")

        # Owners Node
        node_owners = self.overview_tree.insert("", tk.END, "cat_owners", text="Registered Owners", open=True)
        for owner in self.db.get_all_owners():
            self.overview_tree.insert(node_owners, tk.END, f"own_{owner.owner_id}", text=f"{owner.owner_id}: {owner.name}")

        # Pets Node
        node_pets = self.overview_tree.insert("", tk.END, "cat_pets", text="Patient Pets", open=True)
        for pet in self.db.get_all_pets():
            self.overview_tree.insert(node_pets, tk.END, f"pet_{pet.pet_id}", text=f"{pet.pet_id}: {pet.name} ({pet.pet_type})")

        # Appointments Node
        node_apts = self.overview_tree.insert("", tk.END, "cat_apts", text="Appointments", open=True)
        for apt in self.db.get_all_appointments():
            self.overview_tree.insert(node_apts, tk.END, f"apt_{apt.appointment_id}", text=f"{apt.appointment_id}: {apt.pet.name} ({apt.status.value})")

        # Preserve selection or default to full dossier
        if selected_node and self.overview_tree.exists(selected_node):
            self.overview_tree.selection_set(selected_node)
        else:
            self.overview_tree.selection_set("view_full_dossier")
        self._on_overview_item_selected()

    def _on_overview_item_selected(self, event=None) -> None:
        """Render clinical dossier detail corresponding to the selected directory item."""
        selected = self.overview_tree.selection()
        if not selected:
            return

        item_id = selected[0]
        if item_id in ("cat_global", "cat_owners", "cat_pets", "cat_apts", "view_full_dossier"):
            self._display_dossier_text(self._generate_full_dossier())
        elif item_id == "view_all_owners":
            self._display_dossier_text(self._generate_owners_report())
        elif item_id == "view_all_pets":
            self._display_dossier_text(self._generate_pets_report())
        elif item_id == "view_all_apts":
            self._display_dossier_text(self._generate_appointments_report())
        elif item_id.startswith("own_"):
            owner_id = item_id[4:]
            self._display_dossier_text(self._generate_single_owner_dossier(owner_id))
        elif item_id.startswith("pet_"):
            pet_id = item_id[4:]
            self._display_dossier_text(self._generate_single_pet_dossier(pet_id))
        elif item_id.startswith("apt_"):
            apt_id = item_id[4:]
            self._display_dossier_text(self._generate_single_apt_dossier(apt_id))

    def _display_dossier_text(self, text: str) -> None:
        """Render string into the monospace dossier Text widget."""
        self.dossier_txt.config(state=tk.NORMAL)
        self.dossier_txt.delete("1.0", tk.END)
        self.dossier_txt.insert(tk.END, text)
        self.dossier_txt.config(state=tk.DISABLED)

    # =========================================================================
    # ACTION HANDLERS: Form Processing & Business Logic
    # =========================================================================
    def _add_owner(self) -> None:
        """Handle registration of a new Owner from Tab 1 form."""
        owner_id = self.ent_owner_id.get().strip()
        name = self.ent_owner_name.get().strip()
        phone = self.ent_owner_phone.get().strip()

        if not owner_id or not name or not phone:
            self._show_warning("Incomplete Form", "Please fill in all owner fields.")
            return

        try:
            owner = Owner(owner_id=owner_id, name=name, contact_number=phone)
            self.db.add_owner(owner)
        except (ValueError, TypeError) as err:
            self._show_error("Owner Registration Error", str(err))
            return

        self.owner_counter += 1
        self.ent_owner_name.delete(0, tk.END)
        self.ent_owner_phone.delete(0, tk.END)
        self.ent_owner_id.delete(0, tk.END)

        self._refresh_all_views()
        self._show_info(
            "Owner Registered", f"Owner '{name}' ({owner_id}) successfully registered!"
        )

    def _add_pet(self) -> None:
        """Handle registration of a new Pet from Tab 1 form via PetFactory."""
        pet_id = self.ent_pet_id.get().strip()
        name = self.ent_pet_name.get().strip()
        pet_type = self.cmb_pet_type.get().strip()
        breed = self.ent_pet_breed.get().strip()
        age_val = self.ent_pet_age.get().strip()
        weight_val = self.ent_pet_weight.get().strip()
        raw_owner = self.pet_owner_combobox.get().strip()

        if not pet_id or not name or not breed or not age_val or not weight_val or not raw_owner:
            self._show_warning("Incomplete Form", "Please fill in all pet fields.")
            return

        owner_id = self._get_selected_combobox_id(self.pet_owner_combobox)
        if not owner_id:
            self._show_warning("Invalid Owner", "Please select a registered owner.")
            return

        try:
            pet = PetFactory.create_pet(
                pet_id=pet_id,
                name=name,
                pet_type=pet_type,
                breed=breed,
                age=age_val,
                weight=weight_val,
                owner_id=owner_id,
            )
            self.db.add_pet(pet)
        except (ValueError, TypeError) as err:
            self._show_error("Pet Registration Error", str(err))
            return

        self.pet_counter += 1
        self.ent_pet_name.delete(0, tk.END)
        self.ent_pet_breed.delete(0, tk.END)
        self.ent_pet_weight.delete(0, tk.END)
        self.ent_pet_age.delete(0, tk.END)
        self.ent_pet_age.insert(0, "1")
        self.ent_pet_id.delete(0, tk.END)

        self._refresh_all_views()
        self._show_info(
            "Pet Registered", f"Pet '{name}' ({pet_id}) successfully registered!"
        )

    def _schedule_appointment(self) -> None:
        """Handle booking of a new Appointment from Tab 2 form."""
        apt_id = self.ent_apt_id.get().strip()
        raw_owner = self.apt_owner_combobox.get().strip()
        raw_pet = self.apt_pet_combobox.get().strip()
        date = self.ent_apt_date.get().strip()
        time = self.cmb_apt_time.get().strip()
        reason = self.ent_apt_reason.get().strip()

        if not apt_id or not raw_owner or not raw_pet or not date or not time or not reason:
            self._show_warning("Incomplete Form", "Please fill in all appointment fields.")
            return

        if raw_pet.startswith("("):
            self._show_error(
                "No Pet Available", "The selected owner does not have any registered pets."
            )
            return

        owner_id = self._get_selected_combobox_id(self.apt_owner_combobox)
        pet_id = self._get_selected_combobox_id(self.apt_pet_combobox)

        if not owner_id or not pet_id:
            self._show_error("Error", "Please select both a valid owner and pet.")
            return

        owner = self.db.get_owner(owner_id)
        pet = self.db.get_pet(pet_id)

        if not owner or not pet:
            self._show_error("Error", "Referenced pet or owner not found in database.")
            return

        try:
            appointment = Appointment(
                appointment_id=apt_id,
                pet=pet,
                owner=owner,
                date=date,
                time=time,
                reason=reason,
                status=AppointmentStatus.SCHEDULED,
            )
            self.db.schedule_appointment(appointment)
        except (ValueError, TypeError) as err:
            self._show_error("Appointment Scheduling Error", str(err))
            return

        self.apt_counter += 1
        self.ent_apt_reason.delete(0, tk.END)
        self.ent_apt_id.delete(0, tk.END)

        self._refresh_all_views()
        self._show_info(
            "Appointment Scheduled",
            f"Appointment {apt_id} for {pet.name} successfully scheduled!",
        )

    def _complete_appointment(self) -> None:
        """Mark the selected appointment in Tab 2 as COMPLETED."""
        selected = self.apt_tree.selection()
        if not selected:
            self._show_warning("Selection Required", "Please select an appointment to mark completed.")
            return

        apt_id = selected[0]
        try:
            success = self.db.complete_appointment(apt_id)
            if not success:
                self._show_error("Error", f"Appointment {apt_id} not found.")
                return
        except ValueError as err:
            self._show_error("Action Denied", str(err))
            return

        self._refresh_all_views()
        if self.apt_tree.exists(apt_id):
            self.apt_tree.selection_set(apt_id)
            self._on_apt_selected()
        self._show_info("Success", f"Appointment {apt_id} marked as COMPLETED.")

    def _cancel_appointment(self) -> None:
        """Cancel the selected appointment in Tab 2."""
        selected = self.apt_tree.selection()
        if not selected:
            self._show_warning("Selection Required", "Please select an appointment to cancel.")
            return

        apt_id = selected[0]
        confirm = self._confirm(
            "Confirm Cancellation", f"Are you sure you want to cancel appointment {apt_id}?"
        )
        if not confirm:
            return

        try:
            success = self.db.cancel_appointment(apt_id)
            if not success:
                self._show_error("Error", f"Appointment {apt_id} not found.")
                return
        except ValueError as err:
            self._show_error("Action Denied", str(err))
            return

        self._refresh_all_views()
        if self.apt_tree.exists(apt_id):
            self.apt_tree.selection_set(apt_id)
            self._on_apt_selected()
        self._show_info("Cancelled", f"Appointment {apt_id} has been CANCELLED.")

    # =========================================================================
    # MONOSPACE REPORT GENERATORS (Tab 3)
    # =========================================================================
    def _generate_full_dossier(self) -> str:
        """Generate full ASCII clinical audit report across all clinic entities."""
        stats = self.db.get_statistics()
        lines: List[str] = [
            "=" * 82,
            "                   PET CLINIC MANAGEMENT SYSTEM - CLINICAL DOSSIER",
            "=" * 82,
            "Clinic Architecture: Lab4 Model-View Architecture (Singleton Database)",
            f"Total Owners: {stats['total_owners']} | Total Patients: {stats['total_pets']} | Total Appointments: {stats['total_appointments']}",
            "-" * 82,
            "",
            "1. REGISTERED CLIENT OWNERS",
            "-" * 82,
        ]

        owners = self.db.get_all_owners()
        if not owners:
            lines.append("  (No registered owners)")
        for o in owners:
            pets = self.db.get_pets_by_owner(o.owner_id)
            lines.append(f"  • [{o.owner_id}] {o.name:<22} Contact: {o.contact_number:<14} Pets: {len(pets)}")

        lines.extend(["", "2. REGISTERED PATIENTS (SPECIES CATALOG)", "-" * 82])
        pets = self.db.get_all_pets()
        if not pets:
            lines.append("  (No registered pets)")
        for p in pets:
            lines.append(
                f"  • [{p.pet_id}] {p.name:<12} {p.pet_type:<8} Breed: {p.breed:<18} "
                f"Age: {p.age:>2} yrs  Weight: {p.weight:>5.1f} kg  Owner: {p.owner_id}"
            )

        lines.extend(["", "3. APPOINTMENT LOG & CLINICAL ENCOUNTERS", "-" * 82])
        apts = self.db.get_all_appointments()
        if not apts:
            lines.append("  (No scheduled appointments)")
        for a in apts:
            lines.append(
                f"  • [{a.appointment_id}] {a.date} at {a.time:<9} | Status: {a.status.value:<9} | "
                f"Pet: {a.pet.name} ({a.pet.pet_type}) | Owner: {a.owner.name}"
            )
            lines.append(f"    Reason: {a.reason}")

        lines.extend(["", "=" * 82, "                          END OF CLINICAL REPORT", "=" * 82])
        return "\n".join(lines)

    def _generate_owners_report(self) -> str:
        """Generate text report focused on registered owners."""
        owners = self.db.get_all_owners()
        lines = [
            "=" * 72,
            "                        REGISTERED OWNERS DIRECTORY",
            "=" * 72,
        ]
        if not owners:
            lines.append("No registered owners.")
        for o in owners:
            pets = self.db.get_pets_by_owner(o.owner_id)
            lines.append(f"ID:      {o.owner_id}")
            lines.append(f"Name:    {o.name}")
            lines.append(f"Contact: {o.contact_number}")
            lines.append(f"Pets ({len(pets)}):")
            for p in pets:
                lines.append(f"   - {p.name} ({p.pet_type} - {p.breed}, {p.age} yrs)")
            lines.append("-" * 72)
        return "\n".join(lines)

    def _generate_pets_report(self) -> str:
        """Generate text report focused on patient pets."""
        pets = self.db.get_all_pets()
        lines = [
            "=" * 72,
            "                        PATIENT PETS DIRECTORY",
            "=" * 72,
        ]
        if not pets:
            lines.append("No registered pets.")
        for p in pets:
            owner = self.db.get_owner(p.owner_id)
            owner_name = owner.name if owner else "Unknown"
            lines.append(f"ID:      {p.pet_id}")
            lines.append(f"Name:    {p.name}")
            lines.append(f"Species: {p.pet_type} | Breed: {p.breed}")
            lines.append(f"Vitals:  Age: {p.age} years | Weight: {p.weight:.1f} kg")
            lines.append(f"Owner:   {owner_name} ({p.owner_id})")
            lines.append("-" * 72)
        return "\n".join(lines)

    def _generate_appointments_report(self) -> str:
        """Generate text report listing all appointments."""
        apts = self.db.get_all_appointments()
        lines = [
            "=" * 72,
            "                     APPOINTMENTS SCHEDULE & AUDIT",
            "=" * 72,
        ]
        if not apts:
            lines.append("No appointments recorded.")
        for a in apts:
            lines.append(a.get_summary())
            lines.append("-" * 72)
        return "\n".join(lines)

    def _generate_single_owner_dossier(self, owner_id: str) -> str:
        """Generate individual owner clinical dossier."""
        owner = self.db.get_owner(owner_id)
        if not owner:
            return f"Owner ID '{owner_id}' not found."
        pets = self.db.get_pets_by_owner(owner_id)
        apts = self.db.get_appointments_by_owner(owner_id)

        lines = [
            "=" * 72,
            f"               CLIENT DOSSIER: {owner.name} ({owner.owner_id})",
            "=" * 72,
            f"Client Name:       {owner.name}",
            f"Contact Telephone: {owner.contact_number}",
            f"Registered Pets:   {len(pets)}",
            "-" * 72,
            "REGISTERED PATIENTS:",
        ]
        if not pets:
            lines.append("  (No pets registered for this owner)")
        for p in pets:
            lines.append(f"  • {p.name} [{p.pet_id}] - {p.pet_type} ({p.breed}), Age {p.age} yrs, {p.weight:.1f} kg")
        lines.append("-" * 72)
        lines.append("APPOINTMENT HISTORY:")
        if not apts:
            lines.append("  (No appointment history)")
        for a in apts:
            lines.append(f"  • [{a.appointment_id}] {a.date} at {a.time} - {a.pet.name} [{a.status.value}]")
            lines.append(f"    Reason: {a.reason}")
        lines.append("=" * 72)
        return "\n".join(lines)

    def _generate_single_pet_dossier(self, pet_id: str) -> str:
        """Generate individual pet patient dossier."""
        pet = self.db.get_pet(pet_id)
        if not pet:
            return f"Pet ID '{pet_id}' not found."
        owner = self.db.get_owner(pet.owner_id)
        apts = self.db.get_appointments_by_pet(pet_id)

        lines = [
            "=" * 72,
            f"               PATIENT MEDICAL DOSSIER: {pet.name} ({pet.pet_id})",
            "=" * 72,
            f"Patient Name:      {pet.name}",
            f"Species:           {pet.pet_type}",
            f"Breed:             {pet.breed}",
            f"Age:               {pet.age} years",
            f"Weight:            {pet.weight:.1f} kg",
            f"Owner:             {owner.name if owner else 'Unknown'} ({pet.owner_id})",
            f"Owner Contact:     {owner.contact_number if owner else 'N/A'}",
            "-" * 72,
            "CLINICAL VISITS & APPOINTMENTS:",
        ]
        if not apts:
            lines.append("  (No clinical visits recorded)")
        for a in apts:
            lines.append(f"  • [{a.appointment_id}] {a.date} at {a.time} | Status: {a.status.value}")
            lines.append(f"    Clinical Note: {a.reason}")
        lines.append("=" * 72)
        return "\n".join(lines)

    def _generate_single_apt_dossier(self, apt_id: str) -> str:
        """Generate single appointment encounter sheet."""
        apt = self.db.get_appointment(apt_id)
        if not apt:
            return f"Appointment ID '{apt_id}' not found."
        return f"{'=' * 72}\n                   APPOINTMENT ENCOUNTER SHEET\n{'=' * 72}\n{apt.get_summary()}\n{'=' * 72}"
