"""
=============================================================================
         🥑🐾 PIXEL MASCOT POMODORO TIMER MED SKINS & LYD 🐾🥑
=============================================================================
Repository: https://github.com/OneUp82/pomodoro
Author:     OneUp82 (https://github.com/OneUp82)
License:    MIT License

OVERSIKT / OVERVIEW / DESCRIPCIÓN:
Dette prosjektet er en lettvekts, rammeløs skrivebords-maskot og Pomodoro-timer
skrevet i Python med Tkinter og Pillow. Maskoten flyter direkte på skrivebordet
uten standard vindusrammer, kan dras med musen, har 10 utskiftbare skins med
tilhørende lydeffekter, og støtter 3 språk (Norsk, Engelsk, Spansk).

ARKITEKTUR OG MODULSTRUKTUR FOR UTVIKLERE / ARCHITECTURE:
1. i18n (Internationalization):
   - 'TRANSLATIONS'-ordboken inneholder all UI-tekst for Norsk ('no'),
     Engelsk ('en') og Spansk ('es').
   - For å legge til et nytt språk (f.eks. Tysk eller Fransk), legg bare til
     en ny språkkode i LANGUAGES og oversett feltene i TRANSLATIONS.
2. Ressursstyring (Asset Management):
   - 'skins/'-mappen inneholder 224x288 RGBA PNG-bilder og WAV-lydfiler for hvert skin.
   - Bildene skaleres tapsfritt med NEAREST-filtrering for ren pixel art.
   - 'generate_assets.py' lager alle standardfiler automatisk hvis de mangler.
3. Brukergrensesnitt (GUI & Rendering):
   - 'PomodoroMascot' arver fra 'tk.Tk'.
   - Bruker '-transparentcolor' på Windows for gjennomsiktig bakgrunn.
   - Lerretet (Canvas) tegner maskoten, en mørk sirkulær skjermflate i magen,
     en sirkulær fremdriftsbue og tekst med fallskygge for maksimal kontrast.
4. Tidsstyring (Timer Engine):
   - Bruker 'after(1000, self.tell_ned)' for en trådsikker, krasjfri nedtellingsløkke.
=============================================================================
"""

import os
import sys
import json
import math
import webbrowser
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Importer lokal generator som lager pikselskins og lyder hvis mappen er tom
import generate_assets

# Lydmotor: Bruker Pygame hvis installert, med fallback til Windows winsound
try:
    import pygame
    PYGAME_TILGJENGELIG = True
    pygame.mixer.init()
except Exception:
    PYGAME_TILGJENGELIG = False

if sys.platform == "win32":
    import winsound


# =============================================================================
# FLERSPRÅKLIG SYSTEM / INTERNATIONALIZATION (i18n)
# =============================================================================
# Støtter Norsk, Engelsk og Spansk.
# Enkelt å utvide med nye språk ved å legge til en ny blokk nedenfor!

LANGUAGES = {
    "no": "🇳🇴 Norsk",
    "en": "🇬🇧 English",
    "es": "🇪🇸 Español",
}

TRANSLATIONS = {
    "no": {
        # Menytitler
        "menu_skin": "🎨 Bytt Skin...",
        "menu_size": "📏 Størrelse...",
        "menu_lang": "🌐 Språk / Language...",
        "menu_presets": "⏱️ Hurtigvalg tid...",
        "menu_custom": "⚙️ Still inn tid & oppgave...",
        "menu_test_sound": "🔊 Test skin-lyd",
        "menu_test_shake": "📳 Test risting",
        "menu_always_on_top": "📌 Fest alltid øverst (På/Av)",
        "menu_reset": "🔄 Nullstill (Reset)",
        "menu_about": "ℹ️ Om prosjektet...",
        "menu_exit": "❌ Avslutt",

        # Hurtigvalg
        "preset_25": "🍅 25 min (Fokusøkt)",
        "preset_5": "☕ 5 min (Kort pause)",
        "preset_15": "🌟 15 min (Lang pause)",
        "preset_1": "⚡ 1 min (Rask test)",

        # Mage-tekster (Status i timeren)
        "unit_min": "MIN",
        "default_task": "fokus",
        "btn_start": "✔ START",
        "btn_resume": "▶ FORTSETT",
        "btn_pause": "⏸ PAUSE",
        "status_done": "FERDIG!",
        "btn_reset": "🔄 RESET",

        # Størrelser
        "size_small": "▫️ Liten (224 x 288)",
        "size_medium": "◽ Medium (280 x 360) - Standard",
        "size_large": "◻️ Stor (336 x 432)",
        "size_extra": "⬛ Ekstra Stor (392 x 504)",

        # Innstillingsdialog
        "dlg_settings_title": "⏱️ Still inn tid",
        "dlg_settings_header": "⏱️ STILL INN TID & OPPGAVE",
        "lbl_hours": "Timer",
        "lbl_minutes": "Minutter",
        "lbl_seconds": "Sekunder",
        "lbl_task": "Oppgavenavn (vises i magen):",
        "err_integers": "⚠️ Skriv inn bare positive hele tall!",
        "err_max_hours": "⚠️ Maks 24 timer er tillatt!",
        "err_greater_zero": "⚠️ Tiden må være større enn 0 sekunder!",
        "btn_save": "✔ Lagre",
        "btn_cancel": "✕ Avbryt",

        # Om-dialog
        "dlg_about_title": "ℹ️ Om Pomodoro Maskot",
        "about_header": "🥑 PIXEL MASCOT POMODORO",
        "about_created_by": "Laget av OneUp82",
        "about_github_btn": "🌐 Besøk OneUp82 på GitHub",
        "btn_close": "Lukk",
    },
    "en": {
        "menu_skin": "🎨 Change Skin...",
        "menu_size": "📏 Size...",
        "menu_lang": "🌐 Language / Språk...",
        "menu_presets": "⏱️ Quick Presets...",
        "menu_custom": "⚙️ Set Time & Task...",
        "menu_test_sound": "🔊 Test Skin Sound",
        "menu_test_shake": "📳 Test Shake Animation",
        "menu_always_on_top": "📌 Always on Top (On/Off)",
        "menu_reset": "🔄 Reset Timer",
        "menu_about": "ℹ️ About Project...",
        "menu_exit": "❌ Exit",

        "preset_25": "🍅 25 min (Focus session)",
        "preset_5": "☕ 5 min (Short break)",
        "preset_15": "🌟 15 min (Long break)",
        "preset_1": "⚡ 1 min (Quick test)",

        "unit_min": "MIN",
        "default_task": "focus",
        "btn_start": "✔ START",
        "btn_resume": "▶ RESUME",
        "btn_pause": "⏸ PAUSE",
        "status_done": "FINISHED!",
        "btn_reset": "🔄 RESET",

        "size_small": "▫️ Small (224 x 288)",
        "size_medium": "◽ Medium (280 x 360) - Default",
        "size_large": "◻️ Large (336 x 432)",
        "size_extra": "⬛ Extra Large (392 x 504)",

        "dlg_settings_title": "⏱️ Set Time & Task",
        "dlg_settings_header": "⏱️ SET TIME & TASK",
        "lbl_hours": "Hours",
        "lbl_minutes": "Minutes",
        "lbl_seconds": "Seconds",
        "lbl_task": "Task name (shown in belly):",
        "err_integers": "⚠️ Please enter only positive integers!",
        "err_max_hours": "⚠️ Maximum 24 hours allowed!",
        "err_greater_zero": "⚠️ Time must be greater than 0 seconds!",
        "btn_save": "✔ Save",
        "btn_cancel": "✕ Cancel",

        "dlg_about_title": "ℹ️ About Pomodoro Mascot",
        "about_header": "🥑 PIXEL MASCOT POMODORO",
        "about_created_by": "Created by OneUp82",
        "about_github_btn": "🌐 Visit OneUp82 on GitHub",
        "btn_close": "Close",
    },
    "es": {
        "menu_skin": "🎨 Cambiar Skin...",
        "menu_size": "📏 Tamaño...",
        "menu_lang": "🌐 Idioma / Language...",
        "menu_presets": "⏱️ Tiempos Rápidos...",
        "menu_custom": "⚙️ Ajustar Tiempo y Tarea...",
        "menu_test_sound": "🔊 Probar Sonido",
        "menu_test_shake": "📳 Probar Vibración",
        "menu_always_on_top": "📌 Siempre Visible (Sí/No)",
        "menu_reset": "🔄 Reiniciar Temporizador",
        "menu_about": "ℹ️ Acerca del Proyecto...",
        "menu_exit": "❌ Salir",

        "preset_25": "🍅 25 min (Sesión de enfoque)",
        "preset_5": "☕ 5 min (Pausa corta)",
        "preset_15": "🌟 15 min (Pausa larga)",
        "preset_1": "⚡ 1 min (Prueba rápida)",

        "unit_min": "MIN",
        "default_task": "enfoque",
        "btn_start": "✔ INICIAR",
        "btn_resume": "▶ CONTINUAR",
        "btn_pause": "⏸ PAUSA",
        "status_done": "¡LISTO!",
        "btn_reset": "🔄 REINICIAR",

        "size_small": "▫️ Pequeño (224 x 288)",
        "size_medium": "◽ Mediano (280 x 360) - Estándar",
        "size_large": "◻️ Grande (336 x 432)",
        "size_extra": "⬛ Extra Grande (392 x 504)",

        "dlg_settings_title": "⏱️ Ajustar Tiempo",
        "dlg_settings_header": "⏱️ AJUSTAR TIEMPO Y TAREA",
        "lbl_hours": "Horas",
        "lbl_minutes": "Minutos",
        "lbl_seconds": "Segundos",
        "lbl_task": "Nombre de la tarea (en la barriga):",
        "err_integers": "⚠️ ¡Introduce solo números enteros positivos!",
        "err_max_hours": "⚠️ ¡El máximo permitido son 24 horas!",
        "err_greater_zero": "⚠️ ¡El tiempo debe ser mayor a 0 segundos!",
        "btn_save": "✔ Guardar",
        "btn_cancel": "✕ Cancelar",

        "dlg_about_title": "ℹ️ Acerca de Pomodoro Mascot",
        "about_header": "🥑 PIXEL MASCOT POMODORO",
        "about_created_by": "Creado por OneUp82",
        "about_github_btn": "🌐 Visitar OneUp82 en GitHub",
        "btn_close": "Cerrar",
    }
}


# =============================================================================
# DEFINISJON AV SKINS OG STØRRELSER
# =============================================================================

SKIN_DEFINITIONS = [
    {"id": "avocado",    "names": {"no": "🥑 Avokado (Avo-venn)", "en": "🥑 Avocado (Avo-friend)", "es": "🥑 Aguacate (Avo-amigo)"}},
    {"id": "cat",        "names": {"no": "🐱 Katt (Pus)",         "en": "🐱 Cat (Kitty)",         "es": "🐱 Gato (Michi)"}},
    {"id": "dog",        "names": {"no": "🐶 Hund (Valp)",        "en": "🐶 Dog (Puppy)",         "es": "🐶 Perro (Cachorro)"}},
    {"id": "frog",       "names": {"no": "🐸 Frosk (Kvekk)",      "en": "🐸 Frog (Ribbit)",       "es": "🐸 Rana (Croac)"}},
    {"id": "duck",       "names": {"no": "🦆 And (Kvakk)",        "en": "🦆 Duck (Quack)",        "es": "🦆 Pato (Cuac)"}},
    {"id": "panda",      "names": {"no": "🐼 Panda (Bambus)",     "en": "🐼 Panda (Bamboo)",      "es": "🐼 Panda (Bambú)"}},
    {"id": "robot",      "names": {"no": "🤖 Robot (Beep)",       "en": "🤖 Robot (Beep)",       "es": "🤖 Robot (Bip)"}},
    {"id": "ghost",      "names": {"no": "👻 Spøkelse (Bø)",      "en": "👻 Ghost (Boo)",         "es": "👻 Fantasma (Buh)"}},
    {"id": "strawberry", "names": {"no": "🍓 Jordbær (Bær)",      "en": "🍓 Strawberry (Berry)",  "es": "🍓 Fresa (Baya)"}},
    {"id": "bear",       "names": {"no": "🐻 Bjørn (Teddy)",      "en": "🐻 Bear (Teddy)",        "es": "🐻 Oso (Teddy)"}},
]

STORRELSER = [
    {"id": "liten",   "key": "size_small",  "skala": 8},
    {"id": "medium",  "key": "size_medium", "skala": 10},
    {"id": "stor",    "key": "size_large",  "skala": 12},
    {"id": "ekstra",  "key": "size_extra",  "skala": 14},
]


# =============================================================================
# LYDFUNKSJONER (AUDIO PLAYBACK)
# =============================================================================

def spill_skin_lyd(skin_id):
    """
    Spiller av lydfilen tilknyttet et skin (f.eks. skins/cat.wav).
    Prioriterer pygame.mixer hvis tilgjengelig, deretter winsound på Windows.
    """
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

    # Siste utvei hvis ingen lydmodul er tilgjengelig
    print("\a")


# =============================================================================
# HOVEDAPP: DEN SØTE FLYTENDE POMODORO-MASKOTEN
# =============================================================================

class PomodoroMascot(tk.Tk):
    """
    Hovedapplikasjonen for skrivebordsmaskoten.
    Kjører som et rammeløst (overrideredirect) vindu med gjennomsiktig bakgrunn.
    """

    CONFIG_FILE = "config.json"

    def __init__(self):
        super().__init__()

        # Sørg for at standardressurser (skins og lyder) er på plass
        self.verifiser_og_lag_filer()

        # Last inn lagrede brukerinnstillinger (språk, skin, skala)
        self.last_innstillinger()

        # Grunnleggende vindusinnstillinger
        self.title("Pixel Mascot Pomodoro - OneUp82")
        self.overrideredirect(True)              # Fjerner OS-vindusramme
        self.wm_attributes("-topmost", True)      # Holder maskoten flytende over andre apper

        # Transparent fargenøkkel (kun piksler med denne fargen blir usynlige)
        self.trans_farge = "#010203"
        self.wm_attributes("-transparentcolor", self.trans_farge)
        self.configure(bg=self.trans_farge)

        # Skalering og vindusdimensjoner (basert på 28x36 piksler)
        self.bredde = 28 * self.gjeldende_skala
        self.hoyde = 36 * self.gjeldende_skala

        # Plasser maskoten pent nede til høyre ved første oppstart
        skjerm_b = self.winfo_screenwidth()
        skjerm_h = self.winfo_screenheight()
        start_x = max(50, skjerm_b - self.bredde - 60)
        start_y = max(50, skjerm_h - self.hoyde - 100)
        self.geometry(f"{self.bredde}x{self.hoyde}+{start_x}+{start_y}")

        # Timer-tilstand
        self.total_sekunder = 25 * 60
        self.gjenstaende_sekunder = self.total_sekunder
        self.er_aktiv = False
        self.timer_id = None
        self.alltid_overst = True

        # Musedrag-tilstand
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._win_orig_x = 0
        self._win_orig_y = 0
        self._har_dradd = False

        # Opprett lerret, menyer og tegn maskoten på skjermen
        self.opprett_lerret()
        self.last_skin_bilde(self.aktivt_skin)
        self.opprett_hoyreklikk_meny()
        self.tegn_skjerm()

    # =========================================================================
    # INNSTILLINGER (CONFIG PERSISTENCE)
    # =========================================================================

    def last_innstillinger(self):
        """Laster inn lagrede preferanser for språk, skin og størrelse fra config.json."""
        self.aktivt_sprak = "no"
        self.aktivt_skin = "avocado"
        self.gjeldende_skala = 10
        self.oppgave_tekst = self.t("default_task")

        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.aktivt_sprak = data.get("language", "no")
                    self.aktivt_skin = data.get("skin", "avocado")
                    self.gjeldende_skala = data.get("scale", 10)
                    self.oppgave_tekst = data.get("task", self.t("default_task"))
            except Exception as e:
                print(f"[Config-advarsel] Kunne ikke lese innstillinger: {e}")

    def lagre_innstillinger(self):
        """Lagrer gjeldende språk, skin og størrelse til config.json."""
        data = {
            "language": self.aktivt_sprak,
            "skin": self.aktivt_skin,
            "scale": self.gjeldende_skala,
            "task": self.oppgave_tekst
        }
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Config-advarsel] Kunne ikke lagre innstillinger: {e}")

    def t(self, nokkel):
        """Hjelpemetode for å hente oversatt tekst basert på gjeldende språk."""
        sprak_tabell = TRANSLATIONS.get(self.aktivt_sprak, TRANSLATIONS["no"])
        return sprak_tabell.get(nokkel, TRANSLATIONS["no"].get(nokkel, nokkel))

    def bytt_sprak(self, nytt_sprak):
        """Bytter aktivt språk og oppdaterer alle menyer og tekster umiddelbart."""
        if nytt_sprak in TRANSLATIONS:
            self.aktivt_sprak = nytt_sprak
            # Hvis oppgaven er standard, oversett den til det nye språket
            if self.oppgave_tekst in ["fokus", "focus", "enfoque"]:
                self.oppgave_tekst = self.t("default_task")
            self.opprett_hoyreklikk_meny()
            self.tegn_skjerm()
            self.lagre_innstillinger()

    def verifiser_og_lag_filer(self):
        """Sjekker om alle bildefiler og lydfiler eksisterer, og genererer dem ved behov."""
        os.makedirs("skins", exist_ok=True)
        mangler = False
        for s in SKIN_DEFINITIONS:
            if not os.path.exists(f"skins/{s['id']}.png") or not os.path.exists(f"skins/{s['id']}.wav"):
                mangler = True
                break
        if mangler:
            print("[Info] Genererer skins og lyder...")
            generate_assets.bygg_alle_skins()
            generate_assets.bygg_alle_lyder()

    # =========================================================================
    # LERRET OG TEGNING AV MASKOTEN (CANVAS RENDERING)
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

        # Koble musehendelser
        self.canvas.bind("<ButtonPress-1>", self.paa_mus_trykk)
        self.canvas.bind("<B1-Motion>", self.paa_mus_dra)
        self.canvas.bind("<ButtonRelease-1>", self.paa_mus_slipp)
        self.canvas.bind("<Button-3>", self.vis_hoyreklikk_meny)

    def last_skin_bilde(self, skin_id):
        """Laster inn bildet og skalerer det knivskarpt med Nearest Neighbor-filtrering."""
        bilde_sti = os.path.join("skins", f"{skin_id}.png")
        if not os.path.exists(bilde_sti):
            bilde_sti = "cat.png"

        pil_img = Image.open(bilde_sti)
        skalert_img = pil_img.resize((self.bredde, self.hoyde), Image.Resampling.NEAREST)
        self.tk_maskot_bilde = ImageTk.PhotoImage(skalert_img)

    def tegn_tekst_med_skygge(self, x, y, tekst, farge, font, skygge_farge="#000000"):
        """Tegner tekst med en diskret mørk fallskygge for maksimal kontrast og lesbarhet."""
        self.canvas.create_text(x + 1, y + 1, text=tekst, fill=skygge_farge, font=font)
        self.canvas.create_text(x, y, text=tekst, fill=farge, font=font)

    def tegn_skjerm(self):
        """
        Tegner hele maskoten og det dynamiske innholdet inni magen:
        - Bakgrunnsbilde av maskoten
        - Mørk, høykontrast skjermplate i magen
        - Sirkulær fremdriftsbue
        - Digital nedtelling / minuttvisning
        - Oppgavetekst og Start/Pause-knapp
        """
        self.canvas.delete("all")

        # 1. Tegn maskotbildet sentrert på lerretet
        self.canvas.create_image(self.bredde // 2, self.hoyde // 2, image=self.tk_maskot_bilde)

        # 2. Beregn dynamiske koordinater basert på gjeldende skala
        s = self.gjeldende_skala
        cx = int(14.0 * s)
        cy = int(24.2 * s)
        r = int(5.8 * s)

        # 3. Mørk skjermflate inni magen (sikrer 100% kontrast uansett hudfarge/pels på maskoten)
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

        # 5. Fremdriftsbue (Sirkulær progress bar som animeres)
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

        # 6. Skrifttyper skalert etter vindusstørrelsen
        font_klokke = ("Consolas", int(1.75 * s), "bold")
        font_stortall = ("Segoe UI", int(2.1 * s), "bold")
        font_tekst = ("Segoe UI", max(8, int(0.9 * s)), "bold")
        font_knapp = ("Segoe UI", max(8, int(0.95 * s)), "bold")

        # 7. Render innhold inni magen
        if self.gjenstaende_sekunder <= 0:
            # Tiden er ute
            self.tegn_tekst_med_skygge(cx, cy - int(1.3 * s), "00:00", "#FF4B72", font_klokke)
            self.tegn_tekst_med_skygge(cx, cy + int(0.2 * s), self.t("status_done"), "#FFD166", font_tekst)
            self.canvas.create_line(cx - int(2.2 * s), cy + int(1.4 * s), cx + int(2.2 * s), cy + int(1.4 * s), fill="#4A455A", width=max(1, int(0.15 * s)))
            self.tegn_tekst_med_skygge(cx, cy + int(2.5 * s), self.t("btn_reset"), "#00F5A0", font_knapp)

        elif self.er_aktiv:
            # Nedtellingen går: Vis MM:SS i stor, skarp hvit skrift
            m = self.gjenstaende_sekunder // 60
            sec = self.gjenstaende_sekunder % 60
            tid_tekst = f"{m:02d}:{sec:02d}"

            self.tegn_tekst_med_skygge(cx, cy - int(1.4 * s), tid_tekst, "#FFFFFF", font_klokke)
            self.tegn_tekst_med_skygge(cx, cy + int(0.1 * s), f"({self.oppgave_tekst})", "#FFD166", font_tekst)
            self.canvas.create_line(cx - int(2.2 * s), cy + int(1.3 * s), cx + int(2.2 * s), cy + int(1.3 * s), fill="#4A455A", width=max(1, int(0.15 * s)))
            self.tegn_tekst_med_skygge(cx, cy + int(2.4 * s), self.t("btn_pause"), "#00F5A0", font_knapp)

        else:
            # Klar / Pauset: Vis minutter og START
            minutter = max(1, math.ceil(self.gjenstaende_sekunder / 60))
            self.tegn_tekst_med_skygge(cx, cy - int(1.6 * s), str(minutter), "#FFFFFF", font_stortall)
            self.tegn_tekst_med_skygge(cx, cy - int(0.1 * s), self.t("unit_min"), "#FFD166", font_tekst)
            self.tegn_tekst_med_skygge(cx, cy + int(1.0 * s), f"({self.oppgave_tekst})", "#DDDDDD", font_tekst)
            self.canvas.create_line(cx - int(2.2 * s), cy + int(1.8 * s), cx + int(2.2 * s), cy + int(1.8 * s), fill="#4A455A", width=max(1, int(0.15 * s)))
            start_tekst = self.t("btn_start") if (self.gjenstaende_sekunder == self.total_sekunder) else self.t("btn_resume")
            self.tegn_tekst_med_skygge(cx, cy + int(2.7 * s), start_tekst, "#00F5A0", font_knapp)

    # =========================================================================
    # MUS-INTERAKSJON: DRAING OG KLIKKING (DRAG & CLICK ENGINE)
    # =========================================================================

    def paa_mus_trykk(self, event):
        """Registrerer startposisjonen når venstre museknapp trykkes ned."""
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._win_orig_x = self.winfo_x()
        self._win_orig_y = self.winfo_y()
        self._har_dradd = False

    def paa_mus_dra(self, event):
        """Flytter vinduet sammen med musepekeren hvis musen beveges."""
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        if abs(dx) > 3 or abs(dy) > 3:
            self._har_dradd = True
            ny_x = self._win_orig_x + dx
            ny_y = self._win_orig_y + dy
            self.geometry(f"+{ny_x}+{ny_y}")

    def paa_mus_slipp(self, event):
        """Håndterer klikk hvis brukeren ikke dro maskoten."""
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
    # HØYREKLIKK-MENY MED SPRÅKVELGER OG STØRRELSER
    # =========================================================================

    def opprett_hoyreklikk_meny(self):
        """Bygger den flerspråklige høyreklikk-menyen dynamisk."""
        self.meny = tk.Menu(
            self,
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#242432",
            fg="#FFFFFF",
            activebackground="#00F5A0",
            activeforeground="#000000"
        )

        # 1. Undermeny: Skins (med oversatte navn)
        self.skin_meny = tk.Menu(
            self.meny,
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#242432",
            fg="#FFFFFF",
            activebackground="#00F5A0",
            activeforeground="#000000"
        )
        for s in SKIN_DEFINITIONS:
            prefiks = "✓ " if (s["id"] == self.aktivt_skin) else "   "
            navn = s["names"].get(self.aktivt_sprak, s["names"]["en"])
            self.skin_meny.add_command(
                label=f"{prefiks}{navn}",
                command=lambda sid=s["id"]: self.bytt_skin(sid)
            )

        # 2. Undermeny: Størrelser
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
            tekst = self.t(st["key"])
            self.storrelse_meny.add_command(
                label=f"{prefiks}{tekst}",
                command=lambda skala=st["skala"]: self.sett_storrelse(skala)
            )

        # 3. Undermeny: Språk (Language Selector)
        self.sprak_meny = tk.Menu(
            self.meny,
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#242432",
            fg="#FFFFFF",
            activebackground="#00F5A0",
            activeforeground="#000000"
        )
        for kode, spraknavn in LANGUAGES.items():
            prefiks = "✓ " if (kode == self.aktivt_sprak) else "   "
            self.sprak_meny.add_command(
                label=f"{prefiks}{spraknavn}",
                command=lambda k=kode: self.bytt_sprak(k)
            )

        # 4. Undermeny: Hurtigvalg tid
        self.hurtig_meny = tk.Menu(
            self.meny,
            tearoff=0,
            font=("Segoe UI", 9),
            bg="#242432",
            fg="#FFFFFF",
            activebackground="#00F5A0",
            activeforeground="#000000"
        )
        self.hurtig_meny.add_command(label=self.t("preset_25"), command=lambda: self.sett_tid(0, 25, 0))
        self.hurtig_meny.add_command(label=self.t("preset_5"),  command=lambda: self.sett_tid(0, 5, 0))
        self.hurtig_meny.add_command(label=self.t("preset_15"), command=lambda: self.sett_tid(0, 15, 0))
        self.hurtig_meny.add_command(label=self.t("preset_1"),  command=lambda: self.sett_tid(0, 1, 0))

        # Bygg hovedstrukturen i menyen
        self.meny.add_cascade(label=self.t("menu_skin"),     menu=self.skin_meny)
        self.meny.add_cascade(label=self.t("menu_size"),     menu=self.storrelse_meny)
        self.meny.add_cascade(label=self.t("menu_lang"),     menu=self.sprak_meny)
        self.meny.add_cascade(label=self.t("menu_presets"),  menu=self.hurtig_meny)
        self.meny.add_command(label=self.t("menu_custom"),   command=self.apne_tidsinnstilling)
        self.meny.add_separator()
        self.meny.add_command(label=self.t("menu_test_sound"), command=lambda: spill_skin_lyd(self.aktivt_skin))
        self.meny.add_command(label=self.t("menu_test_shake"), command=self.start_risting)
        self.meny.add_command(label=self.t("menu_always_on_top"), command=self.veksle_alltid_overst)
        self.meny.add_command(label=self.t("menu_reset"),    command=self.nullstill_timer)
        self.meny.add_separator()
        self.meny.add_command(label=self.t("menu_about"),    command=self.apne_om_dialog)
        self.meny.add_command(label=self.t("menu_exit"),     command=self.destroy)

    def vis_hoyreklikk_meny(self, event):
        """Åpner popup-menyen ved musepekeren."""
        try:
            self.opprett_hoyreklikk_meny()
            self.meny.tk_popup(event.x_root, event.y_root)
        finally:
            self.meny.grab_release()

    def sett_storrelse(self, ny_skala):
        """Endrer størrelsen på maskoten og skalerer grafikk og skrifttyper."""
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
        self.lagre_innstillinger()

    def bytt_skin(self, nytt_skin_id):
        """Bytter aktivt skin, oppdaterer grafikken og spiller av lyden."""
        self.aktivt_skin = nytt_skin_id
        self.last_skin_bilde(nytt_skin_id)
        self.tegn_skjerm()
        spill_skin_lyd(nytt_skin_id)
        self.lagre_innstillinger()

    def veksle_alltid_overst(self):
        """Slår på eller av om maskoten skal ligge foran andre vinduer."""
        self.alltid_overst = not self.alltid_overst
        self.wm_attributes("-topmost", self.alltid_overst)

    # =========================================================================
    # TIMER-KONTROLL OG RISTE-EFFEKT (COUNTDOWN & SHAKE ENGINE)
    # =========================================================================

    def veksle_start_pause(self):
        """Starter eller pauser timeren avhengig av gjeldende status."""
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
        """Setter ny tid i sekunder og oppdaterer displayet."""
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.er_aktiv = False

        self.total_sekunder = (timer * 3600) + (minutter * 60) + sekunder
        self.gjenstaende_sekunder = self.total_sekunder
        self.tegn_skjerm()

    def nullstill_timer(self):
        """Nullstiller timeren tilbake til opprinnelig tid."""
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.er_aktiv = False
        self.gjenstaende_sekunder = self.total_sekunder
        self.tegn_skjerm()

    def tell_ned(self):
        """Hovedløkke for nedtelling. Kjøres hvert 1000. millisekund."""
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
        """Kalles når timeren treffer 00:00:00."""
        spill_skin_lyd(self.aktivt_skin)
        self.start_risting()

    def start_risting(self, antall_steg=26, styrke=14):
        """
        Rister maskoten fysisk på skjermen med dempet oscillasjon!
        Perfekt visuell feiring når tiden er ute.
        """
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
        """Viser en ren og stilig 'Om prosjektet'-dialog med lenke til OneUp82 på GitHub."""
        dialog = tk.Toplevel(self)
        dialog.title(self.t("dlg_about_title"))
        dialog.geometry("320x210")
        dialog.resizable(False, False)
        dialog.configure(bg="#1E1E28")
        dialog.wm_attributes("-topmost", True)

        pos_x = max(20, self.winfo_x() - 30)
        pos_y = max(20, self.winfo_y() - 10)
        dialog.geometry(f"+{pos_x}+{pos_y}")

        tk.Label(
            dialog,
            text=self.t("about_header"),
            font=("Segoe UI", 12, "bold"),
            bg="#1E1E28",
            fg="#00F5A0"
        ).pack(pady=(22, 6))

        tk.Label(
            dialog,
            text=self.t("about_created_by"),
            font=("Segoe UI", 11, "bold"),
            bg="#1E1E28",
            fg="#FFFFFF"
        ).pack(pady=(0, 16))

        def apne_github():
            webbrowser.open_new("https://github.com/OneUp82")

        tk.Button(
            dialog,
            text=self.t("about_github_btn"),
            command=apne_github,
            bg="#00F5A0",
            fg="#000000",
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=6,
            relief="flat",
            cursor="hand2"
        ).pack(pady=(0, 12))

        tk.Button(
            dialog,
            text=self.t("btn_close"),
            command=dialog.destroy,
            bg="#3A3A4C",
            fg="#FFFFFF",
            font=("Segoe UI", 9),
            padx=14,
            pady=3,
            relief="flat"
        ).pack()

    def apne_tidsinnstilling(self):
        """Åpner innstillingsvinduet for tid og oppgavenavn med full inndatavalidering."""
        dialog = tk.Toplevel(self)
        dialog.title(self.t("dlg_settings_title"))
        dialog.geometry("330x340")
        dialog.resizable(False, False)
        dialog.configure(bg="#1E1E28")
        dialog.wm_attributes("-topmost", True)

        pos_x = max(20, self.winfo_x() - 50)
        pos_y = max(20, self.winfo_y() - 20)
        dialog.geometry(f"+{pos_x}+{pos_y}")

        tk.Label(
            dialog,
            text=self.t("dlg_settings_header"),
            font=("Segoe UI", 12, "bold"),
            bg="#1E1E28",
            fg="#FFD166"
        ).pack(pady=(15, 10))

        ramme = tk.Frame(dialog, bg="#1E1E28")
        ramme.pack(pady=5)

        gjeldende_t = self.total_sekunder // 3600
        gjeldende_m = (self.total_sekunder % 3600) // 60
        gjeldende_s = self.total_sekunder % 60

        tk.Label(ramme, text=self.t("lbl_hours"), font=("Segoe UI", 9), bg="#1E1E28", fg="#FFFFFF").grid(row=0, column=0, padx=6)
        t_entry = tk.Entry(ramme, width=5, justify="center", font=("Segoe UI", 12), bg="#2B2B3C", fg="#FFFFFF", insertbackground="white")
        t_entry.insert(0, str(gjeldende_t))
        t_entry.grid(row=1, column=0, padx=6, pady=4)

        tk.Label(ramme, text=self.t("lbl_minutes"), font=("Segoe UI", 9), bg="#1E1E28", fg="#FFFFFF").grid(row=0, column=1, padx=6)
        m_entry = tk.Entry(ramme, width=5, justify="center", font=("Segoe UI", 12), bg="#2B2B3C", fg="#FFFFFF", insertbackground="white")
        m_entry.insert(0, str(gjeldende_m))
        m_entry.grid(row=1, column=1, padx=6, pady=4)

        tk.Label(ramme, text=self.t("lbl_seconds"), font=("Segoe UI", 9), bg="#1E1E28", fg="#FFFFFF").grid(row=0, column=2, padx=6)
        s_entry = tk.Entry(ramme, width=5, justify="center", font=("Segoe UI", 12), bg="#2B2B3C", fg="#FFFFFF", insertbackground="white")
        s_entry.insert(0, str(gjeldende_s))
        s_entry.grid(row=1, column=2, padx=6, pady=4)

        tk.Label(dialog, text=self.t("lbl_task"), font=("Segoe UI", 9), bg="#1E1E28", fg="#FFFFFF").pack(pady=(10, 2))
        oppgave_entry = tk.Entry(dialog, width=20, justify="center", font=("Segoe UI", 10), bg="#2B2B3C", fg="#FFFFFF", insertbackground="white")
        oppgave_entry.insert(0, self.oppgave_tekst)
        oppgave_entry.pack(pady=2)

        feil_label = tk.Label(dialog, text="", font=("Segoe UI", 8), bg="#1E1E28", fg="#EF476F")
        feil_label.pack(pady=4)

        def lagre():
            """Validerer inndataene trygt og sikkert uten eval()."""
            t_str = t_entry.get().strip() or "0"
            m_str = m_entry.get().strip() or "0"
            s_str = s_entry.get().strip() or "0"
            oppg = oppgave_entry.get().strip() or self.t("default_task")

            # Validering: Kun positive heltall
            if not (t_str.isdigit() and m_str.isdigit() and s_str.isdigit()):
                feil_label.config(text=self.t("err_integers"))
                return

            t = int(t_str)
            m = int(m_str)
            s = int(s_str)

            if t > 24:
                feil_label.config(text=self.t("err_max_hours"))
                return

            totalt = (t * 3600) + (m * 60) + s
            if totalt <= 0:
                feil_label.config(text=self.t("err_greater_zero"))
                return

            self.oppgave_tekst = oppg[:10]
            self.sett_tid(t, m, s)
            self.lagre_innstillinger()
            dialog.destroy()

        knappe_ramme = tk.Frame(dialog, bg="#1E1E28")
        knappe_ramme.pack(pady=10)

        tk.Button(
            knappe_ramme,
            text=self.t("btn_save"),
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
            text=self.t("btn_cancel"),
            command=dialog.destroy,
            bg="#3A3A4C",
            fg="#FFFFFF",
            font=("Segoe UI", 9),
            padx=10,
            pady=4,
            relief="flat"
        ).pack(side="left", padx=6)


# =============================================================================
# OPPSTART / ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app = PomodoroMascot()
    app.mainloop()
