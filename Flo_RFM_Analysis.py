# Görev 1: Veriyi Anlama ve Hazırlama

# Adım 1: flo_data_20k.csv verisini okuyunuz.Dataframe'in kopyasını oluşturunuz
import pandas as pd
import datetime as dt
pd.set_option("display.max_columns", None)
#pd.set_option("display.max_rows"), None)
pd.set_option("display.width", 500)
pd.set_option("display.float_format", lambda x: "%.3f" % x)

df_ = pd.read_csv("Datasets/flo_data_20k.csv")
df = df_.copy()

# Adım 2: Veri setinde
#      a:İlk 10 gözlem,
#      b:Değişken isimleri,
#      c:Betimsel istatistik,
#      d:Boş değer,
#      e:Değişken tipleri,incelemesini yapınız.

df.head(10)
df.columns
df.describe().T
df.isnull().sum()
df.info()

# Adım 3: Her bir müşterinin toplam alışveriş sayısı ve harcması için yeni değişkenler oluşturunuz.

df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

# Adım 4: Değişken tiplerini inceleyeniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.

date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.info()

# Adım 5: Alışveriş kanallarındaki müşteri sayısının, toplam alınan ürün sayısının ve toplam harcamaların dağılımına bakınız.

df.groupby("order_channel").agg({"master_id": "count",
                                "order_num_total": "sum",
                                "customer_value_total": "sum"})

#                   master_id   order_num_total     customer_value_total
# order_channel
# Android App         9495        52269.000           7819062.760
# Desktop             2735        10920.000           1610321.460
# Ios App             2833        15351.000           2525999.930
# Mobile              4882        21679.000           3028183.160



# Adım 6: En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.

df.sort_values("customer_value_total", ascending=False)[:10]


# Adım 7: En fazla siparişi veren ilk 10 müşteriyi sıralayanız.

df.sort_values("order_num_total",ascending=False)[:10]

# Adım 8: Veri ön hazırlık sürecini fonksiyonlaştırınız.

def data_prep(dataframe):
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = df.columns[df.columns.str.contains("date")]
    df[date_columns] = df[date_columns].apply(pd.to_datetime)
    return df

data_prep(df)
df.head()
df.info()

# Görev 2: RFM Metriklerinin hesaplanması


df["last_order_date"].max()

today_date = dt.datetime(2021, 6, 1)


rfm_ = df.groupby("master_id").agg({"last_order_date": lambda date: (today_date - date.max()).days,
                                   "customer_value_total": lambda totalprice: totalprice.sum(),
                                   "order_num_total": lambda ordernum: ordernum.sum()})
rfm = rfm_.copy()
rfm.columns = ["recency", "monetary", "frequency"]




# Görev 3: RF Skorunun Hesaplanması

# Adım 1: Recency,Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

rfm["RF_SCORE"] = (rfm["recency_score"].astype(str) +
                   rfm["frequency_score"].astype(str))
rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str)+
                    rfm["frequency_score"].astype(str)+
                    rfm["monetary_score"].astype(str))
rfm.head()


# Görev 4: RF Skorunun Segment Olarak Tanımlanması

# Adım 1: Oluşturulan RF skoarları için segment tanımlamalarını yapınız.

seg_map = {
    r"[1-2][1-2]": "hibernating",
    r"[1-2][3-4]": "at_Risk",
    r"[1-2]5": "cant_loose",
    r"3[1-2]": "about_to_sleep",
    r"33": "need_attention",
    r"[3-4][4-5]": "loyal_customers",
    r"41": "promising",
    r"51": "new_customers",
    r"[4-5][2-3]": "potential_loyalists",
    r"5[4-5]": "champions"
}

# Adım 2: Skorları segmentlere çevirin.

rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)


# Görev 5: Aksiyon Zamanı

# Adım 1: Segmentlerin recency,frequency ve monetary ortalamarını inceleyeniz.

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#                        recency         frequency      monetary
#                       mean count      mean count     mean count
# segment
# about_to_sleep      114.032  1643     2.407  1643  361.649  1643
# at_Risk             242.329  3152     4.470  3152  648.325  3152
# cant_loose          235.159  1194    10.717  1194 1481.652  1194
# champions            17.142  1920     8.965  1920 1410.709  1920
# hibernating         247.426  3589     2.391  3589  362.583  3589
# loyal_customers      82.558  3375     8.356  3375 1216.257  3375
# need_attention      113.037   806     3.739   806  553.437   806
# new_customers        17.976   673     2.000   673  344.049   673
# potential_loyalists  36.870  2925     3.311  2925  533.741  2925
# promising            58.695   668     2.000   668  334.153   668



# Adım 2: RFM analizi yardımıyla aşağıda verilen 2 case için ilgili profildeki müşterileri bulun ve müşteri id'lerini csv olarak kaydediniz.
# a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri
# tercihlerinin üstünde. Bu nedenle markanın tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak
# iletişime geçmek isteniliyor. Sadık müşterilerinden(champions, loyal_customers) ve kadın kategorisinden alışveriş
# yapan kişiler özel olarak iletişim kurulacak müşteriler. Bu müşterilerin id numaralarını csv dosyasına kaydediniz.

5295

dfrfm = pd.merge(df, rfm, on="master_id")

target_segments_customer_ids = dfrfm.loc[(dfrfm["interested_in_categories_12"].str.contains("KADIN"))
          & ((dfrfm["segment"] == "champions") | (dfrfm["segment"] == "loyal_customers")), ["master_id"]]

target_segments_customer_ids.to_csv("target_segments_customer_ids.csv")

target_segments_customer_ids.shape


# b. Erkek ve Çocuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte
# iyi müşteri olan ama uzun süredir alışveriş yapmayan kaybedilmemesi gereken müşteriler, uykuda olanlar ve yeni
# gelen müşteriler özel olarak hedef alınmak isteniyor. Uygun profildeki müşterilerin id'lerini csv dosyasına kaydediniz.

target_segments_customer_ids_kid = dfrfm.loc[((dfrfm["interested_in_categories_12"].str.contains("ERKEK") |
           dfrfm["interested_in_categories_12"].str.contains("COCUK")) &
          ((dfrfm["segment"] == "can't_loose") |
           (dfrfm["segment"] == "about_to_sleep") |
           (dfrfm["segment"] == "new_customers"))), ["master_id"]]

target_segments_customer_ids_kid.to_csv("target_segments_customer_ids_kid.csv")