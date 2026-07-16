
import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

n_rows = 27500

makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz', 'Audi', 'Lexus', 'Nissan', 'Hyundai', 
         'Kia', 'Volkswagen', 'Subaru', 'Mazda', 'Jeep', 'Tesla', 'Volvo', 'Acura', 'Infiniti', 'GMC',
         'Toyata', 'Hnda', 'BWM', 'Merc', 'Audii', 'Lexs', 'Nisan', 'Hyuandai', 'Kiaa', 'Volkswagon']

models = {
    'Toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Tacoma', '4Runner', 'Prius', 'Sienna', 'Tundra', 'Avalon'],
    'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot', 'Odyssey', 'HR-V', 'Passport', 'Ridgeline', 'Fit', 'Insight'],
    'Ford': ['F-150', 'Escape', 'Explorer', 'Mustang', 'Edge', 'Ranger', 'Bronco', 'Expedition', 'Fusion', 'Focus'],
    'Chevrolet': ['Silverado', 'Equinox', 'Malibu', 'Traverse', 'Tahoe', 'Suburban', 'Camaro', 'Colorado', 'Blazer', 'Trailblazer'],
    'BMW': ['3 Series', '5 Series', 'X3', 'X5', '7 Series', 'X1', 'X7', '4 Series', '2 Series', 'i4'],
    'Mercedes-Benz': ['C-Class', 'E-Class', 'GLC', 'GLE', 'S-Class', 'A-Class', 'GLA', 'GLB', 'CLA', 'G-Class'],
    'Audi': ['A4', 'Q5', 'A6', 'Q7', 'A3', 'Q3', 'A5', 'e-tron', 'Q8', 'A7'],
    'Lexus': ['RX', 'ES', 'NX', 'IS', 'GX', 'LX', 'UX', 'LC', 'RC', 'LS'],
    'Nissan': ['Altima', 'Rogue', 'Sentra', 'Pathfinder', 'Murano', 'Frontier', 'Titan', 'Maxima', 'Armada', 'Kicks'],
    'Hyundai': ['Elantra', 'Tucson', 'Santa Fe', 'Sonata', 'Kona', 'Palisade', 'Venue', 'Ioniq', 'Accent', 'Nexo'],
    'Kia': ['Sorento', 'Sportage', 'Telluride', 'Forte', 'K5', 'Soul', 'Carnival', 'Stinger', 'Niro', 'EV6'],
    'Volkswagen': ['Jetta', 'Tiguan', 'Atlas', 'Passat', 'Golf', 'ID.4', 'Taos', 'Arteon', 'Beetle', 'CC'],
    'Subaru': ['Outback', 'Forester', 'Crosstrek', 'Impreza', 'Legacy', 'Ascent', 'WRX', 'BRZ', 'Solterra', 'XV'],
    'Mazda': ['CX-5', 'Mazda3', 'CX-9', 'CX-30', 'MX-5', 'CX-50', 'Mazda6', 'CX-90', 'RX-8', '2'],
    'Jeep': ['Wrangler', 'Grand Cherokee', 'Cherokee', 'Compass', 'Renegade', 'Gladiator', 'Wagoneer', 'Grand Wagoneer', 'Patriot', 'Liberty'],
    'Tesla': ['Model 3', 'Model Y', 'Model S', 'Model X', 'Cybertruck', 'Roadster'],
    'Volvo': ['XC90', 'XC60', 'XC40', 'S60', 'V60', 'S90', 'V90', 'C40', 'EX90', 'C30'],
    'Acura': ['MDX', 'RDX', 'TLX', 'ILX', 'Integra', 'NSX', 'ZDX', 'RLX', 'TSX', 'RSX'],
    'Infiniti': ['QX60', 'QX50', 'Q50', 'QX80', 'Q60', 'QX30', 'M37', 'G37', 'EX35', 'FX35'],
    'GMC': ['Sierra', 'Acadia', 'Terrain', 'Yukon', 'Canyon', 'Savana', 'Hummer EV', 'Envoy', 'Jimmy', 'Sonoma']
}

fuel_types = ['Gasoline', 'Diesel', 'Hybrid', 'Electric', 'Plug-in Hybrid', 'gasoline', 'diesel', 'HYBRID', 'Elec', 'PHEV', 'Flex Fuel', 'Natural Gas', '']
transmissions = ['Automatic', 'Manual', 'CVT', 'automatic', 'MANUAL', 'Auto', 'DCT', 'Semi-Automatic', '']
body_types = ['Sedan', 'SUV', 'Truck', 'Coupe', 'Hatchback', 'Wagon', 'Convertible', 'Minivan', 'sedan', 'suv', 'TRUCK', 'Cpe', 'Hback', '']
colors = ['Black', 'White', 'Silver', 'Gray', 'Blue', 'Red', 'Green', 'Brown', 'Beige', 'Yellow', 'Orange', 'Purple', 'Gold', 'Maroon', 'Navy', 'Charcoal', 'Pearl White', 'Matte Black', '']
conditions = ['Excellent', 'Good', 'Fair', 'Poor', 'Like New', 'excellent', 'good', 'FAIR', 'Salvage', 'Certified Pre-Owned', 'CPO', '']
title_statuses = ['Clean', 'Salvage', 'Rebuilt', 'Lien', 'Clean Title', 'clean', 'SALVAGE', 'Flood', '']
seller_types = ['Dealer', 'Private', 'dealer', 'PRIVATE', 'Auction', 'Fleet', '']
states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI', 'NJ', 'VA', 'WA', 'AZ', 'MA', 'IN', 'MO', 'TN', 'MD', 'WI']

def random_missing(val, prob=0.08):
    if random.random() < prob:
        return np.nan
    return val

def add_whitespace(val, prob=0.05):
    if random.random() < prob and isinstance(val, str):
        return ' ' + val + '  '
    return val

def random_case_mix(val, prob=0.06):
    if random.random() < prob and isinstance(val, str):
        return ''.join(random.choice([c.upper(), c.lower()]) for c in val)
    return val

def add_typo(val, prob=0.04):
    if random.random() < prob and isinstance(val, str) and len(val) > 3:
        idx = random.randint(0, len(val)-1)
        return val[:idx] + random.choice('abcdefghijklmnopqrstuvwxyz') + val[idx+1:]
    return val

def generate_messy_vin():
    vin = ''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ0123456789', k=17))
    if random.random() < 0.15:
        vin = vin[:random.randint(10, 16)]
    if random.random() < 0.1:
        vin = vin + 'O'
    if random.random() < 0.08:
        vin = vin.lower()
    return vin

def generate_messy_price(base_price):
    r = random.random()
    if r < 0.02:
        return -abs(base_price)
    elif r < 0.04:
        return base_price * 10
    elif r < 0.06:
        return base_price / 10
    elif r < 0.08:
        return f"${base_price:,.2f}"
    elif r < 0.10:
        return np.nan
    return round(base_price + random.gauss(0, base_price * 0.15), 2)

def generate_messy_mileage(base_miles):
    r = random.random()
    if r < 0.03:
        return -base_miles
    elif r < 0.05:
        return base_miles * 100
    elif r < 0.07:
        return f"{base_miles:,} miles"
    elif r < 0.09:
        return base_miles * 1.609
    elif r < 0.11:
        return np.nan
    return int(base_miles + random.gauss(0, base_miles * 0.1))

def generate_messy_year():
    year = random.randint(1995, 2025)
    r = random.random()
    if r < 0.03:
        return str(year)
    elif r < 0.05:
        return year + 100
    elif r < 0.07:
        return year - 80
    elif r < 0.09:
        return np.nan
    return year

def generate_messy_date():
    date = fake.date_between(start_date='-3y', end_date='today')
    r = random.random()
    if r < 0.04:
        return date.strftime('%m/%d/%Y')
    elif r < 0.06:
        return date.strftime('%d-%m-%Y')
    elif r < 0.08:
        return date.strftime('%Y/%m/%d')
    elif r < 0.10:
        return date.strftime('%B %d, %Y')
    elif r < 0.12:
        return str(date)
    elif r < 0.14:
        return np.nan
    return date

def generate_messy_engine():
    r = random.random()
    if r < 0.4:
        return round(random.uniform(1.0, 6.2), 1)
    elif r < 0.6:
        return f"{round(random.uniform(1.0, 6.2), 1)}L"
    elif r < 0.7:
        return f"{random.randint(100, 500)} cu in"
    elif r < 0.8:
        return np.nan
    elif r < 0.9:
        return f"{round(random.uniform(1.0, 6.2), 1)} L"
    return round(random.uniform(1.0, 6.2), 1)

def generate_messy_horsepower():
    hp = random.randint(90, 650)
    r = random.random()
    if r < 0.05:
        return f"{hp} hp"
    elif r < 0.08:
        return hp * 10
    elif r < 0.10:
        return np.nan
    return hp

def generate_messy_boolean(prob_true=0.5):
    val = random.random() < prob_true
    r = random.random()
    if r < 0.15:
        return 'Yes' if val else 'No'
    elif r < 0.25:
        return 'yes' if val else 'no'
    elif r < 0.35:
        return '1' if val else '0'
    elif r < 0.40:
        return 'TRUE' if val else 'FALSE'
    elif r < 0.45:
        return np.nan
    return val

print("Generating messy used car dataset...")

data = []
for i in range(n_rows):
    make = random.choice(makes)
    real_make = make
    if make in ['Toyata', 'Toyota']:
        real_make = 'Toyota'
    elif make in ['Hnda', 'Honda']:
        real_make = 'Honda'
    elif make in ['BWM', 'BMW']:
        real_make = 'BMW'
    elif make in ['Merc', 'Mercedes-Benz']:
        real_make = 'Mercedes-Benz'
    elif make in ['Audii', 'Audi']:
        real_make = 'Audi'
    elif make in ['Lexs', 'Lexus']:
        real_make = 'Lexus'
    elif make in ['Nisan', 'Nissan']:
        real_make = 'Nissan'
    elif make in ['Hyuandai', 'Hyundai']:
        real_make = 'Hyundai'
    elif make in ['Kiaa', 'Kia']:
        real_make = 'Kia'
    elif make in ['Volkswagon', 'Volkswagen']:
        real_make = 'Volkswagen'
    
    model = random.choice(models.get(real_make, ['Unknown']))
    year = generate_messy_year()
    
    age = 2025 - (int(year) if pd.notna(year) and str(year).isdigit() else 10)
    base_price = 35000 - (age * 1200) + random.gauss(0, 3000)
    if real_make in ['BMW', 'Mercedes-Benz', 'Audi', 'Lexus', 'Acura', 'Infiniti']:
        base_price += 15000
    elif real_make in ['Tesla', 'Volvo']:
        base_price += 20000
    
    mileage = max(0, int(age * 12000 + random.gauss(0, 20000)))
    
    row = {
        'car_id': f"CAR-{random.randint(100000, 999999)}" if random.random() > 0.05 else fake.uuid4(),
        'vin': generate_messy_vin(),
        'make': make,
        'model': model,
        'year': year,
        'mileage': generate_messy_mileage(mileage),
        'fuel_type': random.choice(fuel_types),
        'transmission': random.choice(transmissions),
        'engine_size': generate_messy_engine(),
        'horsepower': generate_messy_horsepower(),
        'color': random.choice(colors),
        'body_type': random.choice(body_types),
        'doors': random_missing(random.choice([2, 3, 4, 5, 'two', 'four', '2', '4', ''])),
        'seats': random_missing(random.choice([2, 4, 5, 7, 8, '5', '7', '8 seats', ''])),
        'condition': random.choice(conditions),
        'owners': random_missing(random.choice([1, 2, 3, 4, 5, '1', '2', 'One', 'Two', 'multiple', -1, 15, ''])),
        'accident_history': random.choice(['None', 'Minor', 'Major', 'none', 'MINOR', '1 accident', '2 accidents', 'Unknown', '']),
        'service_history': random.choice(['Full', 'Partial', 'None', 'full', 'PARTIAL', 'Unknown', 'Dealer maintained', '']),
        'warranty_remaining': random_missing(random.choice([0, 6, 12, 24, 36, 48, '3 months', '1 year', '2 years', 'Expired', ''])),
        'title_status': random.choice(title_statuses),
        'registration_state': random.choice(states),
        'city': fake.city(),
        'zip_code': random_missing(fake.zipcode()),
        'listing_date': generate_messy_date(),
        'days_on_market': random_missing(random.randint(0, 180)),
        'seller_type': random.choice(seller_types),
        'has_navigation': generate_messy_boolean(0.6),
        'has_bluetooth': generate_messy_boolean(0.85),
        'has_backup_camera': generate_messy_boolean(0.7),
        'has_sunroof': generate_messy_boolean(0.4),
        'has_leather_seats': generate_messy_boolean(0.5),
        'has_heated_seats': generate_messy_boolean(0.45),
        'listing_price': generate_messy_price(base_price)
    }
    
    for key in ['make', 'model', 'color', 'body_type', 'condition', 'fuel_type', 'transmission']:
        row[key] = add_whitespace(row[key], 0.05)
        row[key] = random_case_mix(row[key], 0.04)
        row[key] = add_typo(row[key], 0.03)
        row[key] = random_missing(row[key], 0.06)
    
    data.append(row)
    
    if (i + 1) % 5000 == 0:
        print(f"Generated {i+1} rows...")

df = pd.DataFrame(data)

# Add explicit duplicates (2% of data)
n_duplicates = int(n_rows * 0.02)
duplicate_indices = np.random.choice(df.index, size=n_duplicates, replace=False)
duplicates = df.loc[duplicate_indices].copy()
df = pd.concat([df, duplicates], ignore_index=True)

# Add near-duplicates (same car, slightly different data) - handle string values safely
n_near = int(n_rows * 0.03)
for _ in range(n_near):
    idx = random.randint(0, len(df)-1)
    row = df.iloc[idx].copy()
    
    # Only modify if numeric
    if pd.notna(row['mileage']) and isinstance(row['mileage'], (int, float)):
        row['mileage'] = int(row['mileage'] + random.randint(-5000, 5000))
    if pd.notna(row['listing_price']) and isinstance(row['listing_price'], (int, float)):
        row['listing_price'] = round(row['listing_price'] * random.uniform(0.9, 1.1), 2)
    
    row['car_id'] = f"CAR-{random.randint(100000, 999999)}"
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

# Shuffle
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nDataset shape: {df.shape}")
print(f"Columns: {len(df.columns)}")
print(f"\nColumn names:\n{list(df.columns)}")
print(f"\nMissing values per column:\n{df.isnull().sum()}")
print(f"\nData types:\n{df.dtypes}")


output_path = "D:\\Data_Science\\ML-Projects\\car_price_prediction\\car_price_prediction\\data\\generated_data.csv"
df.to_csv(output_path, index=False)
print(f"\nGenerated data saved to {output_path}")
print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")