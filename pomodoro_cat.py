"""
=============================================================================
         🥑🐾 PIXEL MASCOT POMODORO TIMER MED SKINS & LYD 🐾🥑
=============================================================================
Et morsomt og lærerikt skrivebords-kjæledyr og Pomodoro-program for far og sønn!
Utviklet av OneUp82: https://github.com/OneUp82

Nye oppdateringer:
1. ℹ️ "Om prosjektet"-dialog med direkte lenke til OneUp82 på GitHub!
2. 📏 Definerte størrelser i høyreklikk-menyen (Liten, Medium, Stor, Ekstra Stor).
3. 👁️ Krystallklar tekst med mørk skjermflate og fallskygge for maksimal kontrast.
4. 🥑 10 søte skins med matchende lyder og risteeffekt når tiden er ute.
=============================================================================
"""

import os
import sys
import math
import webbrowser
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Importer vår lokale generator for skins og lyder
import generate_assets

# Lydbibliotek (Pygame med fallback til Windows winsound)
try:
    import pygame
    PYGAME_TILGJENGELIG = True
    pygame.mixer.init()
except Exception:
    PYGAME_TILGJENGELIG = False

if sys.platform == "win32":
    import winsound


# =============================================================================
# DEFINISJON AV SKINS OG STØRRELSER
# =============================================================================

SKINS = [
    {"id": "avocado",    "navn": "🥑 Avokado (Avo-venn)", "beskrivelse": "Lille Avo med spire og mørk stein"},
    {"id": "cat",        "navn": "🐱 Katt (Pus)",         "beskrivelse": "Oransje pusekatt som mjauer"},
    {"id": "dog",        "navn": "🐶 Hund (Valp)",        "beskrivelse": "Glad valp som bjeffer muntert"},
    {"id": "frog",       "navn": "🐸 Frosk (Kvekk)",      "beskrivelse": "Liten grønn frosk som kvekker"},
    {"id": "duck",       "navn": "🦆 And (Kvakk)",        "beskrivelse": "Gul andunge med oransje nebb"},
    {"id": "panda",      "navn": "🐼 Panda (Bambus)",     "beskrivelse": "Søt panda som knasker bambus"},
    {"id": "robot",      "navn": "🤖 Robot (Beep)",       "beskrivelse": "Retro 8-bit arkade-robot"},
    {"id": "ghost",      "navn": "👻 Spøkelse (Bø)",      "beskrivelse": "Koselig, snilt lite spøkelse"},
    {"id": "strawberry", "navn": "🍓 Jordbær (Bær)",      "beskrivelse": "Rødt og søtt sommerbær"},
    {"id": "bear",       "navn": "🐻 Bjørn (Teddy)",      "beskrivelse": "Kosebjørn med sjokolademage"},
]

STORRELSER = [
    {"id": "liten",   "navn": "▫️ Liten (224 x 288)",         "skala": 8},
    {"id": "medium",  "navn": "◽ Medium (280 x 360) - Standard", "skala": 10},
    {"id": "stor",    "navn": "◻️ Stor (336 x 432)",          "skala": 12},
    {"id": "ekstra",  "navn": "⬛ Ekstra Stor (392 x 504)",    "skala": 14},
]


def spill_skin_lyd(skin_id):
    """Spiller av den unike lyden som hører til det valgte skinnet."""
    filsti = os.path.join("skins", f"{skin_id}.wav")

    if PYGAME_TILGJENGELIG:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if os.path.exists(filsti):
                lyd = pygame.mixer.Sound(filsti)
                lyd.set_volume(0.85)
                lyd.play()
                return
        except Exception as e:
            print(f"[Lyd-info] Pygame feilet: {e}")

    if sys.platform == "win32":
        try:
            if os.path.exists(filsti):
                winsound.PlaySound(filsti, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            else:
                winsound.MessageBeep()
                return
        except Exception:
            pass

    print("\a")


# =============================================================================
# HOVEDAPP: DEN SØTE FLYTENDE POMODORO-MASKOTEN
# =============================================================================

class PomodoroMascot(tk.Tk):
    """
    Hovedvinduet for maskoten.
    Kjører uten vindusramme (overrideredirect) med transparent bakgrunn.
    """

    def __init__(self):
        super().__init__()

        self.verifiser_og_lag_filer()

        # Vindusinnstillinger
        self.title("Pomodoro Maskot - av OneUp82")
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)

        # Transparent fargenøkkel for Windows
        self.trans_farge = "#010203"
        self.wm_attributes("-transparentcolor", self.trans_farge)
        self.configure(bg=self.trans_farge)

        # --- Størrelse og Skala ---
        self.gjeldende_skala = 10
        self.bredde = 28 * self.gjeldende_skala
        self.hoyde = 36 * self.gjeldende_skala

        # Plassering på skjermen (nede til høyre)
        skjerm_b = self.winfo_screenwidth()
        skjerm_h = self.winfo_screenheight()
        start_x = max(50, skjerm_b - self.bredde - 60)
        start_y = max(50, skjerm_h - self.hoyde - 100)
        self.geometry(f"{self.bredde}x{self.hoyde}+{start_x}+{start_y}")

        # --- Timer- og tilstandsvariabler ---
        self.aktivt_skin = "avocado"
        self.total_sekunder = 25 * 60
        self.gjenstaende_sekunder = self.total_sekunder
        self.er_aktiv = False
        self.oppgave_tekst = "fokus"
        self.timer_id = None
        self.alltid_overst = True

        # --- Musedrag-variabler ---
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._win_orig_x = 0
        self._win_orig_y = 0
        self._har_dradd = False

        # Bygg grensesnittet
        self.opprett_lerret()
        self.last_skin_bilde(self.aktivt_skin)
        self.opprett_hoyreklikk_meny()
        self.tegn_skjerm()

    def verifiser_og_lag_filer(self):
        """Sørger for at alle bilder og lyder er opprettet."""
        os.makedirs("skins", exist_ok=True)
        mangler = False
        for s in SKINS:
            if not os.path.exists(f"skins/{s['id']}.png") or not os.path.exists(f"skins/{s['id']}.wav"):
                mangler = True
                break
        if mangler:
            print("[Info] Genererer skins og lyder...")
            generate_assets.bygg_alle_skins()
            generate_assets.bygg_alle_lyder()

    # =========================================================================
    # LERRET OG TEGNING AV MASKOTEN
    # =========================================================================

    def opprett_lerret(self):
        """Lager Canvas-elementet som maskoten og klokken tegnes på."""
        self.canvas = tk.Canvas(
            self,
            width=self.bredde,
            height=self.hoyde,
            bg=self.trans_farge,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.paa_mus_trykk)
        self.canvas.bind("<B1-Motion>", self.paa_mus_dra)
        self.canvas.bind("<ButtonRelease-1>", self.paa_mus_slipp)
        self.canvas.bind("<Button-3>", self.vis_hoyreklikk_meny)

    def last_skin_bilde(self, skin_id):
        """Laster inn bildet og skalerer det knivskarpt med NEAREST."""
        bilde_sti = os.path.join("skins", f"{skin_id}.png")
        if not os.path.exists(bilde_sti):
            bilde_sti = "cat.png"

        pil_img = Image.open(bilde_sti)
        skalert_img = pil_img.resize((self.bredde, self.hoyde), Image.Resampling.NEAREST)
        self.tk_maskot_bilde = ImageTk.PhotoImage(skalert_img)

    def tegn_tekst_med_skygge(self, x, y, tekst, farge, font, skygge_farge="#000000"):
        """Tegner tekst med mørk fallskygge for maksimal lesbarhet."""
        self.canvas.create_text(x + 1, y + 1, text=tekst, fill=skygge_farge, font=font)
        self.canvas.create_text(x, y, text=tekst, fill=farge, font=font)

    def tegn_skjerm(self):
        """Tegner maskoten, fremdriftsringen og teksten inni magen."""
        self.canvas.delete("all")

        # 1. Tegn maskotbildet
        self.canvas.create_image(self.bredde // 2, self.hoyde // 2, image=self.tk_maskot_bilde)

        # 2. Beregn koordinater ut fra skala
        s = self.gjeldende_skala
        cx = int(14.0 * s)
        cy = int(24.2 * s)
        r = int(5.8 * s)

        # 3. Mørk skjermflate inni magen (sikrer 100% kontrast uansett skin!)
        self.canvas.create_oval(
            cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1,
            fill="#1E1926",
            outline=""
        )

        # 4. Bakgrunnsring for fremdriftslinjen
        ring_bredde = max(3, int(0.35 * s))
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline="#353044",
            width=ring_bredde
        )

        # 5. Fremdriftsbue
        if self.total_sekunder > 0:
            andel = max(0.0, min(1.0, self.gjenstaende_sekunder / self.total_sekunder))
            vinkel_spenn = - (andel * 359.9)
            farge_bue = "#00F5A0" if self.er_aktiv else "#FFD166"
            if self.gjenstaende_sekunder <= 0:
                farge_bue = "#FF4B72"

            self.canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=90,
                extent=vinkel_spenn,
                outline=farge_bue,
                width=ring_bredde,
                style="arc"
            )

        # 6. Skriftstørrelser
        font_klokke = ("Consolas", int(1.75 * s), "bold")
        font_stortall = ("Segoe UI", int(2.1 * s), "bold")
        font_tekst = ("Segoe UI", max(8, int(0.9 * s)), "bold")
        font_knapp = ("Segoe UI", max(8, int(0.95 * s)), "bold")

        # 7. Tegn innholdet inni magen
        if self.gjenstaende_sekunder <= 0:
            self.tegn_tekst_med_skygge(cx, cy - int(1.3 * s), "00:00", "#FF4B72", font_klokke)
            self.tegn_tekst_med_skygge(cx, cy + int(0.2 * s), "FERDIG!", "#FFD166", font_tekst)
            self.canvas.create_line(cx - int(2.2 * s), cy + int(1.4 * s), cx + int(2.2 * s), cy + int(1.4 * s), fill="#4A455A", width=max(1, int(0.15 * s)))
            self.tegn_tekst_med_skygge(cx, cy + int(2.5 * s), "🔄 RESET", "#00F5A0", font_knapp)

        elif self.er_aktiv:
            m = self.gjenstaende_sekunder // 60
            sec = self.gjenstaende_sekunder % 60
            tid_tekst = f"{m:02d}:{sec:02d}"

            self.tegn_tekst_med_skygge(cx, cy - int(1.4 * s), tid_tekst, "#FFFFFF", font_klokke)
            self.tegn_tekst_med_skygge(cx, cy + int(0.1 * s), f"({self.oppgave_tekst})", "#FFD166", font_tekst)
            self.canvas.create_line(cx - int(2.2 * s), cy + int(1.3 * s), cx + int(2.2 * s), cy + int(1.3 * s), fill="#4A455A", width=max(1, int(0.15 * s)))
            self.tegn_tekst_med_skygge(cx, cy + int(2.4 * s), "⏸ PAUSE", "#00F5A0", font_knapp)

        else:
            minutter = max(1, math.ceil(self.gjenstaende_sekunder / 60))
            self.tegn_tekst_med_skygge(cx, cy - int(1.6 * s), str(minutter), "#FFFFFF", font_stortall)
            self.tegn_tekst_med_skygge(cx, cy - int(0.1 * s), "MIN", "#FFD166", font_tekst)
            self.tegn_tekst_med_skygge(cx, cy + int(1.0 * s), f"({self.oppgave_tekst})", "#DDDDDD", font_tekst)
            self.canvas.create_line(cx - int(2.2 * s), cy + int(1.8 * s), cx + int(2.2 * s), cy + int(1.8 * s), fill="#4A455A", width=max(1, int(0.15 * s)))
            start_tekst = "✔ START" if (self.gjenstaende_sekunder == self.total_sekunder) else "▶ FORTSETT"
            self.tegn_tekst_med_skygge(cx, cy + int(2.7 * s), start_tekst, "#00F5A0", font_knapp)

    # =========================================================================
    # MUS-INTERAKSJON: DRAING OG KLIKKING
    # =========================================================================

    def paa_mus_trykk(self, event):
        """Registrerer startposisjon for draing."""
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._win_orig_x = self.winfo_x()
        self._win_orig_y = self.winfo_y()
        self._har_dradd = False

    def paa_mus_dra(self, event):
        """Flytter vinduet etter musen hvis den dras."""
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        if abs(dx) > 3 or abs(dy) > 3:
            self._har_dradd = True
            ny_x = self._win_orig_x + dx
            ny_y = self._win_orig_y + dy
            self.geometry(f"+{ny_x}+{ny_y}")

    def paa_mus_slipp(self, event):
        """Håndterer klikk (hvis brukeren ikke dro)."""
        if not self._har_dradd:
            s = self.gjeldende_skala
            cx = int(14.0 * s)
            cy = int(24.2 * s)
            r = int(5.8 * s)
            distanse = math.hypot(event.x - cx, event.y - cy)
            if distanse <= r + int(1.5 * s):
                self.veksle_start_pause()
            else:
                spill_skin_lyd(self.aktivt_skin)

    # =========================================================================
    # HØYREKLIKK-MENY OG STØRRELSESVELGER
    # =========================================================================

    def opprett_hoyreklikk_meny(self):
        """Lager den moderne høyreklikk-menyen med størrelsesvelger, skins og om-dialog."""
        self.meny = tk.Menu(
            self,
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#242432",
            fg="#FFFFFF",
            activebackground="#00F5A0",
            activeforeground="#000000"
        )

        # 1. Undermeny for Skins
        self.skin_meny = tk.Menu(
            self.meny,
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#242432",
            fg="#FFFFFF",
            activebackground="#00F5A0",
            activeforeground="#000000"
        )
        for s in SKINS:
            prefiks = "✓ " if (s["id"] == self.aktivt_skin) else "   "
            self.skin_meny.add_command(
                label=f"{prefiks}{s['navn']}",
                command=lambda sid=s["id"]: self.bytt_skin(sid)
            )

        # 2. Undermeny for Størrelser
        self.storrelse_meny = tk.Menu(
            self.meny,
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#242432",
            fg="#FFFFFF",
            activebackground="#00F5A0",
            activeforeground="#000000"
        )
        for st in STORRELSER:
            prefiks = "✓ " if (st["skala"] == self.gjeldende_skala) else "   "
            self.storrelse_meny.add_command(
                label=f"{prefiks}{st['navn']}",
                command=lambda skala=st["skala"]: self.sett_storrelse(skala)
            )

        # 3. Undermeny for Hurtigvalg tid
        self.hurtig_meny = tk.Menu(
            self.meny,
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#242432",
            fg="#FFFFFF",
            activebackground="#00F5A0",
            activeforeground="#000000"
        )
        self.hurtig_meny.add_command(label="🍅 25 min (Fokusøkt)", command=lambda: self.sett_tid(0, 25, 0))
        self.hurtig_meny.add_command(label="☕ 5 min (Kort pause)", command=lambda: self.sett_tid(0, 5, 0))
        self.hurtig_meny.add_command(label="🌟 15 min (Lang pause)", command=lambda: self.sett_tid(0, 15, 0))
        self.hurtig_meny.add_command(label="⚡ 1 min (Rask test)", command=lambda: self.sett_tid(0, 1, 0))

        # Bygg hovedmenyen
        self.meny.add_cascade(label="🎨 Bytt Skin...", menu=self.skin_meny)
        self.meny.add_cascade(label="📏 Størrelse...", menu=self.storrelse_meny)
        self.meny.add_cascade(label="⏱️ Hurtigvalg tid...", menu=self.hurtig_meny)
        self.meny.add_command(label="⚙️ Still inn tid & oppgave...", command=self.apne_tidsinnstilling)
        self.meny.add_separator()
        self.meny.add_command(label="🔊 Test skin-lyd", command=lambda: spill_skin_lyd(self.aktivt_skin))
        self.meny.add_command(label="📳 Test risting", command=self.start_risting)
        self.meny.add_command(label="ℹ️ Om prosjektet...", command=self.apne_om_dialog)
        self.meny.add_command(label="📌 Fest alltid øverst (På/Av)", command=self.veksle_alltid_overst)
        self.meny.add_command(label="🔄 Nullstill (Reset)", command=self.nullstill_timer)
        self.meny.add_separator()
        self.meny.add_command(label="❌ Avslutt", command=self.destroy)

    def vis_hoyreklikk_meny(self, event):
        """Viser popup-menyen ved musepekeren."""
        try:
            self.opprett_hoyreklikk_meny()
            self.meny.tk_popup(event.x_root, event.y_root)
        finally:
            self.meny.grab_release()

    def sett_storrelse(self, ny_skala):
        """Endrer størrelsen på maskoten og skalerer om grafikk og skrifttyper."""
        gammel_b = self.bredde
        gammel_h = self.hoyde

        self.gjeldende_skala = ny_skala
        self.bredde = 28 * ny_skala
        self.hoyde = 36 * ny_skala

        ny_x = self.winfo_x() - (self.bredde - gammel_b) // 2
        ny_y = self.winfo_y() - (self.hoyde - gammel_h) // 2

        skjerm_b = self.winfo_screenwidth()
        skjerm_h = self.winfo_screenheight()
        ny_x = max(10, min(skjerm_b - self.bredde - 10, ny_x))
        ny_y = max(10, min(skjerm_h - self.hoyde - 40, ny_y))

        self.geometry(f"{self.bredde}x{self.hoyde}+{ny_x}+{ny_y}")
        self.canvas.configure(width=self.bredde, height=self.hoyde)

        self.last_skin_bilde(self.aktivt_skin)
        self.tegn_skjerm()

    def bytt_skin(self, nytt_skin_id):
        """Bytter aktivt skin, oppdaterer grafikken og spiller av lyden."""
        self.aktivt_skin = nytt_skin_id
        self.last_skin_bilde(nytt_skin_id)
        self.tegn_skjerm()
        spill_skin_lyd(nytt_skin_id)

    def veksle_alltid_overst(self):
        """Slår på eller av om maskoten skal flyte over andre vinduer."""
        self.alltid_overst = not self.alltid_overst
        self.wm_attributes("-topmost", self.alltid_overst)

    # =========================================================================
    # TIMER-KONTROLL OG RISTE-EFFEKT
    # =========================================================================

    def veksle_start_pause(self):
        """Starter eller pauser timeren."""
        if self.gjenstaende_sekunder <= 0:
            self.nullstill_timer()
            return

        if self.er_aktiv:
            self.er_aktiv = False
            if self.timer_id is not None:
                self.after_cancel(self.timer_id)
                self.timer_id = None
        else:
            self.er_aktiv = True
            self.tell_ned()

        self.tegn_skjerm()

    def sett_tid(self, timer, minutter, sekunder):
        """Setter ny tid og nullstiller."""
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.er_aktiv = False

        self.total_sekunder = (timer * 3600) + (minutter * 60) + sekunder
        self.gjenstaende_sekunder = self.total_sekunder
        self.tegn_skjerm()

    def nullstill_timer(self):
        """Setter timeren tilbake til starttiden."""
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.er_aktiv = False
        self.gjenstaende_sekunder = self.total_sekunder
        self.tegn_skjerm()

    def tell_ned(self):
        """Løkken som teller ned hvert sekund med self.after()."""
        if not self.er_aktiv:
            return

        if self.gjenstaende_sekunder <= 0:
            self.er_aktiv = False
            self.timer_id = None
            self.tegn_skjerm()
            self.timer_ferdig()
            return

        self.gjenstaende_sekunder -= 1
        self.tegn_skjerm()
        self.timer_id = self.after(1000, self.tell_ned)

    def timer_ferdig(self):
        """Håndterer hva som skjer når timeren når 00:00:00."""
        spill_skin_lyd(self.aktivt_skin)
        self.start_risting()

    def start_risting(self, antall_steg=26, styrke=14):
        """Rister maskoten fram og tilbake når tiden er ute!"""
        orig_x = self.winfo_x()
        orig_y = self.winfo_y()

        def riste_steg(steg):
            if steg <= 0:
                self.geometry(f"+{orig_x}+{orig_y}")
                return

            dempet_styrke = max(2, int(styrke * (steg / antall_steg)))
            dx = dempet_styrke if (steg % 2 == 0) else -dempet_styrke
            dy = (steg % 3 - 1) * (dempet_styrke // 3)

            self.geometry(f"+{orig_x + dx}+{orig_y + dy}")
            self.after(35, lambda: riste_steg(steg - 1))

        riste_steg(antall_steg)

    # =========================================================================
    # DIALOGER: OM PROSJEKTET OG STILL INN TID
    # =========================================================================

    def apne_om_dialog(self):
        """Viser 'Om prosjektet'-vindu med lenke til OneUp82 på GitHub."""
        dialog = tk.Toplevel(self)
        dialog.title("ℹ️ Om Pomodoro Maskot")
        dialog.geometry("340x270")
        dialog.resizable(False, False)
        dialog.configure(bg="#1E1E28")
        dialog.wm_attributes("-topmost", True)

        pos_x = max(20, self.winfo_x() - 40)
        pos_y = max(20, self.winfo_y() - 10)
        dialog.geometry(f"+{pos_x}+{pos_y}")

        tk.Label(
            dialog,
            text="🥑 PIXEL MASCOT POMODORO",
            font=("Segoe UI", 12, "bold"),
            bg="#1E1E28",
            fg="#00F5A0"
        ).pack(pady=(16, 4))

        tk.Label(
            dialog,
            text="Et morsomt og lærerikt\nfar-og-sønn-kodingsprosjekt!",
            font=("Segoe UI", 10),
            bg="#1E1E28",
            fg="#DDDDDD",
            justify="center"
        ).pack(pady=4)

        tk.Label(
            dialog,
            text="Laget med stolthet av OneUp82 👨‍👦",
            font=("Segoe UI", 10, "bold"),
            bg="#1E1E28",
            fg="#FFD166"
        ).pack(pady=6)

        def apne_github():
            webbrowser.open_new("https://github.com/OneUp82")

        tk.Button(
            dialog,
            text="🌐 Besøk OneUp82 på GitHub",
            command=apne_github,
            bg="#00F5A0",
            fg="#000000",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=5,
            relief="flat",
            cursor="hand2"
        ).pack(pady=8)

        tk.Button(
            dialog,
            text="Lukk",
            command=dialog.destroy,
            bg="#3A3A4C",
            fg="#FFFFFF",
            font=("Segoe UI", 9),
            padx=14,
            pady=3,
            relief="flat"
        ).pack(pady=(4, 10))

    def apne_tidsinnstilling(self):
        """Åpner innstillingsvinduet for tid og oppgave med sikker validering."""
        dialog = tk.Toplevel(self)
        dialog.title("⏱️ Still inn tid")
        dialog.geometry("320x330")
        dialog.resizable(False, False)
        dialog.configure(bg="#1E1E28")
        dialog.wm_attributes("-topmost", True)

        pos_x = max(20, self.winfo_x() - 50)
        pos_y = max(20, self.winfo_y() - 20)
        dialog.geometry(f"+{pos_x}+{pos_y}")

        tk.Label(
            dialog,
            text="⏱️ STILL INN TID & OPPGAVE",
            font=("Segoe UI", 12, "bold"),
            bg="#1E1E28",
            fg="#FFD166"
        ).pack(pady=(15, 10))

        ramme = tk.Frame(dialog, bg="#1E1E28")
        ramme.pack(pady=5)

        gjeldende_t = self.total_sekunder // 3600
        gjeldende_m = (self.total_sekunder % 3600) // 60
        gjeldende_s = self.total_sekunder % 60

        tk.Label(ramme, text="Timer", font=("Segoe UI", 9), bg="#1E1E28", fg="#FFFFFF").grid(row=0, column=0, padx=6)
        t_entry = tk.Entry(ramme, width=5, justify="center", font=("Segoe UI", 12), bg="#2B2B3C", fg="#FFFFFF", insertbackground="white")
        t_entry.insert(0, str(gjeldende_t))
        t_entry.grid(row=1, column=0, padx=6, pady=4)

        tk.Label(ramme, text="Minutter", font=("Segoe UI", 9), bg="#1E1E28", fg="#FFFFFF").grid(row=0, column=1, padx=6)
        m_entry = tk.Entry(ramme, width=5, justify="center", font=("Segoe UI", 12), bg="#2B2B3C", fg="#FFFFFF", insertbackground="white")
        m_entry.insert(0, str(gjeldende_m))
        m_entry.grid(row=1, column=1, padx=6, pady=4)

        tk.Label(ramme, text="Sekunder", font=("Segoe UI", 9), bg="#1E1E28", fg="#FFFFFF").grid(row=0, column=2, padx=6)
        s_entry = tk.Entry(ramme, width=5, justify="center", font=("Segoe UI", 12), bg="#2B2B3C", fg="#FFFFFF", insertbackground="white")
        s_entry.insert(0, str(gjeldende_s))
        s_entry.grid(row=1, column=2, padx=6, pady=4)

        tk.Label(dialog, text="Oppgavenavn (vises i magen):", font=("Segoe UI", 9), bg="#1E1E28", fg="#FFFFFF").pack(pady=(10, 2))
        oppgave_entry = tk.Entry(dialog, width=20, justify="center", font=("Segoe UI", 10), bg="#2B2B3C", fg="#FFFFFF", insertbackground="white")
        oppgave_entry.insert(0, self.oppgave_tekst)
        oppgave_entry.pack(pady=2)

        feil_label = tk.Label(dialog, text="", font=("Segoe UI", 8), bg="#1E1E28", fg="#EF476F")
        feil_label.pack(pady=4)

        def lagre():
            t_str = t_entry.get().strip() or "0"
            m_str = m_entry.get().strip() or "0"
            s_str = s_entry.get().strip() or "0"
            oppg = oppgave_entry.get().strip() or "fokus"

            if not (t_str.isdigit() and m_str.isdigit() and s_str.isdigit()):
                feil_label.config(text="⚠️ Skriv inn bare positive hele tall!")
                return

            t = int(t_str)
            m = int(m_str)
            s = int(s_str)

            if t > 24:
                feil_label.config(text="⚠️ Maks 24 timer!")
                return

            totalt = (t * 3600) + (m * 60) + s
            if totalt <= 0:
                feil_label.config(text="⚠️ Tiden må være større enn 0!")
                return

            self.oppgave_tekst = oppg[:10]
            self.sett_tid(t, m, s)
            dialog.destroy()

        knappe_ramme = tk.Frame(dialog, bg="#1E1E28")
        knappe_ramme.pack(pady=10)

        tk.Button(
            knappe_ramme,
            text="✔ Lagre",
            command=lagre,
            bg="#00F5A0",
            fg="#000000",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=4,
            relief="flat"
        ).pack(side="left", padx=6)

        tk.Button(
            knappe_ramme,
            text="✕ Avbryt",
            command=dialog.destroy,
            bg="#3A3A4C",
            fg="#FFFFFF",
            font=("Segoe UI", 9),
            padx=10,
            pady=4,
            relief="flat"
        ).pack(side="left", padx=6)


# =============================================================================
# OPPSTART
# =============================================================================

if __name__ == "__main__":
    app = PomodoroMascot()
    app.mainloop()
