from database import db
from datetime import datetime, timedelta
import random

# Sample produce types with base prices
produce_data = {
    'tomato': {'base_price': 40, 'varieties': ['Cherry', 'Roma', 'Beefsteak']},
    'potato': {'base_price': 30, 'varieties': ['Russet', 'Red', 'Yellow']},
    'onion': {'base_price': 35, 'varieties': ['Red', 'White', 'Yellow']},
    'carrot': {'base_price': 45, 'varieties': ['Orange', 'Purple', 'Baby']},
    'cabbage': {'base_price': 25, 'varieties': ['Green', 'Red', 'Savoy']},
    'cauliflower': {'base_price': 35, 'varieties': ['White', 'Purple', 'Green']},
    'brinjal': {'base_price': 30, 'varieties': ['Round', 'Long', 'Japanese']},
    'ladyfinger': {'base_price': 40, 'varieties': ['Green', 'Red']},
    'spinach': {'base_price': 20, 'varieties': ['Baby', 'Regular']},
    'capsicum': {'base_price': 60, 'varieties': ['Green', 'Red', 'Yellow']}
}

markets = [
    'Ernakulam Market', 'Thrissur Market', 'Kozhikode Market', 
    'Kottayam Market', 'Palakkad Market', 'Alappuzha Market',
    'Kollam Market', 'Kannur Market'
]

farmer_names = [
    'Ramesh Nair', 'Suresh Menon', 'Lakshmi Amma', 'Krishnan Nambiar', 
    'Radha Devi', 'Mohan Das', 'Saraswati Amma', 'Gopalakrishnan',
    'Anitha Kumari', 'Rajendran Pillai'
]

qualities = ['premium', 'standard', 'economy']

def generate_sample_data(num_listings=50):
    """Generate sample listings for demonstration"""
    print("Clearing existing data...")
    db.listings.delete_many({})
    db.price_history.delete_many({})
    
    print(f"Generating {num_listings} sample listings...")
    
    for i in range(num_listings):
        # Randomly select produce
        produce_type = random.choice(list(produce_data.keys()))
        produce_info = produce_data[produce_type]
        
        # Randomly select market
        market = random.choice(markets)
        
        # Random price variation (base price ± 20)
        base_price = produce_info['base_price']
        price_variation = random.randint(-15, 25)
        price = max(15, base_price + price_variation)  # Ensure minimum price of ₹15
        
        # Random quantity between 20 and 500 kg
        quantity = random.randint(20, 500)
        
        # Random harvest date (within last 7 days)
        harvest_date = datetime.now() - timedelta(days=random.randint(0, 7))
        
        # Random farmer
        farmer_name = random.choice(farmer_names)
        farmer_id = f"FARM{random.randint(100, 999)}"
        
        # Random quality
        quality = random.choice(qualities)
        
        # Adjust price based on quality
        if quality == 'premium':
            price = price * 1.2
        elif quality == 'economy':
            price = price * 0.8
        
        price = round(price, 2)
        
        # Random variety
        variety = random.choice(produce_info['varieties'])
        
        listing = {
            "farmer_id": farmer_id,
            "farmer_name": farmer_name,
            "produce": {
                "type": produce_type,
                "variety": f"{variety} {produce_type}",
                "quality": quality
            },
            "quantity": quantity,
            "price_per_kg": price,
            "market_location": market,
            "harvest_date": harvest_date,
            "description": f"Fresh {quality} quality {produce_type} harvested from our organic farm. Available for immediate delivery.",
            "status": "active",
            "created_at": datetime.now() - timedelta(days=random.randint(0, 10)),
            "updated_at": datetime.now()
        }
        
        # Add listing to database
        result = db.add_listing(listing)
        
        # Add some historical price data for trends
        for days_ago in range(1, 8):  # Add 7 days of history
            historical_price = price + random.randint(-10, 10)
            historical_price = max(15, historical_price)
            db.price_history.insert_one({
                "produce_type": produce_type,
                "market_location": market,
                "price_per_kg": historical_price,
                "date": datetime.now() - timedelta(days=days_ago),
                "listing_id": result,
                "quantity": quantity
            })
        
        print(f"Added: {quality} {produce_type} at ₹{price}/kg in {market} (Farmer: {farmer_name})")
    
    print("\n" + "="*50)
    print("Sample data generation complete!")
    print(f"Total active listings: {db.listings.count_documents({'status': 'active'})}")
    print(f"Total price records: {db.price_history.count_documents({})}")
    print("="*50)
    
    # Display summary statistics
    summary = db.get_summary_stats()
    print("\n📊 Summary Statistics:")
    print(f"  • Total Listings: {summary.get('total_listings', 0)}")
    print(f"  • Total Farmers: {summary.get('total_farmers_count', 0)}")
    print(f"  • Total Quantity: {summary.get('total_quantity', 0)} kg")
    print(f"  • Average Price: ₹{summary.get('avg_price_all', 0)}/kg")
    print(f"  • Markets Covered: {summary.get('total_markets_count', 0)}")

def add_specific_listings():
    """Add some specific example listings"""
    print("\nAdding specific example listings...")
    
    examples = [
        {
            "farmer_id": "FARM001",
            "farmer_name": "Ramesh Nair",
            "produce": {
                "type": "tomato",
                "variety": "Organic Cherry Tomato",
                "quality": "premium"
            },
            "quantity": 100,
            "price_per_kg": 65.00,
            "market_location": "Ernakulam Market",
            "harvest_date": datetime.now(),
            "description": "Organic cherry tomatoes, sweet and fresh!"
        },
        {
            "farmer_id": "FARM002",
            "farmer_name": "Lakshmi Amma",
            "produce": {
                "type": "potato",
                "variety": "Kufri Jyoti",
                "quality": "standard"
            },
            "quantity": 500,
            "price_per_kg": 28.00,
            "market_location": "Thrissur Market",
            "harvest_date": datetime.now(),
            "description": "High yield variety, good for all purposes"
        },
        {
            "farmer_id": "FARM003",
            "farmer_name": "Krishnan Nambiar",
            "produce": {
                "type": "carrot",
                "variety": "Orange Carrot",
                "quality": "premium"
            },
            "quantity": 75,
            "price_per_kg": 55.00,
            "market_location": "Kozhikode Market",
            "harvest_date": datetime.now(),
            "description": "Sweet and crunchy organic carrots"
        }
    ]
    
    for example in examples:
        try:
            result = db.add_listing(example)
            print(f"Added: {example['produce']['type']} - {example['farmer_name']}")
        except Exception as e:
            print(f"Error adding {example['produce']['type']}: {e}")

if __name__ == "__main__":
    print("🌾 Karshaka Sangham - Sample Data Generator")
    print("="*50)
    generate_sample_data(50)
    add_specific_listings()
    print("\n✅ Setup complete! Run 'python app.py' to start the application")