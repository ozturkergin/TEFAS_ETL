from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Path to the CSV file
csv_file = "/home/erginozturk/fetched_data.csv"

@app.route("/filter", methods=["GET"])
def filter_data():
    symbol = request.args.get("symbol")
    symbol_rsi = request.args.get("symbol_rsi")
    
    if not symbol and not symbol_rsi:
        return jsonify({"error": "symbol or symbol_rsi parameter is required"}), 400
    
    try:
        # Read the CSV file
        data = pd.read_csv(csv_file)
        
        # Check if required columns exist
        required_columns = ['FONKODU', 'TARIH', 'FIYAT', 'RSI_14']
        for column in required_columns:
            if column not in data.columns:
                return jsonify({"error": f"The '{column}' column is missing in the CSV file"}), 500
        
        if symbol:
            # Filter data by FONKODU (symbol)
            filtered_data = data[data['FONKODU'] == symbol]
            if filtered_data.empty:
                return jsonify({"error": f"No data found for symbol: {symbol}"}), 404
            
            # Convert TARIH column to datetime
            filtered_data['TARIH'] = pd.to_datetime(filtered_data['TARIH'], errors='coerce')

            # Drop rows with invalid or missing dates
            filtered_data = filtered_data.dropna(subset=['TARIH'])

            # Get the latest row based on TARIH
            latest_row = filtered_data.sort_values(by='TARIH', ascending=False).iloc[0]

            # Extract the latest FIYAT
            latest_price = latest_row['FIYAT']

            # Return the result as plain text
            return str(latest_price), 200
        
        if symbol_rsi:
            # Filter data by FONKODU (symbol_rsi)
            filtered_data = data[data['FONKODU'] == symbol_rsi]
            if filtered_data.empty:
                return jsonify({"error": f"No data found for symbol_rsi: {symbol_rsi}"}), 404
            
            # Convert TARIH column to datetime
            filtered_data['TARIH'] = pd.to_datetime(filtered_data['TARIH'], errors='coerce')

            # Drop rows with invalid or missing dates
            filtered_data = filtered_data.dropna(subset=['TARIH'])

            # Get the latest row based on TARIH
            latest_row = filtered_data.sort_values(by='TARIH', ascending=False).iloc[0]

            # Extract the latest RSI_14
            latest_rsi = latest_row['RSI_14']

            # Return the result as plain text
            return str(latest_rsi), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)