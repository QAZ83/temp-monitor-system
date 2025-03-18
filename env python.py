#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI-Powered Temperature Monitoring System
=======================================
Version: 2.0
Last Updated: 2025-03-16
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
import os
import json
import matplotlib
matplotlib.rcParams['font.family'] = 'Arial'  # لتحسين عرض النصوص العربية إن وجدت

class TempMonitorSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Powered Temperature Monitoring System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # تكوين الخصائص المتقدمة
        self.app_config = {
            "data_dir": "./temp_data",
            "model_file": "temp_model.pkl",
            "history_file": "temp_history.csv",
            "config_file": "app_config.json",
            "auto_predict": True,
            "prediction_days": 7,
            "polynomial_degree": 2,
            "theme": "light"
        }
        
        # تهيئة البيانات
        self.temp_data = {'Date': [], 'Time': [], 'Temperature': [], 'Rating': [], 'Notes': []}
        self.df = pd.DataFrame(self.temp_data)
        
        # تهيئة نماذج التنبؤ المتعددة
        self.models = {
            "linear": LinearRegression(),
            "poly2": LinearRegression(),
            "poly3": LinearRegression()
        }
        
        self.poly_features = {
            "poly2": PolynomialFeatures(degree=2),
            "poly3": PolynomialFeatures(degree=3)
        }
        
        self.active_model = "poly2"  # النموذج الافتراضي
        
        # إنشاء مسار لحفظ البيانات إذا لم يكن موجوداً
        if not os.path.exists(self.app_config["data_dir"]):
            os.makedirs(self.app_config["data_dir"])
        
        # تحميل الإعدادات المحفوظة
        self.load_config()
            
        # التحقق من وجود نماذج مدربة سابقاً
        self.load_data_and_models()
        
        # إنشاء الواجهة الرئيسية
        self.create_widgets()
        
        # تحديث الإحصائيات والرسومات
        self.update_display()
        
    def load_config(self):
        """تحميل إعدادات التطبيق من ملف التكوين"""
        config_path = os.path.join(self.app_config["data_dir"], self.app_config["config_file"])
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as file:
                    loaded_config = json.load(file)
                    # دمج الإعدادات المحملة مع الإعدادات الافتراضية
                    self.app_config.update(loaded_config)
                print("Application settings loaded successfully")
            except Exception as e:
                print(f"Error loading application settings: {e}")
    
    def save_config(self):
        """حفظ إعدادات التطبيق إلى ملف التكوين"""
        config_path = os.path.join(self.app_config["data_dir"], self.app_config["config_file"])
        try:
            with open(config_path, 'w') as file:
                json.dump(self.app_config, file, indent=4)
            print("Application settings saved successfully")
        except Exception as e:
            print(f"Error saving application settings: {e}")
    
    def load_data_and_models(self):
        """تحميل البيانات والنماذج المدربة"""
        history_path = os.path.join(self.app_config["data_dir"], self.app_config["history_file"])
        
        # تحميل بيانات القراءات
        if os.path.exists(history_path):
            try:
                self.df = pd.read_csv(history_path)
                print(f"Loaded {len(self.df)} readings from previous data")
            except Exception as e:
                print(f"Error loading data: {e}")
        
        # تحميل نماذج التنبؤ
        for model_name in self.models.keys():
            model_path = os.path.join(self.app_config["data_dir"], f"{model_name}_model.pkl")
            if os.path.exists(model_path):
                try:
                    self.models[model_name] = joblib.load(model_path)
                    print(f"Model {model_name} loaded successfully")
                except Exception as e:
                    print(f"Error loading model {model_name}: {e}")
    
    def create_widgets(self):
        """إنشاء عناصر واجهة المستخدم"""
        # إنشاء شريط القوائم
        self.create_menu()
        
        # إطار العنوان
        title_frame = tk.Frame(self.root, bg="#3498db", height=50)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame, 
            text="AI-Powered Temperature Monitoring System", 
            font=("Arial", 18, "bold"),
            bg="#3498db",
            fg="white"
        )
        title_label.pack(pady=10)
        
        # إطار الإدخال والعرض
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # تقسيم الواجهة إلى نصفين
        left_frame = tk.Frame(main_frame, bg="#f0f0f0")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # تكوين الشبكة
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # ----- القسم الأيسر -----
        # إطار إدخال البيانات
        self.create_input_frame(left_frame)
        
        # إطار الإحصائيات
        self.create_stats_frame(left_frame)
        
        # ----- القسم الأيمن -----
        # إطار الرسم البياني
        self.create_graph_frame(right_frame)
        
        # إطار التنبؤات المتقدمة
        self.create_predictions_frame(right_frame)
        
        # ----- أسفل الواجهة -----
        # إطار القائمة
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.create_data_table(bottom_frame)
        
        # شريط الحالة
        status_bar = tk.Frame(self.root, height=20, bg="#f0f0f0", relief=tk.SUNKEN, bd=1)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(status_bar, textvariable=self.status_var, anchor="e", bg="#f0f0f0")
        status_label.pack(side=tk.RIGHT, padx=10)
        
        self.records_var = tk.StringVar(value="No readings")
        records_label = tk.Label(status_bar, textvariable=self.records_var, anchor="w", bg="#f0f0f0")
        records_label.pack(side=tk.LEFT, padx=10)
    
    def create_menu(self):
        """إنشاء شريط القوائم"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # قائمة الملف
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data to CSV", command=self.export_data)
        file_menu.add_command(label="Import Data from CSV", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Reset System", command=self.reset_system)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # قائمة التحليل
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Update Data", command=self.update_display)
        analysis_menu.add_command(label="Retrain Models", command=self.train_all_models)
        
        # قائمة النماذج
        model_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Prediction Model", menu=model_menu)
        
        self.model_var = tk.StringVar(value=self.active_model)
        model_menu.add_radiobutton(label="Linear Model", value="linear", variable=self.model_var, command=self.change_model)
        model_menu.add_radiobutton(label="Polynomial Model (Degree 2)", value="poly2", variable=self.model_var, command=self.change_model)
        model_menu.add_radiobutton(label="Polynomial Model (Degree 3)", value="poly3", variable=self.model_var, command=self.change_model)
        
        # قائمة المساعدة
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Guide", command=self.show_help)
    
    def create_input_frame(self, parent):
        """إنشاء إطار إدخال البيانات"""
        input_frame = tk.LabelFrame(
            parent, 
            text="Data Input", 
            font=("Arial", 12),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # التاريخ والوقت
        date_frame = tk.Frame(input_frame, bg="#f0f0f0")
        date_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            date_frame, 
            text="Date and Time:", 
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=5)
        
        now = datetime.now()
        self.date_var = tk.StringVar(value=now.strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(
            date_frame,
            textvariable=self.date_var,
            width=12
        )
        date_entry.pack(side=tk.LEFT, padx=5)
        
        self.time_var = tk.StringVar(value=now.strftime("%H:%M"))
        time_entry = ttk.Entry(
            date_frame,
            textvariable=self.time_var,
            width=8
        )
        time_entry.pack(side=tk.LEFT, padx=5)
        
        date_btn = ttk.Button(date_frame, text="Now", command=self.set_current_datetime, width=5)
        date_btn.pack(side=tk.LEFT, padx=5)
        
        # درجة الحرارة
        temp_frame = tk.Frame(input_frame, bg="#f0f0f0")
        temp_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            temp_frame, 
            text="Temperature (°C):", 
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=5)
        
        self.temp_var = tk.DoubleVar(value=25.0)
        temp_entry = ttk.Spinbox(
            temp_frame,
            from_=-50.0,
            to=60.0,
            increment=0.1,
            textvariable=self.temp_var,
            width=15
        )
        temp_entry.pack(side=tk.LEFT, padx=5)
        
        # تقييم درجة الحرارة
        rating_frame = tk.Frame(input_frame, bg="#f0f0f0")
        rating_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            rating_frame, 
            text="Rating:", 
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=5)
        
        self.rating_var = tk.StringVar(value="Normal")
        rating_combo = ttk.Combobox(
            rating_frame,
            textvariable=self.rating_var,
            values=["Very Cold", "Cold", "Normal", "Warm", "Very Hot"],
            width=15,
            state="readonly"
        )
        rating_combo.pack(side=tk.LEFT, padx=5)
        
        # ملاحظات إضافية
        notes_frame = tk.Frame(input_frame, bg="#f0f0f0")
        notes_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            notes_frame, 
            text="Notes:", 
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=5)
        
        self.notes_var = tk.StringVar()
        notes_entry = ttk.Entry(
            notes_frame,
            textvariable=self.notes_var,
            width=30
        )
        notes_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # أزرار الإجراءات
        btn_frame = tk.Frame(input_frame, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, pady=10)
        
        add_button = tk.Button(
            btn_frame,
            text="Add Reading",
            font=("Arial", 10),
            bg="#2ecc71",
            fg="white",
            padx=10,
            command=self.add_reading
        )
        add_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        clear_button = tk.Button(
            btn_frame,
            text="Clear Fields",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            padx=10,
            command=self.clear_input_fields
        )
        clear_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        delete_button = tk.Button(
            btn_frame,
            text="Delete Selected",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            padx=10,
            command=self.delete_selected
        )
        delete_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    def create_stats_frame(self, parent):
        """إنشاء إطار الإحصائيات"""
        # ملاحظة: تنفيذ هذه الدالة مطلوب
        pass
    
    def create_graph_frame(self, parent):
        """إنشاء إطار الرسم البياني"""
        # ملاحظة: تنفيذ هذه الدالة مطلوب
        pass
    
    def create_predictions_frame(self, parent):
        """إنشاء إطار التنبؤات المستقبلية"""
        # ملاحظة: تنفيذ هذه الدالة مطلوب
        pass
    
    def create_data_table(self, parent):
        """إنشاء جدول عرض البيانات"""
        # ملاحظة: تنفيذ هذه الدالة مطلوب
        pass