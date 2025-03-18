# تهيئة محول الميزات متعدد الحدود من الدرجة الثانية
self.poly_features["poly2"] = PolynomialFeatures(degree=2)

# تحويل البيانات إلى صيغة متعددة الحدود
x_poly = self.poly_features["poly2"].fit_transform(x)

# تدريب النموذج على البيانات المحولة
self.models["poly2"] = LinearRegression()
self.models["poly2"].fit(x_poly, y)