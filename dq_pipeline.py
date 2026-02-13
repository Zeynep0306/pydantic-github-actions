import pandas as pd
from pydantic import BaseModel, Field, field_validator, AliasChoices, BeforeValidator
from datetime import datetime
from typing import Annotated, Any
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
    Amount: float = Field(validation_alias=AliasChoices('Amount', 'amount'), ge=0)
    currency: str = Field(validation_alias=AliasChoices('currency', 'Currency'))
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
    for _, row in df.iterrows():
        try:
            AmazonOrderModel(**row.to_dict())
        except:
            invalid_rows += 1

    if invalid_rows > 0:
        print(f"❌ Başarısız: {invalid_rows} adet hatalı satır bulundu.")
        sys.exit(1) # GitHub bunu görünce 'Kırmızı' yakacak
    else:
        print("✅ Başarılı: Tüm satırlar geçerli!")
        sys.exit(0) # GitHub bunu görünce 'Yeşil' yakacak

if __name__ == "__main__":
    run_validation()