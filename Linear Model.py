# تهيئة نموذج خطي بسيط
self.models["linear"] = LinearRegression()

# تدريب النموذج الخطي
x = np.array(range(len(self.df))).reshape(-1, 1)  # المتغير المستقل (الزمن)
y = np.array(self.df['Temperature'])               # المتغير التابع (درجة الحرارة)
self.models["linear"].fit(x, y)