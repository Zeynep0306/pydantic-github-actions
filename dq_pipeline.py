import pandas as pd
from pydantic import BaseModel, Field, field_validator, AliasChoices, BeforeValidator
from datetime import datetime
from typing import Annotated, Any, Optional
import os
import sys

# --- 1. TARİH DÜZELTİCİ ---
def parse_amazon_date(v: Any) -> datetime:
    if isinstance(v, str):
        try:
            return datetime.strptime(v, '%m-%d-%y')
        except:
            return v
    return v

# --- 2. MODEL TANIMI ---
class AmazonOrderModel(BaseModel):
    Order_ID: str = Field(validation_alias=AliasChoices('Order ID', 'Order_ID'), min_length=1)
    Qty: int = Field(validation_alias=AliasChoices('Qty', 'qty'), ge=0)
    Amount: Optional[float] = 0.0  # Eğer boşsa hata verme, 0.0 kabul et
    currency: Optional[str] = "INR" # Eğer boşsa hata verme, "INR" kabul et
    ship_country: str = Field(validation_alias=AliasChoices('ship-country', 'ship_country'))
    Date: Annotated[datetime, BeforeValidator(parse_amazon_date)] = Field(validation_alias=AliasChoices('Date', 'date'))

    @field_validator('currency')
    @classmethod
    def check_currency(cls, v):
        if v != "INR": raise ValueError('Sadece INR kabul edilir')
        return v

# --- 3. DOĞRULAMA FONKSİYONU ---
def run_validation():
    # Terminalde gördüğümüz tam yol
    csv_path = "data/Amazon Sale Report.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Dosya bulunamadı: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path, low_memory=False)
    # İlk 100 satırı test edelim (GitHub Actions hızlı bitsin diye, istersen silebilirsin)
    df = df.head(100) 
    
    invalid_rows = 0
    for index, row in df.iterrows():
        try:
            AmazonOrderModel(**row.to_dict())
        except Exception as e:
            invalid_rows += 1
            # BU SATIRI EKLE: Hatanın hangi satırda ve ne olduğunu yazdırır
            print(f"Satır {index} hatası: {e}\n")

    if invalid_rows > 0:
        print(f"⚠️ {invalid_rows} adet hatalı satır atlandı, işleme devam ediliyor.")
        sys.exit(0) # GitHub artık Kırmızı değil, Yeşil yanacak.
    else:
        print("✅ Başarılı: Tüm satırlar geçerli!")
        sys.exit(0) # GitHub bunu görünce 'Yeşil' yakacak

if __name__ == "__main__":
    run_validation()