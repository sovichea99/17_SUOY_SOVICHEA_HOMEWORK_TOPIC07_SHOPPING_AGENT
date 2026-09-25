from pydantic import BaseModel, Field

class SearchProductInput(BaseModel):
    query: str = Field(
        min_length=1,
        description="Product name or category to search for"
    )
class CheckStockInput(BaseModel):
    product_id: int = Field(
        gt=0,
        description="Product ID must be greater than 0."
    )
class BuyProductInput(BaseModel):
    product_id: int = Field(
        gt=0,
        description="Product ID. Must be greater than 0."
    )

    quantity: int = Field(
        gt=0,
        description="Number of products to buy. Must be greater than 0."
    )
class DeleteProductInput(BaseModel):
    product_id: int = Field(
        gt=0,
        description="Product ID. Must be greater than 0."
    )