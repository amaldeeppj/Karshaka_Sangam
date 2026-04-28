from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from database import db
import json

app = Flask(__name__)
app.secret_key = 'karshaka-sangham-secret-key-2026'

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

@app.route('/')
def index():
    """Home page - show all active listings"""
    listings = db.get_all_listings()
    summary = db.get_summary_stats()
    
    # Get unique produce types and markets for filters with error handling
    all_listings = list(db.listings.find({"status": "active"}))
    
    # Filter out documents that don't have the required fields
    valid_listings = []
    for l in all_listings:
        if 'produce' in l and 'type' in l.get('produce', {}) and 'market_location' in l:
            valid_listings.append(l)
    
    produce_types = sorted(set([l['produce']['type'] for l in valid_listings if 'produce' in l]))
    markets = sorted(set([l['market_location'] for l in valid_listings if 'market_location' in l]))
    
    return render_template('index.html', 
                         listings=listings, 
                         summary=summary,
                         produce_types=produce_types,
                         markets=markets)

@app.route('/add-listing', methods=['GET', 'POST'])
def add_listing():
    """Add a new farmer listing"""
    if request.method == 'POST':
        try:
            listing = {
                "farmer_id": request.form['farmer_id'],
                "farmer_name": request.form['farmer_name'],
                "produce": {
                    "type": request.form['produce_type'],
                    "variety": request.form.get('variety', ''),
                    "quality": request.form.get('quality', 'standard')
                },
                "quantity": float(request.form['quantity']),
                "price_per_kg": float(request.form['price_per_kg']),
                "market_location": request.form['market_location'],
                "harvest_date": datetime.strptime(request.form['harvest_date'], '%Y-%m-%d'),
                "description": request.form.get('description', '')
            }
            
            result = db.add_listing(listing)
            flash('Listing added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding listing: {str(e)}', 'error')
            return redirect(url_for('add_listing'))
    
    return render_template('add_listing.html')

@app.route('/edit-listing/<listing_id>', methods=['GET', 'POST'])
def edit_listing(listing_id):
    """Edit an existing listing"""
    if request.method == 'POST':
        try:
            update_data = {
                "produce": {
                    "type": request.form['produce_type'],
                    "variety": request.form.get('variety', ''),
                    "quality": request.form.get('quality', 'standard')
                },
                "quantity": float(request.form['quantity']),
                "price_per_kg": float(request.form['price_per_kg']),
                "market_location": request.form['market_location'],
                "harvest_date": datetime.strptime(request.form['harvest_date'], '%Y-%m-%d'),
                "description": request.form.get('description', '')
            }
            
            db.update_listing(ObjectId(listing_id), update_data)
            flash('Listing updated successfully!', 'success')
            return redirect(url_for('manage_listings'))
        except Exception as e:
            flash(f'Error updating listing: {str(e)}', 'error')
            return redirect(url_for('edit_listing', listing_id=listing_id))
    
    listing = db.get_listing_by_id(listing_id)
    if not listing:
        flash('Listing not found', 'error')
        return redirect(url_for('manage_listings'))
    return render_template('edit_listing.html', listing=listing)

@app.route('/delete-listing/<listing_id>')
def delete_listing(listing_id):
    """Delete a listing (soft delete)"""
    try:
        db.delete_listing(ObjectId(listing_id))
        flash('Listing deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting listing: {str(e)}', 'error')
    return redirect(url_for('manage_listings'))

@app.route('/manage-listings')
def manage_listings():
    """Manage all listings for a farmer"""
    farmer_id = request.args.get('farmer_id', 'FARMER001')
    listings = db.get_farmer_listings(farmer_id)
    return render_template('manage_listings.html', listings=listings)

@app.route('/market-index')
def market_index():
    """Display market price index"""
    try:
        price_index = db.get_market_price_index()
        market_rankings = db.get_market_rankings()
        summary = db.get_summary_stats()
        
        return render_template('market_index.html', 
                             price_index=price_index,
                             market_rankings=market_rankings,
                             summary=summary)
    except Exception as e:
        flash(f'Error loading market index: {str(e)}', 'error')
        return render_template('market_index.html', 
                             price_index=[],
                             market_rankings=[],
                             summary={})

@app.route('/api/price-trends/<produce_type>')
def api_price_trends(produce_type):
    """API endpoint for price trends"""
    try:
        trends = db.get_price_trends(produce_type)
        return jsonify([serialize_doc(t) for t in trends])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/market-stats')
def api_market_stats():
    """API endpoint for market statistics"""
    try:
        stats = db.get_market_rankings()
        return jsonify([serialize_doc(s) for s in stats])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/filter-listings')
def filter_listings():
    """Filter listings by produce type and market"""
    produce_type = request.args.get('produce_type')
    market = request.args.get('market')
    
    query = {"status": "active"}
    if produce_type and produce_type != '':
        query["produce.type"] = produce_type
    if market and market != '':
        query["market_location"] = market
    
    listings = list(db.listings.find(query))
    # Convert ObjectId to string for JSON serialization
    for listing in listings:
        listing['_id'] = str(listing['_id'])
        if 'harvest_date' in listing and listing['harvest_date']:
            listing['harvest_date'] = listing['harvest_date'].strftime('%Y-%m-%d')
        else:
            listing['harvest_date'] = 'N/A'
    
    return jsonify(listings)

@app.route('/vegetable-rankings')
def vegetable_rankings():
    """Display rankings for each vegetable"""
    try:
        rankings = db.get_vegetable_rankings()
        summary = db.get_summary_stats()
        return render_template('vegetable_rankings.html', rankings=rankings, summary=summary)
    except Exception as e:
        flash(f'Error loading vegetable rankings: {str(e)}', 'error')
        return render_template('vegetable_rankings.html', rankings=[], summary={})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)