from datetime import datetime

class ProduceListing:
    """Model for produce listing document"""
    
    def __init__(self, farmer_id, farmer_name, produce_type, quantity, price_per_kg, 
                 market_location, harvest_date, variety="", quality="standard", description=""):
        self.farmer_id = farmer_id
        self.farmer_name = farmer_name
        self.produce = {
            "type": produce_type,
            "variety": variety,
            "quality": quality
        }
        self.quantity = float(quantity)
        self.price_per_kg = float(price_per_kg)
        self.market_location = market_location
        self.harvest_date = harvest_date
        self.description = description
        self.status = "active"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary for MongoDB insertion"""
        return {
            "farmer_id": self.farmer_id,
            "farmer_name": self.farmer_name,
            "produce": self.produce,
            "quantity": self.quantity,
            "price_per_kg": self.price_per_kg,
            "market_location": self.market_location,
            "harvest_date": self.harvest_date,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def validate_price(price):
        """Validate price is positive"""
        return price > 0
    
    @staticmethod
    def validate_quantity(quantity):
        """Validate quantity is positive"""
        return quantity > 0

class PriceHistory:
    """Model for price history document"""
    
    def __init__(self, produce_type, market_location, price_per_kg, listing_id, quantity=0, old_price=None):
        self.produce_type = produce_type
        self.market_location = market_location
        self.price_per_kg = price_per_kg
        self.date = datetime.now()
        self.listing_id = listing_id
        self.quantity = quantity
        if old_price:
            self.old_price = old_price
    
    def to_dict(self):
        """Convert to dictionary for MongoDB insertion"""
        data = {
            "produce_type": self.produce_type,
            "market_location": self.market_location,
            "price_per_kg": self.price_per_kg,
            "date": self.date,
            "listing_id": self.listing_id,
            "quantity": self.quantity
        }
        if hasattr(self, 'old_price'):
            data["old_price"] = self.old_price
        return data