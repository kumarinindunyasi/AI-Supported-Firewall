import pandas as pd

# CSV dosyasını yükle
df = pd.read_csv("islenmemis_veri.csv")
#df = df.iloc[:1500]

# "Source IP" ve "Fwd Packets/s" sütunlarını seç
df_filtered = df[["Src IP","Protocol", "Flow Duration", "Total Fwd Packet"]].copy()

esik_degeri = 30

# "Packets/s" sütununu ekle
df_filtered.loc[:, "Packets/s"] = df_filtered["Total Fwd Packet"] / (df_filtered["Flow Duration"] / 1000000)

# "DDOS Attack" sütununu ekle
df_filtered.loc[:, 'DDOS Attack'] = df_filtered["Packets/s"] > esik_degeri

# Yeni CSV dosyasına yaz
df_filtered.to_csv("yeni_veri.csv", index=False)
