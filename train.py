import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
import joblib
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from sklearn.metrics import classification_report, accuracy_score

data = pd.read_csv('yeni_veri.csv')

# Gerekli sütunları seç
X = data.iloc[:, [1, 4]]  # Özellik sütunları
y = data.iloc[:, 5]  # Etiket sütunu

# IP adresleri gibi string verileri sayısal değerlere dönüştürmek için LabelEncoder kullan
label_encoders = {}
for column in X.columns:
    if X[column].dtype == 'object':
        label_encoders[column] = LabelEncoder()
        X.loc[:, column] = label_encoders[column].fit_transform(X[column])

# Eksik ve sonsuz değerleri kontrol et ve temizle
X = X.apply(pd.to_numeric, errors='coerce')  # Sayısal olmayan değerleri NaN'a dönüştür
X = X.fillna(0)  # NaN değerleri sıfır ile doldur
X.replace([np.inf, -np.inf], 0, inplace=True)  # Sonsuz değerleri sıfır ile değiştir

# Eğitim ve test veri setlerini oluştur
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model oluşturma
model = Sequential()
model.add(Dense(100, activation='relu', input_shape=(X_train.shape[1],)))
model.add(Dense(100, activation='relu'))
model.add(Dense(100, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])

# Modeli eğitme
model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=1)

# Modeli değerlendirme
y_pred = (model.predict(X_test) > 0.5).astype("int32")

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Modeli ve LabelEncoder'ları kaydet
model.save("model_test.h5")
joblib.dump(label_encoders, 'label_encoders.joblib')

# Tahmin yapma
ornek_veri = np.array([[17, 35.264324]])  # protocol=17, Packets/s=35.264324
ornek_veri = np.nan_to_num(ornek_veri)  # NaN değerleri sıfır ile değiştir
ornek_veri[np.isinf(ornek_veri)] = 0  # Sonsuz değerleri sıfır ile değiştir

tahmin = (model.predict(ornek_veri) > 0.5).astype("int32")
# Tahmin çıktısını al
tahmin_deger = tahmin[0][0]

print("Tahmin:", tahmin_deger)


print("Tahmin:", tahmin)
