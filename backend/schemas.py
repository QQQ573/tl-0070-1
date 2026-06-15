from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
import re


RARITY_CHOICES = ["常规", "隐藏", "限定"]
STATUS_CHOICES = ["在库", "已出", "置换中"]
ACQUISITION_CHOICES = ["盲盒", "直购", "置换"]
FLOW_STATUS_CHOICES = ["洽谈中", "已成交", "已撤回"]
PLATFORM_CHOICES = ["闲鱼", "千岛", "线下"]


class ItemCreate(BaseModel):
    series: str
    style_id: str
    name: str
    rarity: str
    acquisition_method: str
    purchase_price: float = 0.0
    status: str = "在库"
    batch_no: Optional[str] = None
    image_path: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("rarity")
    @classmethod
    def validate_rarity(cls, v):
        if v not in RARITY_CHOICES:
            raise ValueError(f"稀有度必须为: {RARITY_CHOICES}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in STATUS_CHOICES:
            raise ValueError(f"状态必须为: {STATUS_CHOICES}")
        return v

    @field_validator("acquisition_method")
    @classmethod
    def validate_acquisition(cls, v):
        if v not in ACQUISITION_CHOICES:
            raise ValueError(f"获取方式必须为: {ACQUISITION_CHOICES}")
        return v

    @field_validator("batch_no")
    @classmethod
    def validate_batch_no(cls, v, info):
        rarity = info.data.get("rarity")
        if rarity == "隐藏":
            if not v:
                raise ValueError("隐藏款必须填写获取批次号")
            if not re.match(r"^[A-Za-z]{2}\d{6}-\d{2}$", v):
                raise ValueError("批次号格式: 两位字母+六位数字-两位数字 (如 AB202601-01)")
        return v


class ItemUpdate(BaseModel):
    series: Optional[str] = None
    style_id: Optional[str] = None
    name: Optional[str] = None
    rarity: Optional[str] = None
    acquisition_method: Optional[str] = None
    purchase_price: Optional[float] = None
    status: Optional[str] = None
    batch_no: Optional[str] = None
    image_path: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("rarity")
    @classmethod
    def validate_rarity(cls, v):
        if v is not None and v not in RARITY_CHOICES:
            raise ValueError(f"稀有度必须为: {RARITY_CHOICES}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in STATUS_CHOICES:
            raise ValueError(f"状态必须为: {STATUS_CHOICES}")
        return v

    @field_validator("acquisition_method")
    @classmethod
    def validate_acquisition(cls, v):
        if v is not None and v not in ACQUISITION_CHOICES:
            raise ValueError(f"获取方式必须为: {ACQUISITION_CHOICES}")
        return v

    @field_validator("batch_no")
    @classmethod
    def validate_batch_no(cls, v, info):
        rarity = info.data.get("rarity")
        if rarity == "隐藏":
            if not v:
                raise ValueError("隐藏款必须填写获取批次号")
            if not re.match(r"^[A-Za-z]{2}\d{6}-\d{2}$", v):
                raise ValueError("批次号格式: 两位字母+六位数字-两位数字 (如 AB202601-01)")
        return v


class ItemOut(BaseModel):
    id: int
    series: str
    style_id: str
    name: str
    rarity: str
    acquisition_method: str
    purchase_price: float
    status: str
    batch_no: Optional[str] = None
    image_path: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ItemPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ItemOut]


class ExchangeCreate(BaseModel):
    item_id: int
    exchange_date: str
    counterparty: str
    price_difference: float = 0.0
    flow_status: str = "洽谈中"
    notes: Optional[str] = None

    @field_validator("flow_status")
    @classmethod
    def validate_flow_status(cls, v):
        if v not in FLOW_STATUS_CHOICES:
            raise ValueError(f"流转状态必须为: {FLOW_STATUS_CHOICES}")
        return v

    @field_validator("exchange_date")
    @classmethod
    def validate_date(cls, v):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("日期格式必须为 YYYY-MM-DD")
        return v


class ExchangeUpdate(BaseModel):
    item_id: Optional[int] = None
    exchange_date: Optional[str] = None
    counterparty: Optional[str] = None
    price_difference: Optional[float] = None
    flow_status: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("flow_status")
    @classmethod
    def validate_flow_status(cls, v):
        if v is not None and v not in FLOW_STATUS_CHOICES:
            raise ValueError(f"流转状态必须为: {FLOW_STATUS_CHOICES}")
        return v

    @field_validator("exchange_date")
    @classmethod
    def validate_date(cls, v):
        if v is not None and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("日期格式必须为 YYYY-MM-DD")
        return v


class ExchangeOut(BaseModel):
    id: int
    item_id: int
    exchange_date: str
    counterparty: str
    price_difference: float
    flow_status: str = "洽谈中"
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    item_series: Optional[str] = None
    item_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ExchangePage(BaseModel):
    total: int
    page: int
    page_size: int
    exchanges: list[ExchangeOut]


class MarketPriceCreate(BaseModel):
    style_id: str
    platform: str
    deal_price: float
    record_date: str
    notes: Optional[str] = None

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v):
        if v not in PLATFORM_CHOICES:
            raise ValueError(f"平台必须为: {PLATFORM_CHOICES}")
        return v

    @field_validator("deal_price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("成交价必须大于 0")
        return v

    @field_validator("record_date")
    @classmethod
    def validate_record_date(cls, v):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("记录日期格式必须为 YYYY-MM-DD")
        return v


class MarketPriceUpdate(BaseModel):
    style_id: Optional[str] = None
    platform: Optional[str] = None
    deal_price: Optional[float] = None
    record_date: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v):
        if v is not None and v not in PLATFORM_CHOICES:
            raise ValueError(f"平台必须为: {PLATFORM_CHOICES}")
        return v

    @field_validator("deal_price")
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError("成交价必须大于 0")
        return v

    @field_validator("record_date")
    @classmethod
    def validate_record_date(cls, v):
        if v is not None and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("记录日期格式必须为 YYYY-MM-DD")
        return v


class MarketPriceOut(BaseModel):
    id: int
    style_id: str
    platform: str
    deal_price: float
    record_date: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MarketPricePage(BaseModel):
    total: int
    page: int
    page_size: int
    prices: list[MarketPriceOut]


class MarketPriceTrend(BaseModel):
    style_id: str
    records: list[MarketPriceOut]
    latest_price: Optional[float] = None
    purchase_price: Optional[float] = None
    diff_percent: Optional[float] = None


class SeriesStat(BaseModel):
    series: str
    count: int
    total_value: float


class OverviewStats(BaseModel):
    total_items: int
    instock_count: int
    out_count: int
    exchanging_count: int
    hidden_count: int
    instock_value: float
    series_stats: list[SeriesStat]


class MonthlyExchangeStat(BaseModel):
    month: str
    count: int


class DashboardStats(BaseModel):
    overview: OverviewStats
    monthly_exchanges: list[MonthlyExchangeStat]


class RecycleItemOut(ItemOut):
    pass


class RecycleExchangeOut(ExchangeOut):
    pass


class RecyclePage(BaseModel):
    items: list[RecycleItemOut]
    exchanges: list[RecycleExchangeOut]
