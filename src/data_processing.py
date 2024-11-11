import pandas as pd
import json
import logging
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_data(csv_path):
    """
    Main function for data preprocessing
    """
    try:
        # Load raw data
        logger.info(f"Loading data from: {csv_path}")
        df_original = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df_original)} rows")

        # Handle dates first
        df_original['createdAt'] = pd.to_datetime(df_original['createdAt'].astype(str), format='mixed', errors='coerce')
        
        # Parse JSON data
        parsed_data = []
        for _, row in df_original.iterrows():
            try:
                json_data = json.loads(row['file'])
                if 'User' in json_data:
                    user_info = json_data['User']
                    # Add original fields
                    user_info['original_id'] = row['id']
                    user_info['original_userId'] = row['userId']
                    user_info['createdAt'] = row['createdAt']
                    parsed_data.append(user_info)
            except Exception as e:
                logger.warning(f"Error processing row {row['id']}: {str(e)}")
                continue

        if not parsed_data:
            logger.error("No data was successfully parsed")
            return None

        # Convert to DataFrame
        df_parsed = pd.DataFrame(parsed_data)
        logger.info(f"Successfully parsed {len(df_parsed)} rows")

        # Clean city data
        def clean_city(city_info):
            if pd.isna(city_info):
                return "Not Specified"
            if isinstance(city_info, dict) and 'name' in city_info:
                return city_info['name']
            if isinstance(city_info, str):
                return city_info.split(',')[0].strip()
            return "Not Specified"

        df_parsed['city_clean'] = df_parsed['city'].apply(clean_city)

        # Ensure basic fields exist
        required_fields = ['bio', 'gender', 'city_clean', 'original_id', 'original_userId']
        for field in required_fields:
            if field not in df_parsed.columns:
                df_parsed[field] = None

        logger.info("Data preprocessing completed successfully")
        return df_parsed

    except Exception as e:
        logger.error(f"Error in preprocessing: {str(e)}")
        logger.error(f"Error details: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame instead of None

# Utility functions
def parse_json_safely(json_str):
    try:
        return json.loads(json_str)
    except:
        return None

def extract_user_interests(interests_data):
    if pd.isna(interests_data):
        return []
    try:
        if isinstance(interests_data, list):
            return [interest['name'] for interest in interests_data if 'name' in interest]
        return []
    except:
        return []