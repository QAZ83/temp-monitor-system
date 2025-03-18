import numpy as np              # للعمليات الرياضية والمصفوفات
import pandas as pd             # لمعالجة وتحليل البيانات المنظمة
import matplotlib.pyplot as plt # لإنشاء الرسومات البيانية
import tkinter as tk            # لبناء واجهة المستخدم الرسومية
import joblib                   # لحفظ واسترجاع نماذج التعلم الآلي
from sklearn.linear_model import LinearRegression          # لنموذج الانحدار الخطي
from sklearn.preprocessing import PolynomialFeatures       # لتحويل الميزات إلى صيغة متعددة الحدود
from sklearn.metrics import mean_squared_error, r2_score   # لقياس دقة النماذج