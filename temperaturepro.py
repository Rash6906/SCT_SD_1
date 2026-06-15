import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import csv
import random
import os
from datetime import datetime
import math
import tempfile

# ---------------- APPEARANCE ---------------- #
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

history = []
favorites = []
conversion_history_c = []

# Colors - WCAG-friendly, Tkinter-safe 6-digit hex
DARK_BG = "#0b0e14"
CARD_BG_DARK = "#141821"
CARD_BG_LIGHT = "#ffffff"
ACCENT = "#FF4F81"
ACCENT_HOVER = "#FF7AAE"
ACCENT_GLOW = "#FF9ABB"
GOLD_DARK = "#FFD700"
GOLD_LIGHT = "#A16207"
TEXT_MUTED_DARK = "#aab0bc"
TEXT_MUTED_LIGHT = "#374151"
TEXT_SECONDARY_LIGHT = "#4b5563"
LIGHT_BG = "#eef1f6"
LIGHT_TEXT = "#0f172a"

UNITS = ["Celsius", "Fahrenheit", "Kelvin"]

def to_celsius(val, unit):
    if unit == "Celsius": return val
    if unit == "Fahrenheit": return (val - 32) * 5/9
    if unit == "Kelvin": return val - 273.15
    return val

def from_celsius(c, unit):
    if unit == "Celsius": return c
    if unit == "Fahrenheit": return c * 9/5 + 32
    if unit == "Kelvin": return c + 273.15
    return c

FORMULAS = {
    ("Celsius", "Fahrenheit"): "°F = (°C × 9/5) + 32",
    ("Celsius", "Kelvin"): "K = °C + 273.15",
    ("Fahrenheit", "Celsius"): "°C = (°F - 32) × 5/9",
    ("Fahrenheit", "Kelvin"): "K = (°F - 32) × 5/9 + 273.15",
    ("Kelvin", "Celsius"): "°C = K - 273.15",
    ("Kelvin", "Fahrenheit"): "°F = (K - 273.15) × 9/5 + 32",
}

def get_formula(f, t):
    if f == t: return f"{f} = {t}"
    return FORMULAS.get((f, t), f"{f} → {t}")

# ---------------- MAIN APP ---------------- #
def launch_main_app():
    root = ctk.CTk()
    root.title("Temperature Converter Pro V6")
    root.geometry("1200x740")
    root.minsize(980, 640)

    live_var = ctk.BooleanVar(value=True)
    prec_var = ctk.StringVar(value="2")
    last_result = {"text": "", "value": 0.0}

    # ---------- Aurora + Stars + Glass Bubbles Background ---------- #
    bg_canvas = tk.Canvas(root, highlightthickness=0, bg=DARK_BG)
    bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

    stars = [{"x": random.randint(0,1400), "y": random.randint(0,800),
              "s": random.uniform(1.0, 2.6), "phase": random.random()*6.28}
             for _ in range(90)]

    bubbles = []
    for _ in range(18):
        bubbles.append({
            "x": random.randint(0, 1200),
            "y": random.randint(0, 800),
            "r": random.randint(26, 68),
            "vy": random.uniform(0.4, 1.1),
            "vx": random.uniform(-0.35, 0.35),
            "sway": random.uniform(0.6, 1.6),
            "phase": random.random()*6.28
        })

    aurora_t = {"v": 0}
    bg_after_id = {"id": None}

    def animate_bg():
        if not bg_canvas.winfo_exists():
            return
        is_light = ctk.get_appearance_mode() == "Light"
        bg_col = LIGHT_BG if is_light else DARK_BG
        bg_canvas.configure(bg=bg_col)
        bg_canvas.delete("all")
        w = root.winfo_width() or 1200
        h = root.winfo_height() or 740
        aurora_t["v"] += 0.022

        if not is_light:
            aurora_colors = ["#1a1f3a", "#1e2d4a", "#2a1f3d", "#1f3a3a"]
            bubble_outline = "#3a4155"
            bubble_highlight = "#252a38"
            specular_col = "#4a5266"
            star_col = "#b8c0d0"
            bubble_stipple = "gray25"
            bubble_width = 2
        else:
            aurora_colors = ["#bfdbfe", "#fbcfe8", "#c7d2fe", "#bae6fd"]
            bubble_outline = "#8b97ad"
            bubble_highlight = "#ffffff"
            specular_col = "#ffffff"
            star_col = "#6b7280"
            bubble_stipple = ""
            bubble_width = 2

        for i, col in enumerate(aurora_colors):
            offset = math.sin(aurora_t["v"] + i*1.2) * 60
            y0 = h*0.15 + i*85 + offset
            points = []
            for x in range(0, w+40, 35):
                wave = math.sin((x*0.008) + aurora_t["v"]*1.7 + i) * 45
                points.extend([x, y0 + wave])
            points.extend([w, h, 0, h])
            bg_canvas.create_polygon(points, fill=col, outline="", smooth=True)

        t = aurora_t["v"]*2.5
        for st in stars:
            tw = 0.5 + 0.5 * math.sin(t + st["phase"])
            s = st["s"] * (0.7 + tw*0.6)
            x, y = st["x"] % w, st["y"] % h
            bg_canvas.create_oval(x-s, y-s, x+s, y+s, fill=star_col, outline="")

        for b in bubbles:
            b["y"] -= b["vy"]
            b["x"] += b["vx"] + math.sin(t*b["sway"] + b["phase"]) * 0.45
            if b["y"] < -b["r"]*2:
                b["y"] = h + b["r"]
                b["x"] = random.randint(0, w)
            if b["x"] < -80: b["x"] = w + 40
            if b["x"] > w + 80: b["x"] = -40
            x, y, r = b["x"], b["y"], b["r"]
            bg_canvas.create_oval(x, y, x+r*2, y+r*2, fill="", outline=bubble_outline, width=bubble_width)
            bg_canvas.create_oval(x+r*0.25, y+r*0.2, x+r*0.7, y+r*0.6,
                                  fill=bubble_highlight, outline="", stipple=bubble_stipple)
            bg_canvas.create_oval(x+r*0.3, y+r*0.25, x+r*0.5, y+r*0.45,
                                  fill=specular_col, outline="")

        bg_after_id["id"] = root.after(30, animate_bg)

    # ---------- helpers ---------- #
    def is_light_mode():
        return ctk.get_appearance_mode() == "Light"

    def result_color():
        return GOLD_LIGHT if is_light_mode() else GOLD_DARK

    def muted_color():
        return TEXT_MUTED_LIGHT if is_light_mode() else TEXT_MUTED_DARK

    def text_color():
        return LIGHT_TEXT if is_light_mode() else "#ffffff"

    def card_color():
        return CARD_BG_LIGHT if is_light_mode() else CARD_BG_DARK

    def show_toast(msg, color=ACCENT):
        toast = ctk.CTkFrame(root, fg_color=color, corner_radius=10)
        ctk.CTkLabel(toast, text=msg, font=("Segoe UI", 13, "bold"), text_color="white").pack(padx=18, pady=8)
        toast.place(relx=0.97, rely=0.06, anchor="ne")
        root.after(1800, toast.destroy)

    # ---------- chart ---------- #
    chart_anim_job = {"id": None}
    def update_chart(animated=True):
        if not chart_canvas.winfo_exists(): return
        if chart_anim_job["id"]:
            try: root.after_cancel(chart_anim_job["id"])
            except: pass
        chart_canvas.delete("all")
        w, h = 330, 140
        bg = card_color()
        grid_col = "#cbd5e1" if is_light_mode() else "#232836"
        chart_canvas.configure(bg=bg)

        if len(conversion_history_c) < 2:
            chart_canvas.create_text(w//2, h//2, text="Convert to see trend",
                fill=muted_color(), font=("Segoe UI", 10))
            return

        data = conversion_history_c[-15:]
        n = len(data)
        min_v, max_v = min(data), max(data)
        if max_v == min_v: max_v += 1; min_v -= 1
        pad = (max_v - min_v) * 0.15; min_v -= pad; max_v += pad
        left, right, top, bottom = 42, 10, 15, 25
        plot_w = w - left - right; plot_h = h - top - bottom

        for i in range(4):
            y = top + plot_h * i / 3
            chart_canvas.create_line(left, y, w-right, y, fill=grid_col)
            val = max_v - (max_v - min_v) * i / 3
            chart_canvas.create_text(left-6, y, text=f"{val:.0f}°", anchor="e",
                fill=muted_color(), font=("Segoe UI", 8))

        points = []
        for i, v in enumerate(data):
            x = left + plot_w * i / max(n-1, 1)
            y = top + plot_h * (max_v - v) / (max_v - min_v)
            points.append((x, y))

        def draw_step(k):
            if not chart_canvas.winfo_exists(): return
            chart_canvas.delete("chart_line")
            if k >= 2:
                flat = []
                for px, py in points[:k]: flat.extend([px, py])
                chart_canvas.create_line(*flat, fill=ACCENT, width=2.5, smooth=True, tags="chart_line")
                for px, py in points[:k]:
                    chart_canvas.create_oval(px-3, py-3, px+3, py+3, fill=ACCENT, outline="", tags="chart_line")
            if k < len(points) and animated:
                chart_anim_job["id"] = root.after(42, lambda: draw_step(k+1))

        draw_step(len(points) if not animated else 2)

    # ---------- convert ---------- #
    result_anim_job = {"id": None}
    def animate_result(from_val, to_val, temp_str, from_u, to_u, prec, steps=18):
        if result_anim_job["id"]:
            try: root.after_cancel(result_anim_job["id"])
            except: pass
        def step(i):
            if not result_label.winfo_exists(): return
            t = i / steps
            t = 1 - (1-t)**3
            cur = from_val + (to_val - from_val) * t
            fmt = f"{{:.{prec}f}}"
            txt = f"{temp_str}° {from_u} = {fmt.format(cur)}° {to_u}"
            result_label.configure(text=txt, text_color=result_color())
            if i < steps:
                result_anim_job["id"] = root.after(16, lambda: step(i+1))
        step(0)

    def convert_temperature(add_to_history=True):
        try:
            s = temp_entry.get().strip()
            if not s:
                result_label.configure(text="Result will appear here", text_color=muted_color())
                formula_label.configure(text="Enter a value to see formula")
                return False
            temp = float(s)
            from_u = from_combo.get()
            to_u = to_combo.get()
            prec = int(prec_var.get())

            if from_u == "Kelvin" and temp < 0:
                show_toast("Kelvin cannot be < 0", "#e53935"); return False

            c = to_celsius(temp, from_u)
            result = from_celsius(c, to_u) if from_u!= to_u else temp

            old_val = last_result.get("value", result)
            if abs(old_val - result) > 500: old_val = result
            last_result["value"] = result

            fmt = f"{{:.{prec}f}}"
            temp_str = fmt.format(temp)
            animate_result(old_val, result, temp_str, from_u, to_u, prec)

            formula_label.configure(text=get_formula(from_u, to_u))
            copy_btn.configure(state="normal")
            fav_btn.configure(state="normal")

            if not conversion_history_c or abs(conversion_history_c[-1] - c) > 0.01:
                conversion_history_c.append(round(c, 2))
                if len(conversion_history_c) > 50: conversion_history_c.pop(0)
                update_chart(animated=True)

            if add_to_history:
                result_text = f"{fmt.format(temp)}° {from_u} = {fmt.format(result)}° {to_u}"
                last_result["text"] = result_text
                ts = datetime.now().strftime("%H:%M:%S")
                entry = f"[{ts}] {result_text}"
                if not history or history[-1]!= entry:
                    history.append(entry)
                    refresh_history(True)
            else:
                last_result["text"] = f"{fmt.format(temp)}° {from_u} = {fmt.format(result)}° {to_u}"
            return True
        except ValueError:
            if temp_entry.get().strip() and add_to_history:
                show_toast("Enter a valid number", "#e53935")
            return False

    def on_type(e=None):
        if live_var.get(): convert_temperature(add_to_history=False)

    def set_preset(val, name):
        from_combo.set("Celsius")
        temp_entry.delete(0, "end")
        temp_entry.insert(0, str(val))
        show_toast(name)
        convert_temperature(True)

    def clear_fields():
        temp_entry.delete(0, "end")
        result_label.configure(text="Result will appear here", text_color=muted_color())
        formula_label.configure(text="Enter a value to see formula")
        copy_btn.configure(state="disabled")
        fav_btn.configure(state="disabled")
        temp_entry.focus()

    def copy_result():
        t = last_result["text"]
        if t:
            root.clipboard_clear(); root.clipboard_append(t)
            show_toast("Copied!", "#2e7d32")

    def toggle_fav():
        t = last_result["text"]
        if not t: return
        if t in favorites:
            favorites.remove(t); show_toast("Removed from favorites")
        else:
            favorites.append(t); show_toast("Added to favorites", "#2e7d32")
        refresh_favorites()

    def swap_units():
        a, b = from_combo.get(), to_combo.get()
        from_combo.set(b); to_combo.set(a)
        convert_temperature(True)

    # ---------- history / export ---------- #
    def refresh_history(flash=False):
        q = search_entry.get().lower()
        history_box.configure(state="normal")
        history_box.delete("1.0", "end")
        for h in history:
            if q in h.lower(): history_box.insert("end", h + "\n")
        history_box.configure(state="disabled")
        history_box.yview_moveto(1.0)

    def clear_history():
        history.clear(); conversion_history_c.clear()
        refresh_history(); update_chart(); show_toast("History cleared")

    def export_txt():
        path = filedialog.asksaveasfilename(defaultextension=".txt",
            filetypes=[("Text files", "*.txt")], initialfile="history.txt")
        if not path: return
        with open(path, "w", encoding="utf-8") as f: f.write("\n".join(history))
        show_toast("TXT saved", "#2e7d32")

    def export_csv():
        path = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")], initialfile="history.csv")
        if not path: return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["Conversion"])
            for item in history: w.writerow([item])
        show_toast("CSV exported", "#2e7d32")

    def export_pdf():
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
        except ImportError:
            messagebox.showerror("PDF Export Missing",
                "reportlab is not installed.\n\npip install reportlab"); return

        path = filedialog.asksaveasfilename(defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Temperature_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not path: return
        try:
            doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
            styles = getSampleStyleSheet()
            elements = []
            elements.append(Paragraph("Temperature Converter Pro V6", styles['Title']))
            elements.append(Paragraph("Developed by Rashmi | SkillCraft Technology", styles['Normal']))
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y %H:%M:%S')}", styles['Normal']))
            elements.append(Spacer(1, 20))

            # History table
            data = [["Time", "Conversion"]]
            for h in history:
                if h.startswith("["):
                    try: tm = h[1:h.index("]")]; conv = h[h.index("]")+1:].strip()
                    except: tm, conv = "", h
                else: tm, conv = "", h
                data.append([tm, conv])
            if len(data) == 1: data.append(["", "No conversions recorded"])
            t = Table(data, colWidths=[60, 440])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FF4F81")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f6f6f6")]),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))

            # --- PDF Graph - fixed ---
            chart_tmp = None
            if len(conversion_history_c) >= 2:
                try:
                    import matplotlib
                    matplotlib.use('Agg')
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(7, 2.6))
                    ax.plot(conversion_history_c, marker='o', color='#FF4F81', linewidth=2)
                    ax.set_title("Conversion Trend (°C)", fontsize=11)
                    ax.set_ylabel("°C")
                    ax.set_xlabel("Conversion #")
                    ax.grid(True, alpha=0.3)
                    plt.tight_layout()
                    fd, chart_tmp = tempfile.mkstemp(suffix=".png")
                    os.close(fd)
                    plt.savefig(chart_tmp, dpi=150)
                    plt.close(fig)
                    elements.append(Paragraph("Conversion Trend", styles['Heading2']))
                    elements.append(Image(chart_tmp, width=450, height=160))
                except Exception as e:
                    elements.append(Paragraph("Conversion Trend", styles['Heading2']))
                    elements.append(Paragraph(f"Chart could not be rendered: {e}. Install matplotlib with: pip install matplotlib", styles['Normal']))
            else:
                elements.append(Paragraph("Conversion Trend", styles['Heading2']))
                elements.append(Paragraph(f"{len(conversion_history_c)} conversion(s) recorded. Convert at least 2 temperatures to see the trend chart in the PDF.", styles['Normal']))

            doc.build(elements)

            # cleanup chart image
            if chart_tmp and os.path.exists(chart_tmp):
                try: os.remove(chart_tmp)
                except: pass

            show_toast("PDF saved!", "#2e7d32")
            messagebox.showinfo("PDF Export", f"PDF saved to:\n{path}\n\nTotal conversions: {len(history)}")
        except Exception as e:
            messagebox.showerror("PDF Error", str(e))

    def refresh_favorites():
        for w in fav_list.winfo_children(): w.destroy()
        if not favorites:
            ctk.CTkLabel(fav_list, text="No favorites yet", text_color=muted_color()).pack(); return
        for fav in favorites[-5:][::-1]:
            lbl = ctk.CTkLabel(fav_list, text="★ " + fav, font=("Segoe UI", 11),
                         wraplength=310, justify="left", text_color=text_color())
            lbl.pack(fill="x", pady=2)

    def show_about():
        win = ctk.CTkToplevel(root); win.title("About"); win.geometry("520x420")
        win.resizable(False, False); win.transient(root); win.grab_set()
        card = ctk.CTkFrame(win, corner_radius=16, fg_color=card_color())
        card.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(card, text="🌡 Temperature Converter Pro", font=("Segoe UI", 22, "bold"), text_color=ACCENT).pack(pady=(25, 4))
        ctk.CTkLabel(card, text="Version 6.3 • Aurora Glass Edition", text_color=muted_color()).pack()
        ctk.CTkLabel(card, text="Developed by Rashmi", font=("Segoe UI", 14, "bold"), text_color=text_color()).pack(pady=(12,2))
        ctk.CTkLabel(card, text="SkillCraft Technology Internship Project", text_color=muted_color()).pack()
        features = (
            "• Celsius / Fahrenheit / Kelvin with live formulas\n"
            "• Aurora glow, glass bubbles, twinkling stars\n"
            "• Animated gradient background\n"
            "• Live convert with count-up animation\n"
            "• History chart, favorites, copy\n"
            "• TXT / CSV / PDF export with graph\n"
            "• Light / Dark theme with high contrast"
        )
        ctk.CTkLabel(card, text=features, font=("Segoe UI", 11), justify="left", text_color=text_color()).pack(pady=18, padx=30)
        ctk.CTkButton(card, text="Close", width=120, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      command=win.destroy).pack(pady=10)

    # ---------- theme toggle ---------- #
    theme_labels = []
    def apply_theme():
        light = is_light_mode()
        card = CARD_BG_LIGHT if light else CARD_BG_DARK
        txt_c = LIGHT_TEXT if light else "#ffffff"
        m_c = TEXT_MUTED_LIGHT if light else TEXT_MUTED_DARK
        sec_bg = "#d8dde6" if light else "#232836"
        sec_hover = "#c5ccd8" if light else "#2e3446"
        border_c = "#b8c0cc" if light else "#2e3446"

        left_card.configure(fg_color=card)
        right_frame.configure(fg_color=card)
        scroll_frame.configure(fg_color=card)

        for b in preset_buttons + [clear_btn, copy_btn, fav_btn, clear_history_btn, swap_btn, about_btn]:
            try: b.configure(fg_color=sec_bg, hover_color=sec_hover, text_color=txt_c)
            except: pass
        about_btn.configure(border_color=border_c)

        for lbl, kind in theme_labels:
            try:
                if not lbl.winfo_exists(): continue
                if kind == "muted":
                    lbl.configure(text_color=m_c)
                else:
                    lbl.configure(text_color=txt_c)
            except: pass

        if "°" in result_label.cget("text"):
            result_label.configure(text_color=result_color())
        else:
            result_label.configure(text_color=m_c)

        update_chart(animated=False)
        refresh_favorites()

    def toggle_mode():
        mode = "light" if mode_switch.get() == 1 else "dark"
        ctk.set_appearance_mode(mode)
        root.after(50, apply_theme)

    def update_time():
        if not time_label.winfo_exists(): return
        time_label.configure(text=datetime.now().strftime("%d %b %Y • %I:%M:%S %p"))
        root.after(1000, update_time)

    def on_close():
        for job in [bg_after_id.get("id"), chart_anim_job.get("id"), result_anim_job.get("id")]:
            try:
                if job: root.after_cancel(job)
            except: pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # ---------- LAYOUT ---------- #
    main_frame = ctk.CTkFrame(root, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=14, pady=14)

    left_card = ctk.CTkFrame(main_frame, fg_color=CARD_BG_DARK, corner_radius=20)
    left_card.pack(side="left", fill="both", expand=True, padx=8, pady=8)

    scroll_frame = ctk.CTkScrollableFrame(left_card, fg_color=CARD_BG_DARK)
    scroll_frame.pack(fill="both", expand=True, padx=8, pady=8)

    right_frame = ctk.CTkFrame(main_frame, width=370, fg_color=CARD_BG_DARK, corner_radius=20)
    right_frame.pack(side="right", fill="y", padx=8, pady=8)
    right_frame.pack_propagate(False)

    # Left content
    title_label = ctk.CTkLabel(scroll_frame, text="🌡 Temperature Converter Pro", font=("Segoe UI", 28, "bold"))
    title_label.pack(pady=(10,4)); theme_labels.append((title_label, "text"))

    subtitle_label = ctk.CTkLabel(scroll_frame, text="Aurora Glass • Fast • Accurate", font=("Segoe UI", 12), text_color=TEXT_MUTED_DARK)
    subtitle_label.pack(pady=(0,14)); theme_labels.append((subtitle_label, "muted"))

    top_ctrl = ctk.CTkFrame(scroll_frame, fg_color="transparent"); top_ctrl.pack(pady=4)
    enter_label = ctk.CTkLabel(top_ctrl, text="Enter Temperature", font=("Segoe UI", 13))
    enter_label.pack(side="left", padx=8); theme_labels.append((enter_label, "text"))
    live_check = ctk.CTkCheckBox(top_ctrl, text="Live convert", variable=live_var)
    live_check.pack(side="left", padx=12)
    prec_label = ctk.CTkLabel(top_ctrl, text="Precision:")
    prec_label.pack(side="left", padx=(12,4)); theme_labels.append((prec_label, "text"))
    prec_menu = ctk.CTkOptionMenu(top_ctrl, values=["0","1","2","3","4"], variable=prec_var, width=60,
                                  command=lambda _: convert_temperature(True))
    prec_menu.pack(side="left")

    temp_entry = ctk.CTkEntry(scroll_frame, width=400, height=50, font=("Segoe UI", 18),
                              placeholder_text="e.g. 25", justify="center")
    temp_entry.pack(pady=8)
    temp_entry.bind("<KeyRelease>", on_type)

    preset_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent"); preset_frame.pack(pady=4)
    preset_buttons = []
    presets = [("Freezing 0°C", 0), ("Room 25°C", 25), ("Body 37°C", 37), ("Boiling 100°C", 100)]
    for i, (name, val) in enumerate(presets):
        b = ctk.CTkButton(preset_frame, text=name, width=115, height=30,
            fg_color="#232836", hover_color="#2e3446",
            command=lambda v=val, n=name: set_preset(v, n))
        b.grid(row=0, column=i, padx=4); preset_buttons.append(b)

    units_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent"); units_frame.pack(pady=10)
    from_box = ctk.CTkFrame(units_frame, fg_color="transparent"); from_box.grid(row=0, column=0, padx=15)
    from_text_label = ctk.CTkLabel(from_box, text="From", text_color=TEXT_MUTED_DARK)
    from_text_label.pack(); theme_labels.append((from_text_label, "muted"))
    from_combo = ctk.CTkComboBox(from_box, values=UNITS, width=150, command=lambda _: convert_temperature(True)); from_combo.pack(pady=4); from_combo.set("Celsius")
    swap_btn = ctk.CTkButton(units_frame, text="⇄", width=44, height=34, font=("Segoe UI", 16, "bold"),
        fg_color="#232836", hover_color="#2e3446", command=swap_units)
    swap_btn.grid(row=0, column=1, padx=6, pady=(18,0))
    to_box = ctk.CTkFrame(units_frame, fg_color="transparent"); to_box.grid(row=0, column=2, padx=15)
    to_text_label = ctk.CTkLabel(to_box, text="To", text_color=TEXT_MUTED_DARK)
    to_text_label.pack(); theme_labels.append((to_text_label, "muted"))
    to_combo = ctk.CTkComboBox(to_box, values=UNITS, width=150, command=lambda _: convert_temperature(True)); to_combo.pack(pady=4); to_combo.set("Fahrenheit")

    btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent"); btn_frame.pack(pady=14)
    convert_btn = ctk.CTkButton(btn_frame, text="Convert", width=170, height=44, font=("Segoe UI", 14, "bold"),
        fg_color=ACCENT, hover_color=ACCENT_HOVER, command=lambda: convert_temperature(True))
    convert_btn.grid(row=0, column=0, padx=8)
    clear_btn = ctk.CTkButton(btn_frame, text="Clear", width=170, height=44,
        fg_color="#232836", hover_color="#2e3446", command=clear_fields)
    clear_btn.grid(row=0, column=1, padx=8)

    # hover glow pulse
    glow_job = {"active": False}
    def start_glow():
        glow_job["active"] = True
        def pulse(on=True):
            if not glow_job["active"] or not convert_btn.winfo_exists():
                try: convert_btn.configure(fg_color=ACCENT)
                except: pass
                return
            convert_btn.configure(fg_color=ACCENT_HOVER if on else ACCENT_GLOW)
            root.after(150, lambda: pulse(not on))
        pulse(True)
    def stop_glow(e=None): glow_job["active"] = False; convert_btn.configure(fg_color=ACCENT)
    convert_btn.bind("<Enter>", lambda e: start_glow())
    convert_btn.bind("<Leave>", stop_glow)

    result_label = ctk.CTkLabel(scroll_frame, text="Result will appear here", font=("Segoe UI", 22, "bold"),
                                text_color=TEXT_MUTED_DARK, wraplength=560)
    result_label.pack(pady=(10,4))
    formula_label = ctk.CTkLabel(scroll_frame, text="Enter a value to see formula",
                                 font=("Segoe UI", 11), text_color=TEXT_MUTED_DARK)
    formula_label.pack(); theme_labels.append((formula_label, "muted"))

    action_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent"); action_frame.pack(pady=10)
    copy_btn = ctk.CTkButton(action_frame, text="📋 Copy", width=140, state="disabled",
        fg_color="#232836", hover_color="#2e3446", command=copy_result)
    copy_btn.grid(row=0, column=0, padx=6)
    fav_btn = ctk.CTkButton(action_frame, text="☆ Favorite", width=140, state="disabled",
        fg_color="#232836", hover_color="#2e3446", command=toggle_fav)
    fav_btn.grid(row=0, column=1, padx=6)

    bottom_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent"); bottom_frame.pack(pady=18)
    mode_switch = ctk.CTkSwitch(bottom_frame, text="Light Mode", command=toggle_mode, progress_color=ACCENT)
    mode_switch.grid(row=0, column=0, padx=18)
    about_btn = ctk.CTkButton(bottom_frame, text="ℹ About", width=100, fg_color="transparent", border_width=1,
        text_color=("#0f172a", "#ffffff"), border_color=("#c8cdd7", "#2e3446"),
        hover_color=("#e2e6ee", "#232836"), command=show_about)
    about_btn.grid(row=0, column=1, padx=18)

    time_label = ctk.CTkLabel(scroll_frame, text="", text_color=TEXT_MUTED_DARK)
    time_label.pack(pady=4); theme_labels.append((time_label, "muted"))
    footer_label = ctk.CTkLabel(scroll_frame, text="Developed by Rashmi | SkillCraft Internship Project",
        text_color=TEXT_MUTED_DARK)
    footer_label.pack(pady=(4, 20)); theme_labels.append((footer_label, "muted"))

    # Right panel
    history_title = ctk.CTkLabel(right_frame, text="📜 Conversion History", font=("Segoe UI", 18, "bold"))
    history_title.pack(pady=(16,6)); theme_labels.append((history_title, "text"))

    search_entry = ctk.CTkEntry(right_frame, placeholder_text="Search history...", width=330)
    search_entry.pack(pady=4); search_entry.bind("<KeyRelease>", lambda e: refresh_history())
    history_box = ctk.CTkTextbox(right_frame, width=330, height=170, font=("Consolas", 11))
    history_box.pack(padx=14, pady=6)

    hist_btns = ctk.CTkFrame(right_frame, fg_color="transparent"); hist_btns.pack(fill="x", padx=14, pady=4)
    ctk.CTkButton(hist_btns, text="📄 TXT", fg_color=ACCENT, hover_color=ACCENT_HOVER, command=export_txt).pack(side="left", padx=2, expand=True, fill="x")
    ctk.CTkButton(hist_btns, text="📊 CSV", fg_color=ACCENT, hover_color=ACCENT_HOVER, command=export_csv).pack(side="left", padx=2, expand=True, fill="x")
    clear_history_btn = ctk.CTkButton(hist_btns, text="🗑 Clear", fg_color="#232836", hover_color="#2e3446", command=clear_history)
    clear_history_btn.pack(side="left", padx=2, expand=True, fill="x")

    pdf_btn = ctk.CTkButton(right_frame, text="📕 Export PDF Report", fg_color="#2e7d32", hover_color="#388e3c",
        command=export_pdf)
    pdf_btn.pack(fill="x", padx=14, pady=6)

    chart_title = ctk.CTkLabel(right_frame, text="📈 Conversion Trend (°C)", font=("Segoe UI", 14, "bold"))
    chart_title.pack(pady=(8,2)); theme_labels.append((chart_title, "text"))

    chart_canvas = tk.Canvas(right_frame, width=330, height=140, highlightthickness=0, bg=CARD_BG_DARK)
    chart_canvas.pack(padx=14, pady=4)

    fav_title = ctk.CTkLabel(right_frame, text="☆ Favorites", font=("Segoe UI", 14, "bold"))
    fav_title.pack(pady=(8,2)); theme_labels.append((fav_title, "text"))

    fav_list = ctk.CTkFrame(right_frame, fg_color="transparent")
    fav_list.pack(fill="both", expand=True, padx=14, pady=4)

    # initial theme sync
    apply_theme()
    update_chart(False)
    refresh_favorites(); refresh_history()

    root.bind("<Return>", lambda e: convert_temperature(True))
    root.bind("<Control-l>", lambda e: clear_fields())
    temp_entry.focus()
    update_time()
    animate_bg()
    root.mainloop()

# ---------------- SPLASH ---------------- #
splash = ctk.CTk(); splash.overrideredirect(True); splash.geometry("520x300")
splash.update_idletasks()
x = (splash.winfo_screenwidth() // 2) - 260
y = (splash.winfo_screenheight() // 2) - 150
splash.geometry(f"+{x}+{y}"); splash.configure(fg_color=DARK_BG)

card = ctk.CTkFrame(splash, fg_color=CARD_BG_DARK, corner_radius=20)
card.pack(fill="both", expand=True, padx=20, pady=20)
splash_title = ctk.CTkLabel(card, text="🌡 Temperature Converter Pro", font=("Segoe UI", 24, "bold"), text_color=ACCENT)
splash_title.pack(pady=(50, 8))
ctk.CTkLabel(card, text="V6.3 • Aurora Glass Edition • by Rashmi", text_color=TEXT_MUTED_DARK).pack()
progress = ctk.CTkProgressBar(card, width=340, progress_color=ACCENT); progress.pack(pady=30); progress.set(0)
loading_text = ctk.CTkLabel(card, text="Initializing...", text_color=TEXT_MUTED_DARK); loading_text.pack()

splash_after = {"id": None}
def splash_breathe(step=0):
    if not splash.winfo_exists(): return
    col = ACCENT if math.sin(step*0.18) > 0 else ACCENT_HOVER
    try: splash_title.configure(text_color=col)
    except: return
    splash_after["id"] = splash.after(80, lambda: splash_breathe(step+1))

def animate_splash(v=0):
    if not splash.winfo_exists(): return
    if v > 1.0:
        try:
            if splash_after["id"]: splash.after_cancel(splash_after["id"])
        except: pass
        splash.destroy()
        launch_main_app()
        return
    progress.set(v)
    loading_text.configure(text=f"Loading Aurora... {int(v*100)}%")
    splash.after(16, lambda: animate_splash(v + 0.022))

splash_breathe(); splash.after(200, animate_splash); splash.mainloop()