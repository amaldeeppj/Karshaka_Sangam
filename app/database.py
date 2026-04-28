from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

class MongoDB:
    def __init__(self):
        # Connect to MongoDB
        #mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017/')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['karshaka_sangham']
        
        # Collections
        self.listings = self.db['listings']
        self.markets = self.db['markets']
        self.price_history = self.db['price_history']
        
        # Create indexes for better performance
        self.listings.create_index([("farmer_id", 1), ("status", 1)])
        self.listings.create_index([("produce.type", 1), ("market_location", 1)])
        self.price_history.create_index([("produce_type", 1), ("market_location", 1), ("date", 1)])

    def get_all_listings(self, status='active'):
        """Get all active listings"""
        return list(self.listings.find({"status": status}))

    def get_farmer_listings(self, farmer_id):
        """Get listings for specific farmer"""
        return list(self.listings.find({"farmer_id": farmer_id, "status": "active"}))

    def get_listing_by_id(self, listing_id):
        """Get a single listing by ID"""
        try:
            return self.listings.find_one({"_id": ObjectId(listing_id)})
        except:
            return None

    def add_listing(self, listing_data):
        """Add a new listing"""
        listing_data['created_at'] = datetime.now()
        listing_data['updated_at'] = datetime.now()
        listing_data['status'] = 'active'
        
        result = self.listings.insert_one(listing_data)
        
        # Add to price history
        self.price_history.insert_one({
            "produce_type": listing_data['produce']['type'],
            "market_location": listing_data['market_location'],
            "price_per_kg": listing_data['price_per_kg'],
            "date": datetime.now(),
            "listing_id": result.inserted_id,
            "quantity": listing_data['quantity']
        })
        
        return result.inserted_id

    def update_listing(self, listing_id, update_data):
        """Update a listing"""
        try:
            update_data['updated_at'] = datetime.now()
            
            # Get old listing to check price change
            old_listing = self.listings.find_one({"_id": ObjectId(listing_id)})
            
            result = self.listings.update_one(
                {"_id": ObjectId(listing_id)},
                {"$set": update_data}
            )
            
            # If price changed, add to price history
            if 'price_per_kg' in update_data and old_listing:
                if old_listing.get('price_per_kg', 0) != update_data['price_per_kg']:
                    self.price_history.insert_one({
                        "produce_type": old_listing['produce']['type'],
                        "market_location": old_listing['market_location'],
                        "price_per_kg": update_data['price_per_kg'],
                        "date": datetime.now(),
                        "listing_id": listing_id,
                        "old_price": old_listing.get('price_per_kg', 0)
                    })
            
            return result.modified_count
        except Exception as e:
            print(f"Error updating listing: {e}")
            return 0

    def delete_listing(self, listing_id):
        """Soft delete a listing"""
        try:
            return self.listings.update_one(
                {"_id": ObjectId(listing_id)},
                {"$set": {"status": "deleted", "updated_at": datetime.now()}}
            )
        except Exception as e:
            print(f"Error deleting listing: {e}")
            return None

    def get_market_price_index(self):
        """Calculate market price index using aggregation pipeline"""
        try:
            pipeline = [
                {
                    "$match": {
                        "status": "active",
                        "produce": {"$exists": True},
                        "produce.type": {"$exists": True}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "produce_type": "$produce.type",
                            "market_location": "$market_location"
                        },
                        "average_price": {"$avg": "$price_per_kg"},
                        "min_price": {"$min": "$price_per_kg"},
                        "max_price": {"$max": "$price_per_kg"},
                        "total_listings": {"$sum": 1},
                        "total_quantity": {"$sum": "$quantity"}
                    }
                },
                {
                    "$sort": {
                        "_id.produce_type": 1,
                        "_id.market_location": 1
                    }
                },
                {
                    "$group": {
                        "_id": "$_id.produce_type",
                        "markets": {
                            "$push": {
                                "market": "$_id.market_location",
                                "average_price": {"$round": ["$average_price", 2]},
                                "min_price": {"$round": ["$min_price", 2]},
                                "max_price": {"$round": ["$max_price", 2]},
                                "listings_count": "$total_listings",
                                "total_quantity": "$total_quantity"
                            }
                        },
                        "overall_avg_price": {"$avg": "$average_price"},
                        "total_markets": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"overall_avg_price": -1}
                }
            ]
            
            return list(self.listings.aggregate(pipeline))
        except Exception as e:
            print(f"Error in market price index: {e}")
            return []

    def get_price_trends(self, produce_type, days=30):
        """Get price trends for specific produce using aggregation"""
        try:
            pipeline = [
                {
                    "$match": {
                        "produce_type": produce_type,
                        "date": {"$gte": datetime.now() - timedelta(days=days)}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                            "market": "$market_location"
                        },
                        "avg_price": {"$avg": "$price_per_kg"}
                    }
                },
                {
                    "$sort": {"_id.date": 1, "_id.market": 1}
                }
            ]
            
            return list(self.price_history.aggregate(pipeline))
        except Exception as e:
            print(f"Error in price trends: {e}")
            return []

    def get_market_rankings(self):
        """Get market rankings based on price competitiveness"""
        try:
            pipeline = [
                {
                    "$match": {
                        "status": "active",
                        "produce": {"$exists": True}
                    }
                },
                {
                    "$group": {
                        "_id": "$market_location",
                        "avg_price_all": {"$avg": "$price_per_kg"},
                        "total_listings": {"$sum": 1},
                        "unique_products": {"$addToSet": "$produce.type"}
                    }
                },
                {
                    "$project": {
                        "market": "$_id",
                        "avg_price_all": {"$round": ["$avg_price_all", 2]},
                        "total_listings": 1,
                        "unique_products_count": {"$size": "$unique_products"},
                        "competitiveness_score": {
                            "$cond": [
                                {"$eq": ["$avg_price_all", 0]},
                                0,
                                {"$divide": [100, "$avg_price_all"]}
                            ]
                        }
                    }
                },
                {
                    "$sort": {"avg_price_all": 1}
                }
            ]
            
            return list(self.listings.aggregate(pipeline))
        except Exception as e:
            print(f"Error in market rankings: {e}")
            return []

    def get_summary_stats(self):
        """Get summary statistics using aggregation"""
        try:
            pipeline = [
                {
                    "$match": {
                        "status": "active",
                        "produce": {"$exists": True}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_listings": {"$sum": 1},
                        "total_farmers": {"$addToSet": "$farmer_id"},
                        "total_quantity": {"$sum": "$quantity"},
                        "avg_price_all": {"$avg": "$price_per_kg"},
                        "total_markets": {"$addToSet": "$market_location"}
                    }
                },
                {
                    "$project": {
                        "total_listings": 1,
                        "total_farmers_count": {"$size": "$total_farmers"},
                        "total_quantity": 1,
                        "avg_price_all": {"$round": ["$avg_price_all", 2]},
                        "total_markets_count": {"$size": "$total_markets"}
                    }
                }
            ]
            
            result = list(self.listings.aggregate(pipeline))
            return result[0] if result else {}
        except Exception as e:
            print(f"Error in summary stats: {e}")
            return {}

    def get_produce_by_type(self, produce_type):
        """Get all listings for a specific produce type"""
        return list(self.listings.find({
            "status": "active",
            "produce.type": produce_type
        }))

    def get_vegetable_rankings(self):
        """Get rankings for each vegetable across different markets"""
        try:
            # First, get all grouped data
            group_pipeline = [
                {
                    "$match": {
                        "status": "active",
                        "produce": {"$exists": True}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "vegetable": "$produce.type",
                            "market": "$market_location"
                        },
                        "avg_price": {"$avg": "$price_per_kg"},
                        "total_listings": {"$sum": 1},
                        "total_quantity": {"$sum": "$quantity"}
                    }
                }
            ]
            
            grouped_data = list(self.listings.aggregate(group_pipeline))
            
            # Organize by vegetable
            vegetable_data = {}
            for item in grouped_data:
                veg = item['_id']['vegetable']
                market = item['_id']['market']
                
                if veg not in vegetable_data:
                    vegetable_data[veg] = []
                
                vegetable_data[veg].append({
                    'market': market,
                    'avg_price': round(item['avg_price'], 2),
                    'total_listings': item['total_listings'],
                    'total_quantity': item['total_quantity']
                })
            
            # Sort and add ranks
            result = []
            for veg, markets in vegetable_data.items():
                # Sort by price (lowest to highest)
                markets.sort(key=lambda x: x['avg_price'])
                
                # Add rank (1 for cheapest, 2 for next, etc.)
                for idx, market in enumerate(markets, 1):
                    market['rank'] = idx
                
                result.append({
                    '_id': veg,
                    'markets': markets
                })
            
            # Sort vegetables alphabetically
            result.sort(key=lambda x: x['_id'])
            
            return result
            
        except Exception as e:
            print(f"Error in vegetable rankings: {e}")
            return []

# Initialize database connection
db = MongoDB()
