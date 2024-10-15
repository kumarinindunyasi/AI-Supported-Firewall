import pandas as pd
import numpy as np
from keras.models import load_model
import joblib
import os

# Modeli ve LabelEncoder'ları yükle
model = load_model('model_test.h5')
label_encoders = joblib.load('label_encoders.joblib')

# Yeni verileri yükle
new_data = pd.read_csv("yeni_veri.csv")  # Yeni veri dosyasının adı

# Gerekli sütunları seç
X_new = new_data.iloc[:, [1, 4]]  # Özellik sütunları
ip_addresses = new_data.iloc[:,0]# IP adreslerini içeren sütun

# IP adresleri gibi string verileri sayısal değerlere dönüştürmek için LabelEncoder kullan
for column in X_new.columns:
    if X_new[column].dtype == 'object' and column in label_encoders:
        X_new.loc[:, column] = label_encoders[column].transform(X_new[column])

# Eksik ve sonsuz değerleri kontrol et ve temizle
X_new = X_new.apply(pd.to_numeric, errors='coerce')  # Sayısal olmayan değerleri NaN'a dönüştür
X_new = X_new.fillna(0)  # NaN değerleri sıfır ile doldur
X_new.replace([np.inf, -np.inf], 0, inplace=True)  # Sonsuz değerleri sıfır ile değiştir

# Tahmin yap
predictions = (model.predict(X_new) > 0.5).astype("int32")

# Sonuçları dosyalara yaz
with open("blacklist.txt", "w") as blacklist, open("whitelist.txt", "w") as whitelist:
    for ip, pred in zip(ip_addresses, predictions):
        if pred == 1:
            blacklist.write(f"{ip}\n")
        else:
            whitelist.write(f"{ip}\n")
            
# Dosyanın erişim izinlerini ayarla
os.chmod("blacklist.txt", 0o666)
