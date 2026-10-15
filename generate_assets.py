"""
Genererer 10 søte pixel art skins og 10 matchende lydeffekter!
Oppdatert med dype, mørke mager (skjermer) for maksimal lesbarhet og kontrast!
"""

import os
import math
import struct
import wave
from PIL import Image

os.makedirs("skins", exist_ok=True)

# =============================================================================
# DEL 1: GENERERING AV 10 PIXEL ART SKINS
# =============================================================================

W, H = 28, 36
SCALE = 8

def lag_base_kropp(w=W, h=H, start_y=5, end_y=33, expand_top=5, expand_bottom=12):
    """Lager en grunnpære-/dråpeformet maskotkropp i et 2D-rutenett."""
    kropp = [[False] * w for _ in range(h)]
    for y in range(start_y, end_y + 1):
        t = (y - start_y) / float(end_y - start_y)
        if t < 0.35:
            radius = expand_top + (t / 0.35) * (expand_bottom * 0.7 - expand_top)
        else:
            radius = (expand_bottom * 0.7) + math.sin((t - 0.35) * math.pi / 0.65) * (expand_bottom * 0.3)
        cx = (w - 1) / 2.0
        min_x = max(1, int(cx - radius))
        max_x = min(w - 2, int(cx + radius))
        for x in range(min_x, max_x + 1):
            kropp[y][x] = True
    return kropp

def tegn_ansikt(img, eye_y=13, left_x=9, right_x=17, eye_h=3, blink=False):
    """Tegner søte piksel-øyne, glimt og kinn."""
    black = (24, 24, 28, 255)
    white = (255, 255, 255, 255)
    pink = (255, 110, 150, 255)

    # Øyne
    if blink:
        for x in (left_x, left_x + 1):
            img.putpixel((x, eye_y + 1), black)
        for x in (right_x, right_x + 1):
            img.putpixel((x, eye_y + 1), black)
    else:
        for ey in range(eye_y, eye_y + eye_h):
            for x in (left_x, left_x + 1):
                img.putpixel((x, ey), black)
            for x in (right_x, right_x + 1):
                img.putpixel((x, ey), black)
        # Glimt i øyet
        img.putpixel((left_x, eye_y), white)
        img.putpixel((right_x, eye_y), white)

    # Rosa kinn
    for x in (left_x - 2, left_x - 1):
        for y in (eye_y + eye_h - 1, eye_y + eye_h):
            img.putpixel((x, y), pink)
    for x in (right_x + 2, right_x + 3):
        for y in (eye_y + eye_h - 1, eye_y + eye_h):
            img.putpixel((x, y), pink)

    # Liten munn i midten
    img.putpixel((13, eye_y + eye_h), black)
    img.putpixel((14, eye_y + eye_h), black)

def tegn_mage_sirkel(img, cx=13.5, cy=24.0, radius=6.0, belly_color=(45, 24, 14, 255), border_color=(25, 14, 8, 255)):
    """Tegner en mørk, kontrastrik sirkulær skjerm i magen der teksten skal bo."""
    for y in range(int(cy - radius - 1), int(cy + radius + 2)):
        for x in range(int(cx - radius - 1), int(cx + radius + 2)):
            if 0 <= x < W and 0 <= y < H:
                dist = math.hypot(x - cx, y - cy)
                if dist <= radius:
                    if dist >= radius - 0.9:
                        img.putpixel((x, y), border_color)
                    else:
                        img.putpixel((x, y), belly_color)

def bygg_alle_skins():
    skins = {}

    # 1. 🥑 AVOKADO (Avo-venn)
    img1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp1 = lag_base_kropp()
    dk_grn = (32, 105, 32, 255)
    med_grn = (100, 175, 45, 255)
    lt_grn = (220, 242, 155, 255)
    spire_grn = (40, 160, 40, 255)

    for px, py in [(10, 1), (11, 1), (9, 2), (10, 2), (11, 3), (12, 3)]:
        img1.putpixel((px, py), spire_grn)
    for px, py in [(16, 1), (17, 1), (16, 2), (17, 2), (15, 3), (16, 3)]:
        img1.putpixel((px, py), spire_grn)

    for y in range(H):
        for x in range(W):
            if kropp1[y][x]:
                er_kant = (x == 0 or not kropp1[y][x-1] or x == W-1 or not kropp1[y][x+1] or
                           y == 0 or not kropp1[y-1][x] or y == H-1 or not kropp1[y+1][x])
                if er_kant:
                    img1.putpixel((x, y), dk_grn)
                elif (not kropp1[y-1][x-1] or not kropp1[y-1][x+1] or not kropp1[y+1][x-1] or not kropp1[y+1][x+1]):
                    img1.putpixel((x, y), med_grn)
                else:
                    img1.putpixel((x, y), lt_grn)

    for sx, sy in [(7, 10), (6, 22), (8, 27), (20, 11), (21, 23), (19, 28)]:
        img1.putpixel((sx, sy), (195, 225, 125, 255))
    tegn_ansikt(img1, eye_y=12, eye_h=3)
    # Mørk sjokoladebrun avokadostein
    tegn_mage_sirkel(img1, belly_color=(45, 24, 14, 255), border_color=(25, 14, 8, 255))
    skins["avocado"] = img1

    # 2. 🐱 KATT (Pus)
    img2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp2 = lag_base_kropp(start_y=8, end_y=33)
    pels_oransje = (255, 160, 60, 255)
    striper = (220, 115, 25, 255)
    katt_kant = (45, 30, 25, 255)
    pink = (255, 150, 180, 255)

    for ex, ey in [(6, 4), (7, 4), (6, 5), (7, 5), (8, 5), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6),
                   (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7)]:
        img2.putpixel((ex, ey), pels_oransje)
    for ex, ey in [(7, 5), (7, 6), (8, 6), (7, 7), (8, 7)]:
        img2.putpixel((ex, ey), pink)

    for ex, ey in [(20, 4), (21, 4), (19, 5), (20, 5), (21, 5), (18, 6), (19, 6), (20, 6), (21, 6), (22, 6),
                   (17, 7), (18, 7), (19, 7), (20, 7), (21, 7), (22, 7)]:
        img2.putpixel((ex, ey), pels_oransje)
    for ex, ey in [(20, 5), (19, 6), (20, 6), (19, 7), (20, 7)]:
        img2.putpixel((ex, ey), pink)

    for y in range(H):
        for x in range(W):
            if kropp2[y][x]:
                er_kant = (x == 0 or not kropp2[y][x-1] or x == W-1 or not kropp2[y][x+1] or
                           y == 0 or not kropp2[y-1][x] or y == H-1 or not kropp2[y+1][x])
                if er_kant:
                    img2.putpixel((x, y), katt_kant)
                elif (y in (10, 11, 26, 27) and (x < 10 or x > 17)):
                    img2.putpixel((x, y), striper)
                else:
                    img2.putpixel((x, y), pels_oransje)

    for x in range(8, 20):
        img2.putpixel((x, 18), (230, 50, 60, 255))
    img2.putpixel((13, 19), (255, 215, 0, 255))
    img2.putpixel((14, 19), (255, 215, 0, 255))

    tegn_ansikt(img2, eye_y=12, eye_h=3)
    # Mørk dyp lilla/natt-mage for katten
    tegn_mage_sirkel(img2, cy=25.0, radius=5.8, belly_color=(36, 26, 42, 255), border_color=(22, 15, 26, 255))
    skins["cat"] = img2

    # 3. 🐶 HUND (Valp)
    img3 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp3 = lag_base_kropp(start_y=7, end_y=33)
    hund_brun = (215, 160, 95, 255)
    hund_mork = (145, 95, 50, 255)
    hund_kant = (40, 25, 15, 255)

    for ox, oy in [(3, 8), (4, 8), (3, 9), (4, 9), (5, 9), (3, 10), (4, 10), (5, 10), (3, 11), (4, 11), (3, 12), (4, 12)]:
        img3.putpixel((ox, oy), hund_mork)
    for ox, oy in [(23, 8), (24, 8), (22, 9), (23, 9), (24, 9), (22, 10), (23, 10), (24, 10), (23, 11), (24, 11), (23, 12), (24, 12)]:
        img3.putpixel((ox, oy), hund_mork)

    for y in range(H):
        for x in range(W):
            if kropp3[y][x]:
                er_kant = (x == 0 or not kropp3[y][x-1] or x == W-1 or not kropp3[y][x+1] or
                           y == 0 or not kropp3[y-1][x] or y == H-1 or not kropp3[y+1][x])
                img3.putpixel((x, y), hund_kant if er_kant else hund_brun)

    for x in range(8, 20):
        img3.putpixel((x, 18), (50, 140, 235, 255))

    tegn_ansikt(img3, eye_y=12, eye_h=3)
    img3.putpixel((13, 17), (255, 100, 130, 255))
    # Mørk lærbrun mage for hunden
    tegn_mage_sirkel(img3, cy=25.0, radius=5.8, belly_color=(42, 24, 14, 255), border_color=(26, 14, 8, 255))
    skins["dog"] = img3

    # 4. 🐸 FROSK (Kvekk)
    img4 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp4 = lag_base_kropp(start_y=8, end_y=33)
    frosk_gronn = (115, 205, 75, 255)
    frosk_kant = (30, 85, 25, 255)

    for ex, ey in [(6, 4), (7, 4), (8, 4), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]:
        img4.putpixel((ex, ey), frosk_gronn)
    for ex, ey in [(19, 4), (20, 4), (21, 4), (18, 5), (19, 5), (20, 5), (21, 5), (22, 5), (18, 6), (19, 6), (20, 6), (21, 6), (22, 6)]:
        img4.putpixel((ex, ey), frosk_gronn)

    for y in range(H):
        for x in range(W):
            if kropp4[y][x]:
                er_kant = (x == 0 or not kropp4[y][x-1] or x == W-1 or not kropp4[y][x+1] or
                           y == 0 or not kropp4[y-1][x] or y == H-1 or not kropp4[y+1][x])
                img4.putpixel((x, y), frosk_kant if er_kant else frosk_gronn)

    tegn_ansikt(img4, eye_y=6, left_x=6, right_x=20, eye_h=3)
    for mx in range(11, 17):
        img4.putpixel((mx, 14), (30, 85, 25, 255))
    # Mørk dyp skogsgrønn mage for frosken
    tegn_mage_sirkel(img4, cy=24.0, radius=6.0, belly_color=(18, 44, 20, 255), border_color=(10, 26, 12, 255))
    skins["frog"] = img4

    # 5. 🦆 AND (Kvakk)
    img5 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp5 = lag_base_kropp(start_y=6, end_y=33)
    and_gul = (255, 220, 55, 255)
    and_nebb = (255, 135, 25, 255)
    and_kant = (50, 40, 10, 255)

    for fx, fy in [(13, 3), (14, 3), (14, 4), (15, 4), (14, 5)]:
        img5.putpixel((fx, fy), and_gul)

    for y in range(H):
        for x in range(W):
            if kropp5[y][x]:
                er_kant = (x == 0 or not kropp5[y][x-1] or x == W-1 or not kropp5[y][x+1] or
                           y == 0 or not kropp5[y-1][x] or y == H-1 or not kropp5[y+1][x])
                img5.putpixel((x, y), and_kant if er_kant else and_gul)

    tegn_ansikt(img5, eye_y=11, eye_h=3)
    for nx in range(11, 17):
        for ny in (15, 16):
            img5.putpixel((nx, ny), and_nebb)
    # Mørk innsjø-blå mage for anden
    tegn_mage_sirkel(img5, cy=24.5, radius=5.8, belly_color=(16, 36, 52, 255), border_color=(10, 22, 34, 255))
    skins["duck"] = img5

    # 6. 🐼 PANDA (Bambus)
    img6 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp6 = lag_base_kropp(start_y=7, end_y=33)
    panda_hvit = (250, 250, 252, 255)
    panda_sort = (35, 35, 42, 255)

    for ex, ey in [(6, 4), (7, 4), (8, 4), (5, 5), (6, 5), (7, 5), (8, 5), (5, 6), (6, 6), (7, 6)]:
        img6.putpixel((ex, ey), panda_sort)
    for ex, ey in [(19, 4), (20, 4), (21, 4), (19, 5), (20, 5), (21, 5), (22, 5), (20, 6), (21, 6), (22, 6)]:
        img6.putpixel((ex, ey), panda_sort)

    for y in range(H):
        for x in range(W):
            if kropp6[y][x]:
                er_kant = (x == 0 or not kropp6[y][x-1] or x == W-1 or not kropp6[y][x+1] or
                           y == 0 or not kropp6[y-1][x] or y == H-1 or not kropp6[y+1][x])
                if er_kant:
                    img6.putpixel((x, y), panda_sort)
                elif y > 29 or (y in (18, 19) and (x < 8 or x > 19)):
                    img6.putpixel((x, y), panda_sort)
                else:
                    img6.putpixel((x, y), panda_hvit)

    for px in range(8, 12):
        for py in range(12, 16):
            img6.putpixel((px, py), panda_sort)
    for px in range(16, 20):
        for py in range(12, 16):
            img6.putpixel((px, py), panda_sort)

    img6.putpixel((9, 13), (255, 255, 255, 255))
    img6.putpixel((17, 13), (255, 255, 255, 255))
    img6.putpixel((6, 16), (255, 130, 160, 255))
    img6.putpixel((21, 16), (255, 130, 160, 255))
    img6.putpixel((13, 16), panda_sort)
    img6.putpixel((14, 16), panda_sort)

    # Mørk kullgrå mage for pandaen
    tegn_mage_sirkel(img6, cy=24.5, radius=5.8, belly_color=(26, 28, 34, 255), border_color=(16, 16, 20, 255))
    skins["panda"] = img6

    # 7. 🤖 ROBOT (Beep)
    img7 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp7 = lag_base_kropp(start_y=6, end_y=33)
    robot_graa = (160, 180, 205, 255)
    robot_kant = (30, 40, 55, 255)
    cyan_glow = (60, 240, 255, 255)

    img7.putpixel((13, 1), (255, 70, 80, 255))
    img7.putpixel((14, 1), (255, 70, 80, 255))
    img7.putpixel((13, 2), (255, 70, 80, 255))
    img7.putpixel((14, 2), (255, 70, 80, 255))
    for ay in (3, 4, 5):
        img7.putpixel((13, ay), (120, 140, 160, 255))
        img7.putpixel((14, ay), (120, 140, 160, 255))

    for y in range(H):
        for x in range(W):
            if kropp7[y][x]:
                er_kant = (x == 0 or not kropp7[y][x-1] or x == W-1 or not kropp7[y][x+1] or
                           y == 0 or not kropp7[y-1][x] or y == H-1 or not kropp7[y+1][x])
                img7.putpixel((x, y), robot_kant if er_kant else robot_graa)

    for ey in (12, 13):
        for ex in (9, 10):
            img7.putpixel((ex, ey), cyan_glow)
        for ex in (17, 18):
            img7.putpixel((ex, ey), cyan_glow)

    for mx in (12, 13, 14, 15):
        img7.putpixel((mx, 16), (40, 50, 65, 255))

    # Mørk reaktor-kjerne for roboten
    tegn_mage_sirkel(img7, cy=24.5, radius=5.8, belly_color=(15, 28, 44, 255), border_color=(25, 60, 95, 255))
    skins["robot"] = img7

    # 8. 👻 SPØKELSE (Bø)
    img8 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp8 = lag_base_kropp(start_y=6, end_y=30)
    spok_hvit = (245, 250, 255, 255)
    spok_kant = (50, 60, 80, 255)

    for y in range(H):
        for x in range(W):
            if kropp8[y][x]:
                er_kant = (x == 0 or not kropp8[y][x-1] or x == W-1 or not kropp8[y][x+1] or
                           y == 0 or not kropp8[y-1][x] or y == 30)
                img8.putpixel((x, y), spok_kant if er_kant else spok_hvit)

    for bx in range(6, 22):
        if bx % 4 in (0, 1):
            img8.putpixel((bx, 31), spok_hvit)
            img8.putpixel((bx, 32), spok_kant)
        else:
            img8.putpixel((bx, 31), spok_kant)

    tegn_ansikt(img8, eye_y=12, eye_h=3)
    # Mørk kosmisk lilla mage for spøkelset
    tegn_mage_sirkel(img8, cy=23.5, radius=5.8, belly_color=(32, 20, 48, 255), border_color=(20, 12, 32, 255))
    skins["ghost"] = img8

    # 9. 🍓 JORDBÆR (Bær)
    img9 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp9 = lag_base_kropp(start_y=7, end_y=33)
    bar_rod = (235, 55, 75, 255)
    bar_kant = (60, 15, 25, 255)
    blad_gronn = (70, 180, 65, 255)

    for bx, by in [(13, 2), (14, 2), (13, 3), (14, 3),
                   (9, 4), (10, 4), (11, 4), (12, 4), (13, 4), (14, 4), (15, 4), (16, 4), (17, 4), (18, 4),
                   (8, 5), (9, 5), (10, 5), (17, 5), (18, 5), (19, 5)]:
        img9.putpixel((bx, by), blad_gronn)

    for y in range(H):
        for x in range(W):
            if kropp9[y][x]:
                er_kant = (x == 0 or not kropp9[y][x-1] or x == W-1 or not kropp9[y][x+1] or
                           y == 0 or not kropp9[y-1][x] or y == H-1 or not kropp9[y+1][x])
                img9.putpixel((x, y), bar_kant if er_kant else bar_rod)

    for fx, fy in [(7, 10), (20, 10), (6, 21), (21, 21), (8, 27), (19, 27)]:
        img9.putpixel((fx, fy), (255, 235, 100, 255))

    tegn_ansikt(img9, eye_y=12, eye_h=3)
    # Mørk rubin-rød mage for jordbæret
    tegn_mage_sirkel(img9, cy=24.5, radius=5.8, belly_color=(46, 14, 22, 255), border_color=(28, 8, 14, 255))
    skins["strawberry"] = img9

    # 10. 🐻 BJØRN (Teddy) - NÅ MED MØRK, KONTRASTRIK SJOKOLADEMAGE!
    img10 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kropp10 = lag_base_kropp(start_y=7, end_y=33)
    bjorn_brun = (175, 115, 65, 255)
    bjorn_snute = (235, 195, 145, 255)
    bjorn_kant = (45, 25, 15, 255)

    for ex, ey in [(6, 4), (7, 4), (8, 4), (5, 5), (6, 5), (7, 5), (8, 5), (5, 6), (6, 6), (7, 6), (8, 6)]:
        img10.putpixel((ex, ey), bjorn_brun)
    for ex, ey in [(7, 5), (7, 6)]:
        img10.putpixel((ex, ey), bjorn_snute)

    for ex, ey in [(19, 4), (20, 4), (21, 4), (19, 5), (20, 5), (21, 5), (22, 5), (19, 6), (20, 6), (21, 6), (22, 6)]:
        img10.putpixel((ex, ey), bjorn_brun)
    for ex, ey in [(20, 5), (20, 6)]:
        img10.putpixel((ex, ey), bjorn_snute)

    for y in range(H):
        for x in range(W):
            if kropp10[y][x]:
                er_kant = (x == 0 or not kropp10[y][x-1] or x == W-1 or not kropp10[y][x+1] or
                           y == 0 or not kropp10[y-1][x] or y == H-1 or not kropp10[y+1][x])
                img10.putpixel((x, y), bjorn_kant if er_kant else bjorn_brun)

    tegn_ansikt(img10, eye_y=12, eye_h=3)
    for sx in (12, 13, 14, 15):
        for sy in (15, 16):
            img10.putpixel((sx, sy), bjorn_snute)
    img10.putpixel((13, 15), (30, 20, 15, 255))
    img10.putpixel((14, 15), (30, 20, 15, 255))

    # Mørk sjokoladebrun mage for bjørnen (gjør teksten krystallklar!)
    tegn_mage_sirkel(img10, cy=24.5, radius=5.8, belly_color=(46, 26, 14, 255), border_color=(28, 16, 8, 255))
    skins["bear"] = img10

    # Skaler og lagre alle 10 bildene
    for navn, bilde in skins.items():
        sti = f"skins/{navn}.png"
        forstorret = bilde.resize((W * SCALE, H * SCALE), Image.Resampling.NEAREST)
        forstorret.save(sti)

    print("Alle 10 pixel art skins er oppdatert med mørke, høykontrast mager!")


def lagre_wav(filsti, lyd_data, sr=44100):
    with wave.open(filsti, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(lyd_data)

def bygg_alle_lyder():
    sr = 44100

    # 1. 🥑 Avokado: 'Pop' & 'Squish'
    dur = 0.5
    tot = int(sr * dur)
    data = bytearray()
    for i in range(tot):
        t = i / float(tot)
        freq = 300 + 900 * (t ** 2)
        amp = math.exp(-6.0 * t)
        val = int(math.sin(2 * math.pi * freq * (i / sr)) * amp * 28000)
        data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/avocado.wav", data, sr)

    # 2. 🐱 Katt: 'Mjau'
    dur = 0.9
    tot = int(sr * dur)
    data = bytearray()
    for i in range(tot):
        t = i / float(tot)
        freq = 420 + 320 * math.sin(math.pi * t)
        phase = 2 * math.pi * freq * (i / sr)
        amp = math.sin(math.pi * t) * math.exp(-1.5 * t)
        sample = (math.sin(phase) + 0.45 * math.sin(2 * phase) + 0.2 * math.sin(3 * phase)) / 1.65
        val = int(sample * amp * 27000)
        data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/cat.wav", data, sr)

    # 3. 🐶 Hund: 'Voff-Voff'
    dur = 0.7
    tot = int(sr * dur)
    data = bytearray()
    for i in range(tot):
        t = i / float(tot)
        sub_t = (t % 0.35) / 0.35
        freq = 360 - 140 * sub_t
        phase = 2 * math.pi * freq * (i / sr)
        amp = math.sin(math.pi * sub_t) * math.exp(-3.0 * sub_t)
        sample = math.sin(phase) + 0.3 * math.sin(2 * phase)
        val = int(sample * amp * 26000)
        data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/dog.wav", data, sr)

    # 4. 🐸 Frosk: 'Kvekk-Kvekk'
    dur = 0.6
    tot = int(sr * dur)
    data = bytearray()
    for i in range(tot):
        t = i / float(tot)
        sub_t = (t % 0.3) / 0.3
        freq = 160 + 40 * math.sin(2 * math.pi * 35 * sub_t)
        phase = 2 * math.pi * freq * (i / sr)
        amp = math.sin(math.pi * sub_t) * math.exp(-2.5 * sub_t)
        sample = math.sin(phase) + 0.5 * math.sin(3 * phase)
        val = int(sample * amp * 26000)
        data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/frog.wav", data, sr)

    # 5. 🦆 And: 'Kvakk-Kvakk'
    dur = 0.65
    tot = int(sr * dur)
    data = bytearray()
    for i in range(tot):
        t = i / float(tot)
        sub_t = (t % 0.32) / 0.32
        freq = 480 - 180 * sub_t
        phase = 2 * math.pi * freq * (i / sr)
        amp = math.sin(math.pi * sub_t) * math.exp(-2.0 * sub_t)
        sample = math.sin(phase) + 0.6 * math.sin(2 * phase) + 0.4 * math.sin(3 * phase)
        val = int(sample * amp * 25000)
        data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/duck.wav", data, sr)

    # 6. 🐼 Panda: 'Mums / Sprø bambus-chime'
    dur = 0.8
    tot = int(sr * dur)
    data = bytearray()
    chords = [523.25, 659.25, 783.99, 1046.50]
    seg = tot // len(chords)
    for idx, f in enumerate(chords):
        for s in range(seg):
            st = s / float(seg)
            amp = math.exp(-3.5 * st)
            phase = 2 * math.pi * f * (s / sr)
            val = int(math.sin(phase) * amp * 24000)
            data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/panda.wav", data, sr)

    # 7. 🤖 Robot: 'Beep-Boop-Bop'
    dur = 0.6
    tot = int(sr * dur)
    data = bytearray()
    robot_freks = [440, 880, 1320, 1760]
    seg = tot // len(robot_freks)
    for idx, f in enumerate(robot_freks):
        for s in range(seg):
            sample = 1.0 if (math.sin(2 * math.pi * f * (s / sr)) > 0) else -1.0
            amp = math.exp(-2.0 * (s / float(seg)))
            val = int(sample * amp * 20000)
            data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/robot.wav", data, sr)

    # 8. 👻 Spøkelse: 'Woooo-Oooo'
    dur = 1.0
    tot = int(sr * dur)
    data = bytearray()
    for i in range(tot):
        t = i / float(tot)
        vibrato = math.sin(2 * math.pi * 6.0 * t) * 45
        freq = 550 + math.sin(math.pi * t) * 150 + vibrato
        amp = math.sin(math.pi * t) * 0.9
        sample = math.sin(2 * math.pi * freq * (i / sr))
        val = int(sample * amp * 26000)
        data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/ghost.wav", data, sr)

    # 9. 🍓 Jordbær: 'Krystall-bjelle / Ding'
    dur = 0.9
    tot = int(sr * dur)
    data = bytearray()
    for i in range(tot):
        t = i / float(tot)
        amp = math.exp(-4.0 * t)
        sample = (math.sin(2 * math.pi * 1200 * (i / sr)) +
                  0.5 * math.sin(2 * math.pi * 2400 * (i / sr)) +
                  0.25 * math.sin(2 * math.pi * 3600 * (i / sr))) / 1.75
        val = int(sample * amp * 27000)
        data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/strawberry.wav", data, sr)

    # 10. 🐻 Bjørn: 'Varm bjørnebrum & harpe'
    dur = 0.9
    tot = int(sr * dur)
    data = bytearray()
    for i in range(tot):
        t = i / float(tot)
        freq = 180 + 90 * math.sin(math.pi * t)
        amp = math.sin(math.pi * t) * math.exp(-1.5 * t)
        phase = 2 * math.pi * freq * (i / sr)
        sample = math.sin(phase) + 0.4 * math.sin(2 * phase)
        val = int(sample * amp * 27000)
        data.extend(struct.pack('<h', max(-32767, min(32767, val))))
    lagre_wav("skins/bear.wav", data, sr)


if __name__ == "__main__":
    bygg_alle_skins()
    bygg_alle_lyder()
