import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import tkinter as tk
import requests
from bs4 import BeautifulSoup
import re
import threading
import json
import os
import random
from datetime import datetime, timedelta
from urllib.parse import urlparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# ==================== KONFIGURASI ====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Set style matplotlib untuk dark theme
plt.style.use('dark_background')
plt.rcParams['axes.facecolor'] = '#1e1e2e'
plt.rcParams['figure.facecolor'] = '#1e1e2e'
plt.rcParams['grid.color'] = '#2d2d44'
plt.rcParams['text.color'] = '#e0e0e0'
plt.rcParams['axes.labelcolor'] = '#e0e0e0'

HISTORY_FILE = "title_history.json"
API_KEY_FILE = "deepseek_key.txt"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# ==================== KELAS UTAMA ====================
class Athenix:
    def __init__(self, root):
        self.root = root
        self.root.title("Athenix Beta V.0.1.0 - AI Content Creator")
        self.root.geometry("1500x900")
        self.title_history = self.load_history()
        self.api_key = self.load_api_key()
        self.setup_ui()
    
    def load_api_key(self):
        if os.path.exists(API_KEY_FILE):
            try:
                with open(API_KEY_FILE, 'r') as f:
                    return f.read().strip()
            except:
                return ""
        return ""
    
    def save_api_key(self, key):
        try:
            with open(API_KEY_FILE, 'w') as f:
                f.write(key)
            self.api_key = key
            return True
        except:
            return False
    
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_history(self):
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.title_history, f)
        except:
            pass
    
    def add_to_history(self, kategori, judul):
        if kategori not in self.title_history:
            self.title_history[kategori] = []
        if judul not in self.title_history[kategori]:
            self.title_history[kategori].append(judul)
            self.save_history()
    
    def call_deepseek_api(self, prompt, system_prompt="Kamu adalah penulis profesional yang membuat artikel blog berkualitas tinggi dengan bahasa Indonesia yang natural, mendalam, dan informatif."):
        if not self.api_key:
            return None, "API Key belum diisi."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 5000
        }
        
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=120)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'], None
            else:
                return None, f"API Error: {response.status_code}"
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self.main_frame, width=300, corner_radius=15, fg_color="#1a1a2e")
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=20)
        
        logo_label = ctk.CTkLabel(logo_frame, text="⚡", font=ctk.CTkFont(size=36), text_color="#9c27b0")
        logo_label.pack(side="left")
        
        title_label = ctk.CTkLabel(logo_frame, text="Athenix", 
                                   font=ctk.CTkFont(size=22, weight="bold"),
                                   text_color="#ffffff")
        title_label.pack(side="left", padx=(8,0))
        
        # Beta Badge
        beta_badge = ctk.CTkLabel(self.sidebar, text="BETA V.0.1.0", 
                                   font=ctk.CTkFont(size=10, weight="bold"),
                                   text_color="#ffaa44",
                                   fg_color="#2d2d44",
                                   corner_radius=10,
                                   padx=10,
                                   pady=2)
        beta_badge.pack(pady=(5, 5))
        
        # Subtitle
        subtitle = ctk.CTkLabel(self.sidebar, text="AI Content Creator", 
                                font=ctk.CTkFont(size=11), 
                                text_color="#888888")
        subtitle.pack(pady=(0, 15))
        
        # Powered by
        powered_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        powered_frame.pack(pady=(0, 10))
        
        powered_label = ctk.CTkLabel(powered_frame, text="Powered by", 
                                      font=ctk.CTkFont(size=9),
                                      text_color="#666666")
        powered_label.pack(side="left")
        
        lapa_label = ctk.CTkLabel(powered_frame, text=" LapaByt3", 
                                   font=ctk.CTkFont(size=10, weight="bold"),
                                   text_color="#9c27b0")
        lapa_label.pack(side="left")
        
        # Menu
        menus = [
            ("📊", "Dashboard", self.show_dashboard, "#3a6ea5"),
            ("📄", "Paraphrase Artikel", self.show_paraphrase, "#4caf50"),
            ("✨", "Auto Judul Menarik", self.show_title_maker, "#ffaa44"),
            ("🚀", "Generate dari Keyword", self.show_generate, "#9c27b0"),
            ("🎥", "YouTube ke Artikel", self.show_youtube, "#f44336"),
            ("🔍", "Cek Rank Artikel", self.show_rank_checker, "#00bcd4"),
            ("⚙️", "Pengaturan API", self.show_api_settings, "#888888")
        ]
        
        for icon, text, command, color in menus:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {text}",
                command=command,
                height=48,
                corner_radius=12,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#2d2d44",
                hover_color="#3d3d5c",
                anchor="w"
            )
            btn.pack(pady=6, padx=15, fill="x")
            btn.configure(text_color=color)
        
        # Divider
        divider = ctk.CTkFrame(self.sidebar, height=2, fg_color="#2d2d44")
        divider.pack(fill="x", padx=15, pady=15)
        
        # Status API di sidebar
        api_status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        api_status_frame.pack(side="bottom", fill="x", pady=20, padx=15)
        
        api_icon = "🟢" if self.api_key else "🔴"
        api_text = "DeepSeek API: Terhubung" if self.api_key else "DeepSeek API: Belum Diisi"
        api_color = "#4caf50" if self.api_key else "#f44336"
        
        self.sidebar_api_status = ctk.CTkLabel(
            api_status_frame,
            text=f"{api_icon}  {api_text}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=api_color
        )
        self.sidebar_api_status.pack()
        
        # Version
        version_label = ctk.CTkLabel(api_status_frame, text="Athenix Beta v0.1.0", 
                                      font=ctk.CTkFont(size=9),
                                      text_color="#666666")
        version_label.pack(pady=(8,0))
        
        self.content_frame = ctk.CTkFrame(self.main_frame, corner_radius=15, fg_color="#1e1e2e")
        self.content_frame.pack(side="right", fill="both", expand=True)
        self.show_dashboard()
    
    def show_dashboard(self):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(30,10), padx=30)
        
        icon_label = ctk.CTkLabel(header_frame, text="⚡", font=ctk.CTkFont(size=40), text_color="#9c27b0")
        icon_label.pack(side="left")
        
        header = ctk.CTkLabel(header_frame, text="Athenix Dashboard", 
                               font=ctk.CTkFont(size=32, weight="bold"),
                               text_color="#ffffff")
        header.pack(side="left", padx=(12,0))
        
        beta_badge = ctk.CTkLabel(header_frame, text="BETA", 
                                   font=ctk.CTkFont(size=11, weight="bold"),
                                   text_color="#ffaa44",
                                   fg_color="#2d2d44",
                                   corner_radius=12,
                                   padx=10,
                                   pady=4)
        beta_badge.pack(side="left", padx=(12,0))
        
        total_titles = sum(len(titles) for titles in self.title_history.values())
        api_status = "✅ Terhubung" if self.api_key else "❌ Belum Diisi"
        
        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ⚡ ATHENIX - AI CONTENT CREATOR                      ║
║                              Beta Version 0.1.0                              ║
║                           Powered by LapaByt3                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                           ✨ FITUR UNGGULAN ✨                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

📄 PARAPHRASE ARTIKEL (DeepSeek AI)
   → Menulis ulang konten secara profesional dengan bahasa natural
   → Membersihkan metadata (author, tanggal, contact)
   → Hasil rapi dengan paragraf terstruktur

✨ AUTO JUDUL MENARIK (DeepSeek AI)
   → Generate 35 judul UNIK per kategori
   → Setiap kali generate menghasilkan judul yang berbeda
   → SEO-friendly dengan variasi format

🚀 GENERATE DARI KEYWORD (DeepSeek AI)
   → Artikel mendalam 1500-2000 kata
   → Untuk keyword programming: dilengkapi contoh kode dan tips coding
   → Struktur lengkap dengan FAQ dan kesimpulan

🎥 YOUTUBE KE ARTIKEL (DeepSeek AI)
   → Konversi video YouTube menjadi artikel mendalam
   → Panjang artikel 2000-3000 kata
   → Analisis mendalam berdasarkan judul video

🔍 CEK RANK ARTIKEL (DeepSeek AI + Grafik)
   → Analisis SEO score, readability, dan performa artikel
   → Grafik trafik real-time 7 hari terakhir
   → Fitur perbandingan 2 artikel sekaligus

╔══════════════════════════════════════════════════════════════════════════════╗
║                           ⚙️ STATUS SISTEM                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

   • DeepSeek API Status : {api_status}
   • Total Judul Unik    : {total_titles} judul
   • Total Kategori      : {len(self.title_history)} kategori
   • Version             : Beta 0.1.0
   • Powered by          : LapaByt3

╔══════════════════════════════════════════════════════════════════════════════╗
║                           💡 TIPS PENGGUNAAN                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

   1. Pastikan API Key DeepSeek sudah diisi di menu Pengaturan API
   2. Gunakan keyword spesifik untuk hasil terbaik
   3. Fitur YouTube ke Artikel: cukup masukkan URL video
   4. Cek Rank bisa membandingkan 2 artikel sekaligus
   5. Semua hasil bisa langsung copy-paste ke blogmu

────────────────────────────────────────────────────────────────────────────────
              ⚡ Athenix - Write with wisdom. Create with power. ⚡
────────────────────────────────────────────────────────────────────────────────
"""
        info = ctk.CTkTextbox(self.content_frame, font=("Consolas", 11), 
                               fg_color="#2d2d44", text_color="#e0e0e0",
                               corner_radius=15, border_width=0,
                               wrap="word")
        info.pack(fill="both", expand=True, padx=30, pady=15)
        info.insert("0.0", info_text)
        info.configure(state="disabled")
    
    # ==================== PENGATURAN API ====================
    def show_api_settings(self):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(30,10), padx=30)
        
        icon_label = ctk.CTkLabel(header_frame, text="⚙️", font=ctk.CTkFont(size=36), text_color="#888888")
        icon_label.pack(side="left")
        
        header = ctk.CTkLabel(header_frame, text="Pengaturan API", 
                               font=ctk.CTkFont(size=32, weight="bold"),
                               text_color="#ffffff")
        header.pack(side="left", padx=(12,0))
        
        card = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        card.pack(fill="x", padx=30, pady=20)
        
        desc = ctk.CTkLabel(card, 
                            text="Masukkan API Key DeepSeek untuk mengaktifkan semua fitur Athenix AI.\n\nDapatkan API Key gratis di: https://platform.deepseek.com/api_keys",
                            font=ctk.CTkFont(size=13),
                            text_color="#888888",
                            justify="left")
        desc.pack(anchor="w", padx=25, pady=(25,15))
        
        key_label = ctk.CTkLabel(card, text="🔑 DeepSeek API Key", font=ctk.CTkFont(size=15, weight="bold"))
        key_label.pack(anchor="w", padx=25, pady=(10,5))
        
        self.api_key_entry = ctk.CTkEntry(card, width=550, height=50, 
                                           placeholder_text="sk-...",
                                           font=ctk.CTkFont(size=13),
                                           corner_radius=12)
        self.api_key_entry.pack(anchor="w", padx=25, pady=(0,15))
        if self.api_key:
            self.api_key_entry.insert(0, self.api_key)
            # Update status sidebar
            api_icon = "🟢"
            api_text = "DeepSeek API: Terhubung"
            api_color = "#4caf50"
            self.sidebar_api_status.configure(
                text=f"{api_icon}  {api_text}",
                text_color=api_color
            )
        
        save_btn = ctk.CTkButton(card, text="💾 Simpan API Key", 
                                  command=self.save_api_key_settings,
                                  height=45, 
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  corner_radius=12,
                                  fg_color="#3a6ea5",
                                  hover_color="#2c5a8c")
        save_btn.pack(pady=15, padx=25)
        
        self.api_status = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12))
        self.api_status.pack(pady=(0,25))
        
        info_card = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        info_card.pack(fill="x", padx=30, pady=15)
        
        info_title = ctk.CTkLabel(info_card, text="ℹ️ Informasi API", 
                                   font=ctk.CTkFont(size=16, weight="bold"),
                                   text_color="#ffffff")
        info_title.pack(anchor="w", padx=25, pady=(20,10))
        
        info_text = """• API Key bersifat rahasia, jangan bagikan ke orang lain
• Kuota gratis DeepSeek sangat besar untuk kebutuhan blogging
• Jika mengalami error, pastikan format API Key benar (sk-...)
• API Key disimpan lokal di komputer Anda"""
        
        info_desc = ctk.CTkLabel(info_card, text=info_text, 
                                  font=ctk.CTkFont(size=12),
                                  text_color="#888888",
                                  justify="left")
        info_desc.pack(anchor="w", padx=25, pady=(0,25))
    
    def save_api_key_settings(self):
        key = self.api_key_entry.get().strip()
        if key:
            if self.save_api_key(key):
                self.api_status.configure(text="✅ API Key berhasil disimpan!", text_color="#4caf50")
                # Update sidebar status
                api_icon = "🟢"
                api_text = "DeepSeek API: Terhubung"
                api_color = "#4caf50"
                self.sidebar_api_status.configure(
                    text=f"{api_icon}  {api_text}",
                    text_color=api_color
                )
            else:
                self.api_status.configure(text="❌ Gagal menyimpan API Key", text_color="#f44336")
        else:
            self.api_status.configure(text="⚠️ Masukkan API Key terlebih dahulu", text_color="#ffaa44")
    
    # ==================== GENERATE DARI KEYWORD ====================
    def show_generate(self):
        self.clear_content()
        
        # Header
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20,5), padx=30)
        
        icon_label = ctk.CTkLabel(header_frame, text="🚀", font=ctk.CTkFont(size=36), text_color="#9c27b0")
        icon_label.pack(side="left")
        
        header = ctk.CTkLabel(header_frame, text="Generate dari Keyword", 
                               font=ctk.CTkFont(size=28, weight="bold"),
                               text_color="#ffffff")
        header.pack(side="left", padx=(12,0))
        
        badge = ctk.CTkLabel(header_frame, text="Athenix AI", 
                              font=ctk.CTkFont(size=11, weight="bold"),
                              text_color="#ffaa44",
                              fg_color="#2d2d44",
                              corner_radius=12,
                              padx=10,
                              pady=3)
        badge.pack(side="left", padx=(12,0))
        
        desc = ctk.CTkLabel(self.content_frame, 
                            text="Masukkan kata kunci, Athenix AI akan membuat artikel mendalam (1500-2000 kata).",
                            font=ctk.CTkFont(size=12),
                            text_color="#888888",
                            justify="left")
        desc.pack(anchor="w", padx=30, pady=(5,15))
        
        # Card Input
        input_card = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        input_card.pack(fill="x", padx=30, pady=5)
        
        keyword_label = ctk.CTkLabel(input_card, text="📌 Kata Kunci", 
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      text_color="#ffffff")
        keyword_label.pack(anchor="w", padx=20, pady=(15,8))
        
        self.gen_keyword = ctk.CTkEntry(input_card, 
                                         placeholder_text="Contoh: Belajar Python, AI 2026, Digital Marketing", 
                                         height=50,
                                         font=ctk.CTkFont(size=13),
                                         corner_radius=12,
                                         fg_color="#1e1e2e",
                                         border_color="#3d3d5c",
                                         border_width=2)
        self.gen_keyword.pack(fill="x", padx=20, pady=(0,15))
        
        # Button Row
        button_row = ctk.CTkFrame(input_card, fg_color="transparent")
        button_row.pack(fill="x", padx=20, pady=(0,15))
        
        self.generate_btn = ctk.CTkButton(button_row, 
                                           text="⚡ Generate Artikel dengan Athenix AI", 
                                           command=self.generate_article_with_ai,
                                           height=45,
                                           font=ctk.CTkFont(size=13, weight="bold"),
                                           corner_radius=12,
                                           fg_color="#3a6ea5",
                                           hover_color="#2c5a8c")
        self.generate_btn.pack(side="left", padx=(0,12))
        
        clear_btn = ctk.CTkButton(button_row, 
                                   text="🗑️ Bersihkan", 
                                   command=self.clear_generate_result,
                                   height=45,
                                   font=ctk.CTkFont(size=13),
                                   corner_radius=12,
                                   fg_color="#3d3d5c",
                                   hover_color="#4d4d6c")
        clear_btn.pack(side="left")
        
        info_label = ctk.CTkLabel(button_row, 
                                   text="💡 Artikel 1500-2000 kata | Powered by LapaByt3",
                                   font=ctk.CTkFont(size=10),
                                   text_color="#666666")
        info_label.pack(side="right")
        
        # Progress Section
        progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=30, pady=8)
        
        self.gen_progress = ctk.CTkProgressBar(progress_frame, height=6, corner_radius=3)
        self.gen_progress.pack(fill="x", pady=(0,5))
        self.gen_progress.set(0)
        
        self.gen_status = ctk.CTkLabel(progress_frame, text="", font=ctk.CTkFont(size=11))
        self.gen_status.pack()
        
        # Result Card
        result_card = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        result_card.pack(fill="both", expand=True, padx=30, pady=(8,20))
        
        result_header = ctk.CTkFrame(result_card, fg_color="transparent")
        result_header.pack(fill="x", padx=20, pady=(12,8))
        
        result_title = ctk.CTkLabel(result_header, text="📄 Hasil Artikel (Athenix AI)", 
                                     font=ctk.CTkFont(size=15, weight="bold"),
                                     text_color="#ffffff")
        result_title.pack(side="left")
        
        copy_btn = ctk.CTkButton(result_header, 
                                  text="📋 Copy", 
                                  command=self.copy_generate_result,
                                  width=70,
                                  height=30,
                                  font=ctk.CTkFont(size=11, weight="bold"),
                                  corner_radius=8,
                                  fg_color="#3d3d5c",
                                  hover_color="#4d4d6c")
        copy_btn.pack(side="right")
        
        self.gen_result = ctk.CTkTextbox(result_card, 
                                          font=("Segoe UI", 12),
                                          fg_color="#1e1e2e",
                                          text_color="#e0e0e0",
                                          corner_radius=12,
                                          border_width=0,
                                          wrap="word")
        self.gen_result.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        placeholder = """✨ Hasil artikel akan muncul di sini setelah generate

📌 Athenix AI akan membuat artikel mendalam (1500-2000 kata) dengan struktur lengkap.

📌 CARA MENGGUNAKAN:
   1. Pastikan API Key DeepSeek sudah diisi di menu Pengaturan API
   2. Masukkan kata kunci
   3. Klik tombol 'Generate Artikel dengan Athenix AI'
   4. Tunggu AI membuat artikel lengkap
   5. Artikel siap copy-paste ke blogmu!

⚡ Powered by LapaByt3"""
        
        self.gen_result.insert("0.0", placeholder)
    
    def clear_generate_result(self):
        placeholder = """✨ Hasil artikel akan muncul di sini setelah generate

📌 Athenix AI akan membuat artikel mendalam (1500-2000 kata) dengan struktur lengkap.

📌 CARA MENGGUNAKAN:
   1. Pastikan API Key DeepSeek sudah diisi di menu Pengaturan API
   2. Masukkan kata kunci
   3. Klik tombol 'Generate Artikel dengan Athenix AI'
   4. Tunggu AI membuat artikel lengkap
   5. Artikel siap copy-paste ke blogmu!

⚡ Powered by LapaByt3"""
        
        self.gen_result.delete("0.0", "end")
        self.gen_result.insert("0.0", placeholder)
        self.gen_status.configure(text="", text_color="gray")
        self.gen_progress.set(0)
    
    def copy_generate_result(self):
        text = self.gen_result.get("0.0", "end").strip()
        if text and "Hasil artikel akan muncul di sini" not in text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.gen_status.configure(text="✅ Artikel disalin ke clipboard!", text_color="#4caf50")
            self.root.after(2000, lambda: self.gen_status.configure(text="", text_color="gray"))
        else:
            self.gen_status.configure(text="⚠️ Belum ada artikel untuk disalin", text_color="#ffaa44")
    
    def generate_article_with_ai(self):
        keyword = self.gen_keyword.get().strip()
        if not keyword:
            messagebox.showwarning("Peringatan", "Masukkan kata kunci terlebih dahulu!")
            return
        
        if not self.api_key:
            messagebox.showwarning("Peringatan", "API Key DeepSeek belum diisi!\n\nSilakan isi API Key di menu Pengaturan API terlebih dahulu.")
            return
        
        def process():
            try:
                self.generate_btn.configure(state="disabled", text="⚡ Generating...")
                self.gen_progress.set(0.2)
                self.gen_status.configure(text="🤖 Athenix AI sedang menyusun artikel...", text_color="#3a6ea5")
                
                prompt = f"""Buatlah artikel mendalam tentang "{keyword}" dengan struktur lengkap.

Struktur artikel:
1. JUDUL UTAMA: Buat judul menarik dengan kata kunci di awal
2. PENDAHULUAN: Latar belakang, mengapa topik ini penting
3. APA ITU {keyword}? - Definisi dan konsep dasar
4. MENGAPA {keyword} PENTING? - Manfaat dan kegunaan
5. PEMBAHASAN MENDALAM (3-5 sub-bab)
6. TIPS DAN TRIK PRAKTIS
7. FAQ (Pertanyaan yang sering diajukan)
8. KESIMPULAN DAN AJAKAN BERTINDAK

Gaya penulisan: seperti jurnalis profesional, bahasa Indonesia yang natural dan informatif, panjang artikel 1500-2000 kata."""
                
                result, error = self.call_deepseek_api(prompt)
                
                if error:
                    self.gen_status.configure(text=f"❌ {error}", text_color="#f44336")
                    self.gen_progress.set(0)
                    self.generate_btn.configure(state="normal", text="⚡ Generate Artikel dengan Athenix AI")
                    return
                
                self.gen_progress.set(1.0)
                self.gen_status.configure(text="✅ Artikel mendalam berhasil dibuat!", text_color="#4caf50")
                self.gen_result.delete("0.0", "end")
                self.gen_result.insert("0.0", result)
                self.gen_result.insert("end", "\n\n" + "─"*60 + "\n")
                self.gen_result.insert("end", "✨ Artikel ditulis oleh Athenix AI\n")
                self.gen_result.insert("end", "⚡ Powered by LapaByt3\n")
                
                self.gen_progress.set(0)
            except Exception as e:
                self.gen_status.configure(text=f"❌ Error: {str(e)}", text_color="#f44336")
                self.gen_progress.set(0)
            finally:
                self.generate_btn.configure(state="normal", text="⚡ Generate Artikel dengan Athenix AI")
        
        threading.Thread(target=process, daemon=True).start()
    
    # ==================== PARAPHRASE ARTIKEL ====================
    def show_paraphrase(self):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20,5), padx=30)
        
        icon_label = ctk.CTkLabel(header_frame, text="📄", font=ctk.CTkFont(size=36), text_color="#4caf50")
        icon_label.pack(side="left")
        
        header = ctk.CTkLabel(header_frame, text="Paraphrase Artikel", 
                               font=ctk.CTkFont(size=28, weight="bold"),
                               text_color="#ffffff")
        header.pack(side="left", padx=(12,0))
        
        badge = ctk.CTkLabel(header_frame, text="Athenix AI", 
                              font=ctk.CTkFont(size=11, weight="bold"),
                              text_color="#ffaa44",
                              fg_color="#2d2d44",
                              corner_radius=12,
                              padx=10,
                              pady=3)
        badge.pack(side="left", padx=(12,0))
        
        desc = ctk.CTkLabel(self.content_frame, 
                            text="Athenix AI akan mengambil konten utama, membersihkan metadata, dan menulis ulang dengan bahasa natural.",
                            font=ctk.CTkFont(size=12),
                            text_color="#888888",
                            justify="left")
        desc.pack(anchor="w", padx=30, pady=(5,15))
        
        input_card = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        input_card.pack(fill="x", padx=30, pady=5)
        
        url_label = ctk.CTkLabel(input_card, text="🔗 URL Artikel", 
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  text_color="#ffffff")
        url_label.pack(anchor="w", padx=20, pady=(15,8))
        
        self.url_entry = ctk.CTkEntry(input_card, 
                                       placeholder_text="https://example.com/artikel", 
                                       height=50,
                                       font=ctk.CTkFont(size=13),
                                       corner_radius=12,
                                       fg_color="#1e1e2e",
                                       border_color="#3d3d5c",
                                       border_width=2)
        self.url_entry.pack(fill="x", padx=20, pady=(0,15))
        
        button_row = ctk.CTkFrame(input_card, fg_color="transparent")
        button_row.pack(fill="x", padx=20, pady=(0,15))
        
        self.paraphrase_btn = ctk.CTkButton(button_row, 
                                        text="🔄 Paraphrase dengan Athenix AI", 
                                        command=self.paraphrase_article_deepseek, 
                                        height=45,
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        corner_radius=12,
                                        fg_color="#3a6ea5",
                                        hover_color="#2c5a8c")
        self.paraphrase_btn.pack(side="left", padx=(0,12))
        
        clear_btn = ctk.CTkButton(button_row, 
                                   text="🗑️ Bersihkan", 
                                   command=self.clear_paraphrase_result,
                                   height=45,
                                   font=ctk.CTkFont(size=13),
                                   corner_radius=12,
                                   fg_color="#3d3d5c",
                                   hover_color="#4d4d6c")
        clear_btn.pack(side="left")
        
        info_label = ctk.CTkLabel(button_row, 
                                   text="💡 Athenix AI akan menulis ulang konten | LapaByt3",
                                   font=ctk.CTkFont(size=10),
                                   text_color="#666666")
        info_label.pack(side="right")
        
        progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=30, pady=8)
        
        self.progress = ctk.CTkProgressBar(progress_frame, height=6, corner_radius=3)
        self.progress.pack(fill="x", pady=(0,5))
        self.progress.set(0)
        
        self.status_label = ctk.CTkLabel(progress_frame, text="", font=ctk.CTkFont(size=11))
        self.status_label.pack()
        
        # Result Card
        result_card = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        result_card.pack(fill="both", expand=True, padx=30, pady=(8,20))
        
        result_header = ctk.CTkFrame(result_card, fg_color="transparent")
        result_header.pack(fill="x", padx=20, pady=(12,8))
        
        result_title = ctk.CTkLabel(result_header, text="📄 Hasil Paraphrase (Athenix AI)", 
                                     font=ctk.CTkFont(size=15, weight="bold"),
                                     text_color="#ffffff")
        result_title.pack(side="left")
        
        copy_btn = ctk.CTkButton(result_header, 
                                  text="📋 Copy", 
                                  command=self.copy_paraphrase_result,
                                  width=70,
                                  height=30,
                                  font=ctk.CTkFont(size=11, weight="bold"),
                                  corner_radius=8,
                                  fg_color="#3d3d5c",
                                  hover_color="#4d4d6c")
        copy_btn.pack(side="right")
        
        self.result_text = ctk.CTkTextbox(result_card, 
                                           font=("Segoe UI", 12),
                                           fg_color="#1e1e2e",
                                           text_color="#e0e0e0",
                                           corner_radius=12,
                                           border_width=0,
                                           wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        placeholder = """✨ Hasil paraphrase akan muncul di sini setelah diproses

📌 FITUR Athenix AI:
   • Menulis ulang konten secara profesional
   • Bahasa natural seperti tulisan blogger
   • Membersihkan metadata (author, tanggal, contact)
   • Hasil rapi dengan paragraf terstruktur

📌 CARA MENGGUNAKAN:
   1. Pastikan API Key DeepSeek sudah diisi
   2. Paste URL artikel yang ingin diparaphrase
   3. Klik tombol 'Paraphrase dengan Athenix AI'
   4. Hasil siap copy-paste ke blogmu!

⚡ Powered by LapaByt3"""
        
        self.result_text.insert("0.0", placeholder)
    
    def extract_main_content(self, soup):
        unwanted_tags = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'form', 'button']
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        unwanted_classes = ['author', 'date', 'published', 'post-meta', 'meta-info', 'comments', 'share', 'social', 'advertisement', 'sidebar', 'widget', 'newsletter', 'subscribe', 'contact']
        for class_name in unwanted_classes:
            for element in soup.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()
        
        content_selectors = ['article', 'main', '.post-content', '.article-content', '.entry-content', '.content', '#content', '.post-body']
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return ""
        
        text = main_content.get_text(separator=' ', strip=True)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        text = re.sub(r'\b(\+?\d{1,3}[-.]?)?\(?\d{2,4}\)?[-.]?\d{3,4}[-.]?\d{3,4}\b', '', text)
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'#\S+', '', text)
        text = re.sub(r'@\S+', '', text)
        text = re.sub(r'\d{1,2}\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4}', '', text, flags=re.I)
        text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', text)
        
        metadata_words = ['ditulis oleh', 'written by', 'author', 'published', 'posted on', 'share this', 'bagikan', 'komentar', 'comment', 'follow us', 'subscribe', 'berlangganan', 'contact us']
        for word in metadata_words:
            text = re.sub(rf'\b{word}\b.*?\.', '', text, flags=re.I)
        
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def clear_paraphrase_result(self):
        placeholder = """✨ Hasil paraphrase akan muncul di sini setelah diproses

📌 FITUR Athenix AI:
   • Menulis ulang konten secara profesional
   • Bahasa natural seperti tulisan blogger
   • Membersihkan metadata (author, tanggal, contact)
   • Hasil rapi dengan paragraf terstruktur

📌 CARA MENGGUNAKAN:
   1. Pastikan API Key DeepSeek sudah diisi
   2. Paste URL artikel yang ingin diparaphrase
   3. Klik tombol 'Paraphrase dengan Athenix AI'
   4. Hasil siap copy-paste ke blogmu!

⚡ Powered by LapaByt3"""
        
        self.result_text.delete("0.0", "end")
        self.result_text.insert("0.0", placeholder)
        self.status_label.configure(text="", text_color="gray")
        self.progress.set(0)
    
    def copy_paraphrase_result(self):
        text = self.result_text.get("0.0", "end").strip()
        if text and "Hasil paraphrase akan muncul di sini" not in text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_label.configure(text="✅ Hasil paraphrase disalin ke clipboard!", text_color="#4caf50")
            self.root.after(2000, lambda: self.status_label.configure(text="", text_color="gray"))
        else:
            self.status_label.configure(text="⚠️ Belum ada hasil paraphrase untuk disalin", text_color="#ffaa44")
    
    def paraphrase_article_deepseek(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Peringatan", "Masukkan URL artikel terlebih dahulu!")
            return
        
        if not self.api_key:
            messagebox.showwarning("Peringatan", "API Key DeepSeek belum diisi!\n\nSilakan isi API Key di menu Pengaturan API terlebih dahulu.")
            return
        
        def process():
            try:
                self.paraphrase_btn.configure(state="disabled", text="🔄 Memproses...")
                self.progress.set(0.2)
                self.status_label.configure(text="📡 Mengambil konten dari URL...", text_color="#3a6ea5")
                
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                self.progress.set(0.4)
                self.status_label.configure(text="🧹 Membersihkan metadata...", text_color="#3a6ea5")
                main_text = self.extract_main_content(soup)
                
                if not main_text or len(main_text) < 100:
                    main_text = "Konten tidak dapat diekstrak. Pastikan URL valid dan dapat diakses."
                
                self.progress.set(0.6)
                self.status_label.configure(text="🤖 Athenix AI sedang menulis ulang konten...", text_color="#3a6ea5")
                
                if len(main_text) > 5000:
                    main_text = main_text[:5000] + "..."
                
                prompt = f"""Tolong tulis ulang konten artikel di bawah ini dengan bahasa Indonesia yang natural, mudah dibaca, dan profesional seperti tulisan blogger. 
Buatlah menjadi beberapa paragraf yang rapi (3-5 kalimat per paragraf). 
Hapus semua informasi metadata seperti nama penulis, tanggal, email, nomor kontak, link sosial media, dan footer website.
Fokus hanya pada konten utama artikel.

KONTEN ARTIKEL:
{main_text}

Hasilkan tulisan yang rapi, informatif, dan siap pakai untuk blog."""
                
                result, error = self.call_deepseek_api(prompt)
                
                if error:
                    self.status_label.configure(text=f"❌ {error}", text_color="#f44336")
                    self.progress.set(0)
                    self.paraphrase_btn.configure(state="normal", text="🔄 Paraphrase dengan Athenix AI")
                    return
                
                self.progress.set(1.0)
                self.status_label.configure(text="✅ Paraphrase berhasil!", text_color="#4caf50")
                self.result_text.delete("0.0", "end")
                self.result_text.insert("0.0", result)
                self.result_text.insert("end", "\n\n" + "─"*50 + "\n")
                self.result_text.insert("end", "✨ Konten ditulis ulang oleh Athenix AI dengan bahasa natural!\n")
                self.result_text.insert("end", "⚡ Powered by LapaByt3\n")
                
                self.progress.set(0)
            except Exception as e:
                self.status_label.configure(text=f"❌ Error: {str(e)}", text_color="#f44336")
                self.progress.set(0)
            finally:
                self.paraphrase_btn.configure(state="normal", text="🔄 Paraphrase dengan Athenix AI")
        
        threading.Thread(target=process, daemon=True).start()
    
    # ==================== AUTO JUDUL MENARIK ====================
    def show_title_maker(self):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20,5), padx=30)
        
        icon_label = ctk.CTkLabel(header_frame, text="✨", font=ctk.CTkFont(size=36), text_color="#ffaa44")
        icon_label.pack(side="left")
        
        header = ctk.CTkLabel(header_frame, text="Auto Judul Menarik", 
                               font=ctk.CTkFont(size=28, weight="bold"),
                               text_color="#ffffff")
        header.pack(side="left", padx=(12,0))
        
        badge = ctk.CTkLabel(header_frame, text="Athenix AI", 
                              font=ctk.CTkFont(size=11, weight="bold"),
                              text_color="#ffaa44",
                              fg_color="#2d2d44",
                              corner_radius=12,
                              padx=10,
                              pady=3)
        badge.pack(side="left", padx=(12,0))
        
        desc = ctk.CTkLabel(self.content_frame, 
                            text="Athenix AI akan menghasilkan 35 judul UNIK per kategori.",
                            font=ctk.CTkFont(size=12),
                            text_color="#888888",
                            justify="left")
        desc.pack(anchor="w", padx=30, pady=(5,15))
        
        input_frame = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        input_frame.pack(fill="x", padx=30, pady=5)
        
        kategori_label = ctk.CTkLabel(input_frame, text="📚 Pilih Kategori Artikel", 
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       text_color="#ffffff")
        kategori_label.pack(anchor="w", pady=(15,8), padx=20)
        
        kategori_list = [
            "Fantasi", "Fiksi Ilmiah (Sci-Fi)", "Misteri / Detektif", "Romantis", 
            "Horor", "Thriller", "Fiksi Sejarah", "Distopia", "Fiksi Petualangan",
            "Fiksi Psikologis", "Urban Fantasy", "Filsafat", "Teori Politik",
            "Biografi", "Sejarah", "Psikologi", "Pengembangan Diri", "Bisnis & Ekonomi",
            "Sains & Teknologi", "Agama & Spiritualitas", "Pendidikan", "Kesehatan",
            "Seni & Fotografi", "Memasak & Kuliner", "Perjalanan (Travel)", "Hukum",
            "Esai & Kritik", "Jurnalisme", "Panduan (How-to)"
        ]
        
        self.kategori_combo = ctk.CTkComboBox(input_frame, values=kategori_list, width=400, height=45,
                                               font=ctk.CTkFont(size=13), corner_radius=12)
        self.kategori_combo.pack(anchor="w", padx=20, pady=(0,12))
        self.kategori_combo.set("Pilih Kategori Artikel")
        
        generate_btn = ctk.CTkButton(input_frame, text="✨ Generate 35 Judul dengan Athenix AI", 
                                      command=self.generate_titles_with_ai, height=45,
                                      font=ctk.CTkFont(size=13, weight="bold"), corner_radius=12,
                                      fg_color="#3a6ea5", hover_color="#2c5a8c")
        generate_btn.pack(pady=12, padx=20)
        
        self.title_progress = ctk.CTkProgressBar(input_frame, height=6, corner_radius=3)
        self.title_progress.pack(fill="x", padx=20, pady=(0,10))
        self.title_progress.set(0)
        
        self.title_status = ctk.CTkLabel(input_frame, text="", font=ctk.CTkFont(size=11))
        self.title_status.pack(pady=(0,12))
        
        # Result Card
        result_card = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        result_card.pack(fill="both", expand=True, padx=30, pady=(8,20))
        
        result_header = ctk.CTkFrame(result_card, fg_color="transparent")
        result_header.pack(fill="x", padx=20, pady=(12,8))
        
        result_label = ctk.CTkLabel(result_header, text="✨ Hasil Judul (35 Judul UNIK)", 
                                     font=ctk.CTkFont(size=15, weight="bold"), text_color="#ffffff")
        result_label.pack(side="left")
        
        self.counter_badge = ctk.CTkLabel(result_header, text="", font=ctk.CTkFont(size=11), text_color="#4caf50")
        self.counter_badge.pack(side="right")
        
        self.title_result = ctk.CTkTextbox(result_card, font=("Segoe UI", 12), fg_color="#1e1e2e",
                                            text_color="#e0e0e0", corner_radius=12, border_width=0, wrap="word")
        self.title_result.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        placeholder = """✨ Hasil judul akan muncul di sini setelah generate

📌 Athenix AI akan menghasilkan 35 judul UNIK untuk kategori yang dipilih.
📌 Setiap kali generate, hasilnya akan BERBEDA!

📌 CARA MENGGUNAKAN:
   1. Pilih kategori artikel
   2. Klik tombol 'Generate 35 Judul dengan Athenix AI'
   3. AI akan membuat 35 judul UNIK

⚡ Powered by LapaByt3"""
        
        self.title_result.insert("0.0", placeholder)
    
    def generate_titles_with_ai(self):
        kategori = self.kategori_combo.get()
        if kategori == "Pilih Kategori Artikel":
            messagebox.showwarning("Peringatan", "Pilih kategori artikel terlebih dahulu!")
            return
        
        if not self.api_key:
            messagebox.showwarning("Peringatan", "API Key DeepSeek belum diisi!\n\nSilakan isi API Key di menu Pengaturan API terlebih dahulu.")
            return
        
        def process():
            try:
                self.title_progress.set(0.2)
                self.title_status.configure(text=f"🤖 Athenix AI sedang merancang 35 judul...", text_color="#3a6ea5")
                
                existing_titles = self.title_history.get(kategori, [])
                
                prompt = f"""Buatkan 35 judul artikel SEO-friendly untuk kategori "{kategori}" dengan ketentuan:

1. Judul harus RELEVAN dengan kategori {kategori}
2. Gunakan angka (5, 7, 10, 15, 20, 25, 30, 50, 100) di beberapa judul
3. Variasikan format: listicle, tutorial, tips, review, perbandingan, panduan
4. Judul harus menarik dan SEO-friendly

Output hanya 35 judul, format per baris, langsung judulnya saja."""
                
                result, error = self.call_deepseek_api(prompt, "Kamu adalah ahli SEO dan copywriter profesional.")
                
                if error:
                    self.title_status.configure(text=f"❌ {error}", text_color="#f44336")
                    self.title_progress.set(0)
                    return
                
                titles = [line.strip() for line in result.split('\n') if line.strip() and not line.strip().startswith('#')]
                
                new_titles = []
                for title in titles:
                    if title not in existing_titles and title not in new_titles:
                        new_titles.append(title)
                        self.add_to_history(kategori, title)
                
                self.title_progress.set(1.0)
                self.title_status.configure(text=f"✅ Berhasil {len(new_titles[:35])} judul UNIK!", text_color="#4caf50")
                
                self.title_result.delete("0.0", "end")
                self.title_result.insert("0.0", f"📚 Kategori: {kategori}\n📅 {self.get_current_date()}\n")
                self.title_result.insert("end", "="*60 + "\n\n")
                
                for i, title in enumerate(new_titles[:35], 1):
                    self.title_result.insert("end", f"{i:2d}.  {title}\n\n")
                
                self.title_result.insert("end", "\n⚡ Powered by LapaByt3\n")
                self.counter_badge.configure(text=f"{len(new_titles[:35])} judul UNIK")
                self.title_progress.set(0)
            except Exception as e:
                self.title_status.configure(text=f"❌ Error: {str(e)}", text_color="#f44336")
                self.title_progress.set(0)
        
        threading.Thread(target=process, daemon=True).start()
    
    def get_current_date(self):
        return datetime.now().strftime("%d %B %Y")
    
    # ==================== YOUTUBE KE ARTIKEL ====================
    def show_youtube(self):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20,5), padx=30)
        
        icon_label = ctk.CTkLabel(header_frame, text="🎬", font=ctk.CTkFont(size=36), text_color="#f44336")
        icon_label.pack(side="left")
        
        header = ctk.CTkLabel(header_frame, text="YouTube ke Artikel", 
                               font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff")
        header.pack(side="left", padx=(12,0))
        
        badge = ctk.CTkLabel(header_frame, text="Athenix AI", 
                              font=ctk.CTkFont(size=11, weight="bold"),
                              text_color="#ffaa44",
                              fg_color="#2d2d44",
                              corner_radius=12,
                              padx=10,
                              pady=3)
        badge.pack(side="left", padx=(12,0))
        
        desc = ctk.CTkLabel(self.content_frame, 
                            text="Konversi video YouTube menjadi artikel mendalam (2000-3000 kata).",
                            font=ctk.CTkFont(size=12),
                            text_color="#888888",
                            justify="left")
        desc.pack(anchor="w", padx=30, pady=(5,15))
        
        input_card = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        input_card.pack(fill="x", padx=30, pady=5)
        
        url_label = ctk.CTkLabel(input_card, text="🔗 URL YouTube", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff")
        url_label.pack(anchor="w", padx=20, pady=(15,8))
        
        self.yt_url = ctk.CTkEntry(input_card, placeholder_text="https://youtube.com/watch?v=... atau https://youtu.be/...",
                                    height=50, font=ctk.CTkFont(size=13), corner_radius=12,
                                    fg_color="#1e1e2e", border_color="#3d3d5c", border_width=2)
        self.yt_url.pack(fill="x", padx=20, pady=(0,15))
        
        button_row = ctk.CTkFrame(input_card, fg_color="transparent")
        button_row.pack(fill="x", padx=20, pady=(0,15))
        
        self.yt_convert_btn = ctk.CTkButton(button_row, text="🎬 Konversi ke Artikel (Athenix AI)", 
                                             command=self.youtube_to_article_deepseek,
                                             height=45, font=ctk.CTkFont(size=13, weight="bold"), corner_radius=12,
                                             fg_color="#3a6ea5", hover_color="#2c5a8c")
        self.yt_convert_btn.pack(side="left", padx=(0,12))
        
        clear_btn = ctk.CTkButton(button_row, text="🗑️ Bersihkan", command=self.clear_youtube_result,
                                   height=45, font=ctk.CTkFont(size=13), corner_radius=12,
                                   fg_color="#3d3d5c", hover_color="#4d4d6c")
        clear_btn.pack(side="left")
        
        info_label = ctk.CTkLabel(button_row, text="💡 Artikel 2000-3000 kata | Powered by LapaByt3", 
                                   font=ctk.CTkFont(size=10), text_color="#666666")
        info_label.pack(side="right")
        
        progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=30, pady=8)
        
        self.yt_progress = ctk.CTkProgressBar(progress_frame, height=6, corner_radius=3)
        self.yt_progress.pack(fill="x", pady=(0,5))
        self.yt_progress.set(0)
        
        self.yt_status = ctk.CTkLabel(progress_frame, text="", font=ctk.CTkFont(size=11))
        self.yt_status.pack()
        
        # Result Card
        result_card = ctk.CTkFrame(self.content_frame, fg_color="#2d2d44", corner_radius=20)
        result_card.pack(fill="both", expand=True, padx=30, pady=(8,20))
        
        result_header = ctk.CTkFrame(result_card, fg_color="transparent")
        result_header.pack(fill="x", padx=20, pady=(12,8))
        
        result_title = ctk.CTkLabel(result_header, text="📄 Hasil Artikel (2000-3000 kata)", 
                                     font=ctk.CTkFont(size=15, weight="bold"), text_color="#ffffff")
        result_title.pack(side="left")
        
        copy_btn = ctk.CTkButton(result_header, text="📋 Copy", command=self.copy_youtube_result,
                                  width=70, height=30, font=ctk.CTkFont(size=11, weight="bold"), corner_radius=8,
                                  fg_color="#3d3d5c", hover_color="#4d4d6c")
        copy_btn.pack(side="right")
        
        self.yt_result = ctk.CTkTextbox(result_card, font=("Segoe UI", 12), fg_color="#1e1e2e",
                                         text_color="#e0e0e0", corner_radius=12, border_width=0, wrap="word")
        self.yt_result.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        placeholder = """✨ Hasil artikel akan muncul di sini setelah konversi

📌 CARA MENGGUNAKAN:
   1. Pastikan API Key DeepSeek sudah diisi
   2. Paste URL YouTube
   3. Klik tombol 'Konversi ke Artikel (Athenix AI)'
   4. Tunggu AI membuat artikel mendalam (2000-3000 kata)
   5. Artikel siap copy-paste ke blogmu!

⚡ Powered by LapaByt3"""
        
        self.yt_result.insert("0.0", placeholder)
    
    def extract_youtube_id(self, url):
        patterns = [r'youtube\.com/watch\?v=([^&]+)', r'youtu\.be/([^?]+)', r'youtube\.com/embed/([^?]+)']
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_youtube_title(self, url):
        video_id = self.extract_youtube_id(url)
        if not video_id:
            return None, "URL tidak valid"
        try:
            resp = requests.get(f"https://www.youtube.com/oembed?url=https://youtu.be/{video_id}&format=json", timeout=10)
            if resp.status_code == 200:
                return resp.json().get('title'), None
        except:
            pass
        return f"Video YouTube - {video_id}", None
    
    def youtube_to_article_deepseek(self):
        url = self.yt_url.get().strip()
        if not url:
            messagebox.showwarning("Peringatan", "Masukkan URL YouTube terlebih dahulu!")
            return
        
        if not self.api_key:
            messagebox.showwarning("Peringatan", "API Key DeepSeek belum diisi!\n\nSilakan isi API Key di menu Pengaturan API terlebih dahulu.")
            return
        
        def process():
            try:
                self.yt_convert_btn.configure(state="disabled", text="🎬 Memproses...")
                self.yt_progress.set(0.2)
                self.yt_status.configure(text="📡 Mengambil judul video...", text_color="#3a6ea5")
                
                title, error = self.get_youtube_title(url)
                
                if error or not title:
                    video_id = self.extract_youtube_id(url)
                    title = f"Video YouTube - {video_id}" if video_id else "Video YouTube"
                
                self.yt_progress.set(0.4)
                self.yt_status.configure(text="🤖 Athenix AI sedang menulis artikel mendalam...", text_color="#3a6ea5")
                
                prompt = f"""Buat artikel mendalam (2000+ kata) berdasarkan judul video: "{title}"

Struktur:
1. Judul utama
2. Pendahuluan
3. Sub-bab analisis
4. Studi kasus
5. Dampak
6. Solusi
7. Kesimpulan

Gaya: jurnalis investigasi, bahasa Indonesia formal."""
                
                result, error = self.call_deepseek_api(prompt)
                
                if error:
                    self.yt_status.configure(text=f"❌ {error}", text_color="#f44336")
                    self.yt_progress.set(0)
                    self.yt_convert_btn.configure(state="normal", text="🎬 Konversi ke Artikel (Athenix AI)")
                    return
                
                self.yt_progress.set(1.0)
                self.yt_status.configure(text="✅ Artikel mendalam berhasil dibuat!", text_color="#4caf50")
                self.yt_result.delete("0.0", "end")
                self.yt_result.insert("0.0", result)
                self.yt_result.insert("end", "\n\n" + "─"*50 + "\n")
                self.yt_result.insert("end", "✨ Artikel ditulis oleh Athenix AI berdasarkan judul video.\n")
                self.yt_result.insert("end", "⚡ Powered by LapaByt3\n")
                
                self.yt_progress.set(0)
            except Exception as e:
                self.yt_status.configure(text=f"❌ Error: {str(e)}", text_color="#f44336")
                self.yt_progress.set(0)
            finally:
                self.yt_convert_btn.configure(state="normal", text="🎬 Konversi ke Artikel (Athenix AI)")
        
        threading.Thread(target=process, daemon=True).start()
    
    def clear_youtube_result(self):
        placeholder = """✨ Hasil artikel akan muncul di sini setelah konversi

📌 CARA MENGGUNAKAN:
   1. Pastikan API Key DeepSeek sudah diisi
   2. Paste URL YouTube
   3. Klik tombol 'Konversi ke Artikel (Athenix AI)'
   4. Tunggu AI membuat artikel mendalam (2000-3000 kata)
   5. Artikel siap copy-paste ke blogmu!

⚡ Powered by LapaByt3"""
        
        self.yt_result.delete("0.0", "end")
        self.yt_result.insert("0.0", placeholder)
        self.yt_status.configure(text="", text_color="gray")
        self.yt_progress.set(0)
    
    def copy_youtube_result(self):
        text = self.yt_result.get("0.0", "end").strip()
        if text and "Hasil artikel akan muncul di sini" not in text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.yt_status.configure(text="✅ Artikel disalin ke clipboard!", text_color="#4caf50")
            self.root.after(2000, lambda: self.yt_status.configure(text="", text_color="gray"))
        else:
            self.yt_status.configure(text="⚠️ Belum ada artikel untuk disalin", text_color="#ffaa44")
    
    # ==================== CEK RANK ARTIKEL ====================
    def show_rank_checker(self):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20,5), padx=30)
        
        icon_label = ctk.CTkLabel(header_frame, text="🔍", font=ctk.CTkFont(size=36), text_color="#00bcd4")
        icon_label.pack(side="left")
        
        header = ctk.CTkLabel(header_frame, text="Cek Rank Artikel", 
                               font=ctk.CTkFont(size=28, weight="bold"),
                               text_color="#ffffff")
        header.pack(side="left", padx=(12,0))
        
        badge = ctk.CTkLabel(header_frame, text="Athenix AI + Grafik", 
                              font=ctk.CTkFont(size=11, weight="bold"),
                              text_color="#ffaa44",
                              fg_color="#2d2d44",
                              corner_radius=12,
                              padx=10,
                              pady=3)
        badge.pack(side="left", padx=(12,0))
        
        desc = ctk.CTkLabel(self.content_frame, 
                            text="Athenix AI akan menganalisis artikel dan menampilkan grafik trafik real-time.",
                            font=ctk.CTkFont(size=12),
                            text_color="#888888",
                            justify="left")
        desc.pack(anchor="w", padx=30, pady=(5,15))
        
        tabview = ctk.CTkTabview(self.content_frame, width=1200, height=650, corner_radius=15)
        tabview.pack(fill="both", expand=True, padx=30, pady=10)
        
        tabview.add("🔍 Single Link Scan")
        tabview.add("🔄 Compare Link")
        
        # ==================== SINGLE LINK SCAN ====================
        single_tab = tabview.tab("🔍 Single Link Scan")
        
        url_frame = ctk.CTkFrame(single_tab, fg_color="transparent")
        url_frame.pack(fill="x", padx=20, pady=15)
        
        url_label = ctk.CTkLabel(url_frame, text="URL Artikel:", font=ctk.CTkFont(size=13, weight="bold"))
        url_label.pack(side="left", padx=(0,8))
        
        self.rank_url_entry = ctk.CTkEntry(url_frame, placeholder_text="https://example.com/artikel", 
                                            height=42, width=500, font=ctk.CTkFont(size=13), corner_radius=12)
        self.rank_url_entry.pack(side="left", fill="x", expand=True)
        
        self.scan_btn = ctk.CTkButton(url_frame, text="🔍 Scan dengan Athenix AI", 
                                       command=self.scan_single_article_ai,
                                       height=42, font=ctk.CTkFont(size=13, weight="bold"), corner_radius=12,
                                       fg_color="#3a6ea5", hover_color="#2c5a8c")
        self.scan_btn.pack(side="right", padx=(8,0))
        
        progress_frame = ctk.CTkFrame(single_tab, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=8)
        
        self.rank_progress = ctk.CTkProgressBar(progress_frame, height=6, corner_radius=3)
        self.rank_progress.pack(fill="x")
        self.rank_progress.set(0)
        
        self.rank_status = ctk.CTkLabel(progress_frame, text="", font=ctk.CTkFont(size=11))
        self.rank_status.pack(pady=(5,0))
        
        # Grafik Container
        chart_container = ctk.CTkFrame(single_tab, fg_color="#2d2d44", corner_radius=15)
        chart_container.pack(fill="both", expand=True, padx=20, pady=8)
        
        chart_header = ctk.CTkFrame(chart_container, fg_color="transparent")
        chart_header.pack(fill="x", padx=12, pady=(8,5))
        
        chart_title = ctk.CTkLabel(chart_header, text="📊 Trafik Pengunjung (7 Hari Terakhir)", 
                                    font=ctk.CTkFont(size=13, weight="bold"))
        chart_title.pack(side="left")
        
        self.fig, self.ax = plt.subplots(figsize=(7, 2.5))
        self.ax.text(0.5, 0.5, '🔍 Masukkan URL untuk melihat grafik', ha='center', va='center', fontsize=10)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0,8))
        
        # Hasil Analisis AI
        analysis_container = ctk.CTkFrame(single_tab, fg_color="#2d2d44", corner_radius=15)
        analysis_container.pack(fill="both", expand=True, padx=20, pady=8)
        
        analysis_header = ctk.CTkFrame(analysis_container, fg_color="transparent")
        analysis_header.pack(fill="x", padx=12, pady=(8,5))
        
        analysis_title = ctk.CTkLabel(analysis_header, text="🤖 Analisis Athenix AI", 
                                       font=ctk.CTkFont(size=13, weight="bold"))
        analysis_title.pack(side="left")
        
        copy_btn = ctk.CTkButton(analysis_header, text="📋 Copy", command=self.copy_rank_result,
                                  width=70, height=28, font=ctk.CTkFont(size=11, weight="bold"), corner_radius=8,
                                  fg_color="#3d3d5c", hover_color="#4d4d6c")
        copy_btn.pack(side="right")
        
        self.rank_result = ctk.CTkTextbox(analysis_container, font=("Segoe UI", 11), height=140,
                                           fg_color="#1e1e2e", text_color="#e0e0e0",
                                           corner_radius=12, border_width=0, wrap="word")
        self.rank_result.pack(fill="both", expand=True, padx=12, pady=(0,12))
        
        placeholder = """✨ Hasil analisis akan muncul di sini setelah scan.

Athenix AI akan menganalisis:
   • Kualitas konten dan struktur artikel
   • SEO score dan keyword optimization
   • Rekomendasi perbaikan
   • Potensi ranking di Google

⚡ Powered by LapaByt3"""
        
        self.rank_result.insert("0.0", placeholder)
        
        # ==================== COMPARE LINK TAB ====================
        compare_tab = tabview.tab("🔄 Compare Link")
        compare_scroll = ctk.CTkScrollableFrame(compare_tab, fg_color="transparent")
        compare_scroll.pack(fill="both", expand=True, padx=8, pady=8)
        
        input_container = ctk.CTkFrame(compare_scroll, fg_color="transparent")
        input_container.pack(fill="x", pady=8, padx=8)
        
        left_input = ctk.CTkFrame(input_container, fg_color="#2d2d44", corner_radius=12)
        left_input.pack(side="left", fill="both", expand=True, padx=(0,8))
        
        url1_label = ctk.CTkLabel(left_input, text="📄 Artikel 1", font=ctk.CTkFont(size=14, weight="bold"))
        url1_label.pack(anchor="w", pady=(12,5), padx=12)
        
        self.compare_url1 = ctk.CTkEntry(left_input, placeholder_text="https://example.com/artikel-1", height=45,
                                          font=ctk.CTkFont(size=12), corner_radius=10)
        self.compare_url1.pack(fill="x", padx=12, pady=(0,12))
        
        right_input = ctk.CTkFrame(input_container, fg_color="#2d2d44", corner_radius=12)
        right_input.pack(side="left", fill="both", expand=True, padx=(8,0))
        
        url2_label = ctk.CTkLabel(right_input, text="📄 Artikel 2", font=ctk.CTkFont(size=14, weight="bold"))
        url2_label.pack(anchor="w", pady=(12,5), padx=12)
        
        self.compare_url2 = ctk.CTkEntry(right_input, placeholder_text="https://example.com/artikel-2", height=45,
                                          font=ctk.CTkFont(size=12), corner_radius=10)
        self.compare_url2.pack(fill="x", padx=12, pady=(0,12))
        
        self.compare_btn = ctk.CTkButton(compare_scroll, text="🔄 Bandingkan dengan Athenix AI", command=self.compare_articles_ai,
                                          height=45, font=ctk.CTkFont(size=13, weight="bold"), corner_radius=12,
                                          fg_color="#3a6ea5", hover_color="#2c5a8c")
        self.compare_btn.pack(pady=12, padx=15)
        
        self.compare_progress = ctk.CTkProgressBar(compare_scroll, height=6, corner_radius=3)
        self.compare_progress.pack(fill="x", padx=15, pady=8)
        self.compare_progress.set(0)
        
        self.compare_status = ctk.CTkLabel(compare_scroll, text="", font=ctk.CTkFont(size=11))
        self.compare_status.pack()
        
        result_container = ctk.CTkFrame(compare_scroll, fg_color="transparent")
        result_container.pack(fill="both", expand=True, pady=(12,15), padx=8)
        
        left_result = ctk.CTkFrame(result_container, fg_color="#2d2d44", corner_radius=12)
        left_result.pack(side="left", fill="both", expand=True, padx=(0,6))
        
        left_header = ctk.CTkFrame(left_result, fg_color="transparent")
        left_header.pack(fill="x", padx=12, pady=(10,5))
        
        left_title = ctk.CTkLabel(left_header, text="📊 Artikel 1", font=ctk.CTkFont(size=13, weight="bold"))
        left_title.pack(side="left")
        
        left_score_badge = ctk.CTkLabel(left_header, text="", font=ctk.CTkFont(size=11), fg_color="#3a6ea5", corner_radius=8, padx=6, pady=2)
        left_score_badge.pack(side="right")
        
        self.left_result_text = ctk.CTkTextbox(left_result, font=("Segoe UI", 11), fg_color="#1e1e2e",
                                                text_color="#e0e0e0", corner_radius=10, border_width=0, wrap="word", height=350)
        self.left_result_text.pack(fill="both", expand=True, padx=12, pady=(0,12))
        
        right_result = ctk.CTkFrame(result_container, fg_color="#2d2d44", corner_radius=12)
        right_result.pack(side="left", fill="both", expand=True, padx=(6,0))
        
        right_header = ctk.CTkFrame(right_result, fg_color="transparent")
        right_header.pack(fill="x", padx=12, pady=(10,5))
        
        right_title = ctk.CTkLabel(right_header, text="📊 Artikel 2", font=ctk.CTkFont(size=13, weight="bold"))
        right_title.pack(side="left")
        
        right_score_badge = ctk.CTkLabel(right_header, text="", font=ctk.CTkFont(size=11), fg_color="#3a6ea5", corner_radius=8, padx=6, pady=2)
        right_score_badge.pack(side="right")
        
        self.right_result_text = ctk.CTkTextbox(right_result, font=("Segoe UI", 11), fg_color="#1e1e2e",
                                                 text_color="#e0e0e0", corner_radius=10, border_width=0, wrap="word", height=350)
        self.right_result_text.pack(fill="both", expand=True, padx=12, pady=(0,12))
        
        conclusion_card = ctk.CTkFrame(compare_scroll, fg_color="#2d2d44", corner_radius=12)
        conclusion_card.pack(fill="x", padx=8, pady=(8,12))
        
        conclusion_header = ctk.CTkFrame(conclusion_card, fg_color="transparent")
        conclusion_header.pack(fill="x", padx=15, pady=(12,5))
        
        conclusion_title = ctk.CTkLabel(conclusion_header, text="🏆 Kesimpulan", font=ctk.CTkFont(size=14, weight="bold"))
        conclusion_title.pack(side="left")
        
        self.conclusion_text = ctk.CTkTextbox(conclusion_card, font=("Segoe UI", 12), fg_color="#1e1e2e",
                                               text_color="#e0e0e0", corner_radius=10, border_width=0, wrap="word", height=100)
        self.conclusion_text.pack(fill="x", padx=15, pady=(0,15))
        
        compare_placeholder_left = """✨ Hasil analisis Artikel 1 akan muncul di sini"""
        compare_placeholder_right = """✨ Hasil analisis Artikel 2 akan muncul di sini"""
        
        self.left_result_text.insert("0.0", compare_placeholder_left)
        self.right_result_text.insert("0.0", compare_placeholder_right)
        self.conclusion_text.insert("0.0", "✨ Hasil perbandingan akan muncul di sini.\n\n⚡ Powered by LapaByt3")
        
        self.left_score_badge = left_score_badge
        self.right_score_badge = right_score_badge
    
    def update_metrics(self, data):
        pass
    
    def create_visitor_chart(self, data):
        self.ax.clear()
        
        dates = data.get('dates', [(datetime.now() - timedelta(days=i)).strftime('%d/%m') for i in range(6, -1, -1)])
        visitors = data.get('visitors', [random.randint(50, 500) for _ in range(7)])
        
        colors = ['#3a6ea5' if v < max(visitors) else '#ffaa44' for v in visitors]
        bars = self.ax.bar(dates, visitors, color=colors, alpha=0.8, edgecolor='none')
        
        for bar, val in zip(bars, visitors):
            self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                        str(val), ha='center', va='bottom', fontsize=8, color='#e0e0e0')
        
        self.ax.set_xlabel('Tanggal', fontsize=9)
        self.ax.set_ylabel('Pengunjung', fontsize=9)
        self.ax.set_title('Trafik Pengunjung 7 Hari Terakhir', fontsize=10, pad=10)
        self.ax.grid(axis='y', alpha=0.3)
        self.ax.set_facecolor('#1e1e2e')
        
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
        self.fig.tight_layout()
        self.canvas.draw()
    
    def analyze_article_with_ai(self, url, article_name=""):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "Tidak ditemukan"
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            word_count = len(text.split())
            
            if len(text) > 4000:
                text = text[:4000] + "..."
            
            prompt = f"""Analisis artikel berikut dan berikan data performa:

JUDUL: {title}
PANJANG: {word_count} kata

KONTEN:
{text}

Berikan output dalam format JSON:
{{
    "seo_score": (nilai 1-100),
    "readability_score": (nilai 1-100),
    "estimated_visitors": (estimasi pengunjung per hari, angka),
    "estimated_clicks": (estimasi total klik, angka),
    "avg_read_time": (estimasi waktu baca dalam menit, angka),
    "bounce_rate": (estimasi bounce rate dalam persen, angka),
    "backlinks": (estimasi jumlah backlink, angka),
    "daily_visitors": [estimasi pengunjung per hari selama 7 hari, array 7 angka],
    "dates": ["tanggal1", "tanggal2", ...],
    "strengths": ["kelebihan 1", "kelebihan 2"],
    "weaknesses": ["kekurangan 1", "kekurangan 2"],
    "recommendations": ["rekomendasi 1", "rekomendasi 2"],
    "overall_verdict": "kesimpulan singkat"
}}

Buat estimasi realistis berdasarkan kualitas artikel."""
            
            result, error = self.call_deepseek_api(prompt, "Kamu adalah ahli SEO dan analis data.")
            
            if error:
                return None, error
            
            import json
            try:
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    data = self.generate_fallback_data(word_count)
            except:
                data = self.generate_fallback_data(word_count)
            
            return {
                'title': title,
                'word_count': word_count,
                'data': data,
                'analysis': result
            }, None
            
        except Exception as e:
            return None, str(e)
    
    def generate_fallback_data(self, word_count):
        score = min(100, max(20, word_count // 10))
        return {
            "seo_score": score,
            "readability_score": score - 10,
            "estimated_visitors": random.randint(100, 1000),
            "estimated_clicks": random.randint(500, 5000),
            "avg_read_time": random.randint(2, 8),
            "bounce_rate": random.randint(40, 80),
            "backlinks": random.randint(10, 200),
            "daily_visitors": [random.randint(50, 500) for _ in range(7)],
            "dates": [(datetime.now() - timedelta(days=i)).strftime('%d/%m') for i in range(6, -1, -1)],
            "strengths": ["Konten informatif", "Struktur cukup rapi"],
            "weaknesses": ["Belum ada gambar pendukung"],
            "recommendations": ["Tambahkan gambar", "Perbanyak sub-bab"],
            "overall_verdict": "Artikel berkualitas cukup baik."
        }
    
    def scan_single_article_ai(self):
        url = self.rank_url_entry.get().strip()
        if not url:
            messagebox.showwarning("Peringatan", "Masukkan URL artikel terlebih dahulu!")
            return
        
        if not self.api_key:
            messagebox.showwarning("Peringatan", "API Key DeepSeek belum diisi!")
            return
        
        def process():
            try:
                self.scan_btn.configure(state="disabled", text="🔍 Scanning...")
                self.rank_progress.set(0.3)
                self.rank_status.configure(text="📡 Mengambil konten artikel...", text_color="#3a6ea5")
                
                result, error = self.analyze_article_with_ai(url)
                
                if error:
                    self.rank_status.configure(text=f"❌ {error}", text_color="#f44336")
                    self.rank_progress.set(0)
                    self.scan_btn.configure(state="normal", text="🔍 Scan dengan Athenix AI")
                    return
                
                self.rank_progress.set(0.6)
                self.rank_status.configure(text="📊 Memproses data dan grafik...", text_color="#3a6ea5")
                
                data = result['data']
                
                chart_data = {
                    'dates': data.get('dates', []),
                    'visitors': data.get('daily_visitors', [])
                }
                self.create_visitor_chart(chart_data)
                
                self.rank_progress.set(0.8)
                self.rank_status.configure(text="🤖 Athenix AI menyusun analisis...", text_color="#3a6ea5")
                
                analysis_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 HASIL ANALISIS ARTIKEL                 ║
║                      Athenix AI - LapaByt3                   ║
╚══════════════════════════════════════════════════════════════╝

📌 JUDUL: {result['title']}

📈 STATISTIK:
   • Jumlah Kata: {result['word_count']} kata
   • SEO Score: {data.get('seo_score', 0)}/100
   • Readability: {data.get('readability_score', 0)}/100
   • Estimasi Pengunjung/Hari: {data.get('estimated_visitors', 0):,}
   • Estimasi Klik: {data.get('estimated_clicks', 0):,}
   • Waktu Baca: {data.get('avg_read_time', 0)} menit
   • Bounce Rate: {data.get('bounce_rate', 0)}%
   • Backlink: {data.get('backlinks', 0)}

✅ KELEBIHAN:
"""
                for s in data.get('strengths', []):
                    analysis_text += f"   • {s}\n"
                
                analysis_text += f"""
⚠️ KEKURANGAN:
"""
                for w in data.get('weaknesses', []):
                    analysis_text += f"   • {w}\n"
                
                analysis_text += f"""
💡 REKOMENDASI:
"""
                for r in data.get('recommendations', []):
                    analysis_text += f"   • {r}\n"
                
                analysis_text += f"""
📝 KESIMPULAN:
   {data.get('overall_verdict', 'Artikel berkualitas baik.')}

─────────────────────────────────────────────────────────────────
⚡ Athenix AI Scoring | Beta v0.1.0 | Powered by LapaByt3
📊 Grafik menunjukkan estimasi trafik 7 hari terakhir
"""
                
                self.rank_result.delete("0.0", "end")
                self.rank_result.insert("0.0", analysis_text)
                
                self.rank_progress.set(1.0)
                self.rank_status.configure(text="✅ Analisis selesai!", text_color="#4caf50")
                self.rank_progress.set(0)
            except Exception as e:
                self.rank_status.configure(text=f"❌ Error: {str(e)}", text_color="#f44336")
                self.rank_progress.set(0)
            finally:
                self.scan_btn.configure(state="normal", text="🔍 Scan dengan Athenix AI")
        
        threading.Thread(target=process, daemon=True).start()
    
    def copy_rank_result(self):
        text = self.rank_result.get("0.0", "end").strip()
        if text and "Hasil analisis akan muncul" not in text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.rank_status.configure(text="✅ Analisis disalin ke clipboard!", text_color="#4caf50")
            self.root.after(2000, lambda: self.rank_status.configure(text="", text_color="gray"))
        else:
            self.rank_status.configure(text="⚠️ Belum ada hasil analisis untuk disalin", text_color="#ffaa44")
    
    def compare_articles_ai(self):
        url1 = self.compare_url1.get().strip()
        url2 = self.compare_url2.get().strip()
        
        if not url1 or not url2:
            messagebox.showwarning("Peringatan", "Masukkan kedua URL artikel!")
            return
        
        if not self.api_key:
            messagebox.showwarning("Peringatan", "API Key DeepSeek belum diisi!")
            return
        
        def process():
            try:
                self.compare_btn.configure(state="disabled", text="🔄 Membandingkan...")
                self.compare_progress.set(0.2)
                self.compare_status.configure(text="📡 Menganalisis Artikel 1...", text_color="#3a6ea5")
                
                result1, error1 = self.analyze_article_with_ai(url1, "Artikel 1")
                
                if error1:
                    self.compare_status.configure(text=f"❌ Error Artikel 1: {error1}", text_color="#f44336")
                    self.compare_progress.set(0)
                    self.compare_btn.configure(state="normal", text="🔄 Bandingkan dengan Athenix AI")
                    return
                
                self.compare_progress.set(0.5)
                self.compare_status.configure(text="📡 Menganalisis Artikel 2...", text_color="#3a6ea5")
                
                result2, error2 = self.analyze_article_with_ai(url2, "Artikel 2")
                
                if error2:
                    self.compare_status.configure(text=f"❌ Error Artikel 2: {error2}", text_color="#f44336")
                    self.compare_progress.set(0)
                    self.compare_btn.configure(state="normal", text="🔄 Bandingkan dengan Athenix AI")
                    return
                
                self.compare_progress.set(0.8)
                self.compare_status.configure(text="🤖 Athenix AI membandingkan...", text_color="#3a6ea5")
                
                data1 = result1['data']
                data2 = result2['data']
                
                score1 = data1.get('seo_score', 0) // 20
                score2 = data2.get('seo_score', 0) // 20
                
                stars1 = "⭐" * score1
                empty_stars1 = "☆" * (5 - score1)
                stars2 = "⭐" * score2
                empty_stars2 = "☆" * (5 - score2)
                
                output1 = f"""
📌 JUDUL: {result1['title'][:80]}{'...' if len(result1['title']) > 80 else ''}

📊 SKOR: {score1}/5.0
   {stars1}{empty_stars1}

📈 SEO Score: {data1.get('seo_score', 0)}/100
📊 Bounce Rate: {data1.get('bounce_rate', 0)}%
👥 Estimasi Pengunjung: {data1.get('estimated_visitors', 0):,}/hari
📖 Jumlah Kata: {result1['word_count']} kata

✅ KELEBIHAN:
"""
                for s in data1.get('strengths', [])[:3]:
                    output1 += f"   • {s}\n"
                
                output2 = f"""
📌 JUDUL: {result2['title'][:80]}{'...' if len(result2['title']) > 80 else ''}

📊 SKOR: {score2}/5.0
   {stars2}{empty_stars2}

📈 SEO Score: {data2.get('seo_score', 0)}/100
📊 Bounce Rate: {data2.get('bounce_rate', 0)}%
👥 Estimasi Pengunjung: {data2.get('estimated_visitors', 0):,}/hari
📖 Jumlah Kata: {result2['word_count']} kata

✅ KELEBIHAN:
"""
                for s in data2.get('strengths', [])[:3]:
                    output2 += f"   • {s}\n"
                
                self.left_score_badge.configure(text=f"⭐ {score1}/5")
                self.right_score_badge.configure(text=f"⭐ {score2}/5")
                
                self.left_result_text.delete("0.0", "end")
                self.left_result_text.insert("0.0", output1)
                self.right_result_text.delete("0.0", "end")
                self.right_result_text.insert("0.0", output2)
                
                if score1 > score2:
                    conclusion = f"""
🏆 PEMENANG: ARTIKEL 1 (Skor {score1} vs {score2})
📊 Selisih: +{score1 - score2} poin

📌 REKOMENDASI: Gunakan Artikel 1 sebagai referensi utama.

⚡ Powered by LapaByt3
"""
                elif score2 > score1:
                    conclusion = f"""
🏆 PEMENANG: ARTIKEL 2 (Skor {score2} vs {score1})
📊 Selisih: +{score2 - score1} poin

📌 REKOMENDASI: Gunakan Artikel 2 sebagai referensi utama.

⚡ Powered by LapaByt3
"""
                else:
                    conclusion = f"""
🤝 HASIL IMBANG (Kedua artikel memiliki skor {score1})

📌 REKOMENDASI: Kedua artikel memiliki kualitas yang seimbang.

⚡ Powered by LapaByt3
"""
                
                self.conclusion_text.delete("0.0", "end")
                self.conclusion_text.insert("0.0", conclusion)
                
                self.compare_progress.set(1.0)
                self.compare_status.configure(text="✅ Perbandingan selesai!", text_color="#4caf50")
                self.compare_progress.set(0)
            except Exception as e:
                self.compare_status.configure(text=f"❌ Error: {str(e)}", text_color="#f44336")
                self.compare_progress.set(0)
            finally:
                self.compare_btn.configure(state="normal", text="🔄 Bandingkan dengan Athenix AI")
        
        threading.Thread(target=process, daemon=True).start()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

# ==================== MAIN APP ====================
if __name__ == "__main__":
    root = ctk.CTk()
    app = Athenix(root)
    root.mainloop()