import json
import math
import pandas as pd

# 1. Define VDCs (Factories/Origins)
vdcs = {
    'LA': {
        'name': 'Long Beach VDC',
        'city': 'Long Beach, CA',
        'lat': 33.7701,
        'lon': -118.1937,
        'open_time': 360,  # 06:00
        'close_time': 1320, # 22:00
    },
    'SF': {
        'name': 'Benicia VDC',
        'city': 'Benicia, CA',
        'lat': 38.0494,
        'lon': -122.1586,
        'open_time': 360,
        'close_time': 1320,
    },
    'ML': {
        'name': 'Mira Loma VDC',
        'city': 'Mira Loma, CA',
        'lat': 33.9892,
        'lon': -117.5156,
        'open_time': 360,
        'close_time': 1320,
    },
    'PT': {
        'name': 'Portland VDC',
        'city': 'Portland, OR',
        'lat': 45.5152,
        'lon': -122.6784,
        'open_time': 360,
        'close_time': 1320,
    },
    'SK': {
        'name': 'Orillia VDC',
        'city': 'Orillia, ON / Hub',
        'lat': 44.6082,
        'lon': -79.4182,
        'open_time': 360,
        'close_time': 1320,
    },
    '04016': {
        'name': 'Omesa Logistics Hub',
        'city': 'Ontario / Mesa Hub',
        'lat': 34.0633,
        'lon': -117.6509,
        'open_time': 360,
        'close_time': 1320,
    }
}

# 2. Define Dealerships (Delivery Centres D) for each VDC network
dealers_data = [
    # LA (Long Beach) Network - Mix of local and regional/long-haul
    {'dealer_id': 'D_LA_01', 'name': 'Toyota of Anaheim', 'vdc_served': 'LA', 'city': 'Anaheim, CA', 'lat': 33.8366, 'lon': -117.9143, 'service_time_mins': 35, 'earliest_arrival': 420, 'latest_arrival': 1140, 'is_handover_allowed': 1},
    {'dealer_id': 'D_LA_02', 'name': 'Lexus of Glendale', 'vdc_served': 'LA', 'city': 'Glendale, CA', 'lat': 34.1425, 'lon': -118.2551, 'service_time_mins': 40, 'earliest_arrival': 480, 'latest_arrival': 1080, 'is_handover_allowed': 1},
    {'dealer_id': 'D_LA_03', 'name': 'Toyota of San Diego', 'vdc_served': 'LA', 'city': 'San Diego, CA', 'lat': 32.8126, 'lon': -117.1517, 'service_time_mins': 45, 'earliest_arrival': 420, 'latest_arrival': 1200, 'is_handover_allowed': 1},
    {'dealer_id': 'D_LA_04', 'name': 'Toyota of Bakersfield (Long-Haul)', 'vdc_served': 'LA', 'city': 'Bakersfield, CA', 'lat': 35.3733, 'lon': -119.0187, 'service_time_mins': 50, 'earliest_arrival': 540, 'latest_arrival': 1260, 'is_handover_allowed': 1},
    {'dealer_id': 'D_LA_05', 'name': 'Fresno Lexus Hub (Extended Long-Haul)', 'vdc_served': 'LA', 'city': 'Fresno, CA', 'lat': 36.7468, 'lon': -119.7726, 'service_time_mins': 45, 'earliest_arrival': 600, 'latest_arrival': 1320, 'is_handover_allowed': 1},
    {'dealer_id': 'D_LA_06', 'name': 'Toyota of Riverside', 'vdc_served': 'LA', 'city': 'Riverside, CA', 'lat': 33.9533, 'lon': -117.3962, 'service_time_mins': 35, 'earliest_arrival': 420, 'latest_arrival': 1140, 'is_handover_allowed': 0},

    # SF (Benicia) Network
    {'dealer_id': 'D_SF_01', 'name': 'Stevens Creek Toyota', 'vdc_served': 'SF', 'city': 'San Jose, CA', 'lat': 37.3230, 'lon': -121.9863, 'service_time_mins': 45, 'earliest_arrival': 450, 'latest_arrival': 1140, 'is_handover_allowed': 1},
    {'dealer_id': 'D_SF_02', 'name': 'Toyota of Walnut Creek', 'vdc_served': 'SF', 'city': 'Walnut Creek, CA', 'lat': 37.9101, 'lon': -122.0652, 'service_time_mins': 35, 'earliest_arrival': 420, 'latest_arrival': 1080, 'is_handover_allowed': 1},
    {'dealer_id': 'D_SF_03', 'name': 'Sacramento Toyota Hub', 'vdc_served': 'SF', 'city': 'Sacramento, CA', 'lat': 38.5816, 'lon': -121.4944, 'service_time_mins': 40, 'earliest_arrival': 480, 'latest_arrival': 1200, 'is_handover_allowed': 1},
    {'dealer_id': 'D_SF_04', 'name': 'Reno Lexus Superstore (Long-Haul)', 'vdc_served': 'SF', 'city': 'Reno, NV', 'lat': 39.5296, 'lon': -119.8138, 'service_time_mins': 50, 'earliest_arrival': 540, 'latest_arrival': 1320, 'is_handover_allowed': 1},

    # ML (Mira Loma) Network
    {'dealer_id': 'D_ML_01', 'name': 'Crown Toyota Ontario', 'vdc_served': 'ML', 'city': 'Ontario, CA', 'lat': 34.0689, 'lon': -117.5645, 'service_time_mins': 30, 'earliest_arrival': 420, 'latest_arrival': 1100, 'is_handover_allowed': 1},
    {'dealer_id': 'D_ML_02', 'name': 'Toyota of San Bernardino', 'vdc_served': 'ML', 'city': 'San Bernardino, CA', 'lat': 34.1083, 'lon': -117.2898, 'service_time_mins': 35, 'earliest_arrival': 450, 'latest_arrival': 1140, 'is_handover_allowed': 1},
    {'dealer_id': 'D_ML_03', 'name': 'Palm Springs Lexus', 'vdc_served': 'ML', 'city': 'Cathedral City, CA', 'lat': 33.7797, 'lon': -116.4653, 'service_time_mins': 40, 'earliest_arrival': 480, 'latest_arrival': 1200, 'is_handover_allowed': 1},
    {'dealer_id': 'D_ML_04', 'name': 'Las Vegas Toyota Hub (Long-Haul)', 'vdc_served': 'ML', 'city': 'Las Vegas, NV', 'lat': 36.1699, 'lon': -115.1398, 'service_time_mins': 55, 'earliest_arrival': 600, 'latest_arrival': 1380, 'is_handover_allowed': 1},

    # PT (Portland) Network
    {'dealer_id': 'D_PT_01', 'name': 'Beaverton Toyota', 'vdc_served': 'PT', 'city': 'Beaverton, OR', 'lat': 45.4871, 'lon': -122.8037, 'service_time_mins': 35, 'earliest_arrival': 450, 'latest_arrival': 1140, 'is_handover_allowed': 1},
    {'dealer_id': 'D_PT_02', 'name': 'Gresham Toyota', 'vdc_served': 'PT', 'city': 'Gresham, OR', 'lat': 45.4998, 'lon': -122.4312, 'service_time_mins': 35, 'earliest_arrival': 420, 'latest_arrival': 1100, 'is_handover_allowed': 1},
    {'dealer_id': 'D_PT_03', 'name': 'Toyota of Olympia', 'vdc_served': 'PT', 'city': 'Tumwater, WA', 'lat': 46.9942, 'lon': -122.9056, 'service_time_mins': 40, 'earliest_arrival': 480, 'latest_arrival': 1200, 'is_handover_allowed': 1},
    {'dealer_id': 'D_PT_04', 'name': 'Seattle Toyota Metro (Long-Haul)', 'vdc_served': 'PT', 'city': 'Seattle, WA', 'lat': 47.6062, 'lon': -122.3321, 'service_time_mins': 50, 'earliest_arrival': 540, 'latest_arrival': 1300, 'is_handover_allowed': 1},
    {'dealer_id': 'D_PT_05', 'name': 'Spokane Lexus Regional Hub', 'vdc_served': 'PT', 'city': 'Spokane, WA', 'lat': 47.6588, 'lon': -117.4260, 'service_time_mins': 60, 'earliest_arrival': 660, 'latest_arrival': 1400, 'is_handover_allowed': 1},

    # SK / 04016 Network
    {'dealer_id': 'D_SK_01', 'name': 'Barrie Toyota Centre', 'vdc_served': 'SK', 'city': 'Barrie, ON', 'lat': 44.3894, 'lon': -79.6903, 'service_time_mins': 35, 'earliest_arrival': 420, 'latest_arrival': 1140, 'is_handover_allowed': 1},
    {'dealer_id': 'D_SK_02', 'name': 'Newmarket Lexus', 'vdc_served': 'SK', 'city': 'Newmarket, ON', 'lat': 44.0592, 'lon': -79.4613, 'service_time_mins': 40, 'earliest_arrival': 450, 'latest_arrival': 1140, 'is_handover_allowed': 1},
    {'dealer_id': 'D_OM_01', 'name': 'Mesa Gateway Toyota', 'vdc_served': '04016', 'city': 'Mesa, AZ', 'lat': 33.4152, 'lon': -111.8315, 'service_time_mins': 35, 'earliest_arrival': 420, 'latest_arrival': 1140, 'is_handover_allowed': 1},
    {'dealer_id': 'D_OM_02', 'name': 'Scottsdale Lexus Hub', 'vdc_served': '04016', 'city': 'Scottsdale, AZ', 'lat': 33.4942, 'lon': -111.9261, 'service_time_mins': 40, 'earliest_arrival': 450, 'latest_arrival': 1140, 'is_handover_allowed': 1},
]

df_dealers = pd.DataFrame(dealers_data)
df_dealers.to_csv('data/dealers.csv', index=False)
print(f"Generated {len(df_dealers)} dealers in data/dealers.csv")

# 3. Define Drivers Pool
drivers_data = [
    {'driver_id': 'DRV_01', 'name': 'Vijay Anna', 'home_vdc': 'LA', 'duty_limit_mins': 660, 'shift_start': 360, 'shift_end': 1380, 'cost_per_hr': 35.0, 'certified_haulers': 'all', 'is_available': True},
    {'driver_id': 'DRV_02', 'name': 'LB746 (Carlos M.)', 'home_vdc': 'LA', 'duty_limit_mins': 660, 'shift_start': 360, 'shift_end': 1380, 'cost_per_hr': 32.0, 'certified_haulers': 'all', 'is_available': True},
    {'driver_id': 'DRV_03', 'name': 'BE14 (David K.)', 'home_vdc': 'SF', 'duty_limit_mins': 660, 'shift_start': 360, 'shift_end': 1380, 'cost_per_hr': 34.0, 'certified_haulers': 'all', 'is_available': True},
    {'driver_id': 'DRV_04', 'name': 'BE25 (Sarah T.)', 'home_vdc': 'SF', 'duty_limit_mins': 660, 'shift_start': 360, 'shift_end': 1380, 'cost_per_hr': 35.0, 'certified_haulers': 'all', 'is_available': True},
    {'driver_id': 'DRV_05', 'name': 'LB764 (Robert R.)', 'home_vdc': 'LA', 'duty_limit_mins': 660, 'shift_start': 420, 'shift_end': 1440, 'cost_per_hr': 33.0, 'certified_haulers': 'all', 'is_available': True},
    {'driver_id': 'DRV_06', 'name': 'Srikanth Al', 'home_vdc': 'PT', 'duty_limit_mins': 660, 'shift_start': 360, 'shift_end': 1380, 'cost_per_hr': 36.0, 'certified_haulers': 'all', 'is_available': True},
    {'driver_id': 'DRV_07', 'name': 'Ravi Sushil', 'home_vdc': 'ML', 'duty_limit_mins': 660, 'shift_start': 360, 'shift_end': 1380, 'cost_per_hr': 33.0, 'certified_haulers': 'all', 'is_available': True},
    {'driver_id': 'DRV_08', 'name': 'Relief Driver West (Relief 1)', 'home_vdc': 'LA', 'duty_limit_mins': 660, 'shift_start': 480, 'shift_end': 1440, 'cost_per_hr': 38.0, 'certified_haulers': 'all', 'is_available': True},
    {'driver_id': 'DRV_09', 'name': 'Relief Driver North (Relief 2)', 'home_vdc': 'PT', 'duty_limit_mins': 660, 'shift_start': 480, 'shift_end': 1440, 'cost_per_hr': 38.0, 'certified_haulers': 'all', 'is_available': True},
]

df_drivers = pd.DataFrame(drivers_data)
df_drivers.to_csv('data/drivers.csv', index=False)
print(f"Generated {len(df_drivers)} drivers in data/drivers.csv")

# 4. Generate Distance & Travel Time Matrix between VDCs and Dealers
def haversine_dist_miles(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Build all locations dictionary
all_locs = {}
for vdc_id, vdc_info in vdcs.items():
    all_locs[vdc_id] = {'name': vdc_info['name'], 'lat': vdc_info['lat'], 'lon': vdc_info['lon'], 'is_vdc': True}

for d in dealers_data:
    all_locs[d['dealer_id']] = {'name': d['name'], 'lat': d['lat'], 'lon': d['lon'], 'is_vdc': False, 'vdc_served': d['vdc_served']}

dist_matrix = {}
time_matrix = {}

# Road winding factor: 1.25x haversine distance
# Average commercial car hauler speed: 50 mph (highway + city mix)
avg_speed_mph = 50.0

for loc1, info1 in all_locs.items():
    dist_matrix[loc1] = {}
    time_matrix[loc1] = {}
    for loc2, info2 in all_locs.items():
        if loc1 == loc2:
            dist_matrix[loc1][loc2] = 0.0
            time_matrix[loc1][loc2] = 0
        else:
            raw_dist = haversine_dist_miles(info1['lat'], info1['lon'], info2['lat'], info2['lon'])
            road_dist = round(raw_dist * 1.28, 1)
            # Travel time in minutes
            travel_mins = int(round((road_dist / avg_speed_mph) * 60))
            dist_matrix[loc1][loc2] = road_dist
            time_matrix[loc1][loc2] = travel_mins

dist_payload = {
    'locations': all_locs,
    'distances_miles': dist_matrix,
    'travel_time_minutes': time_matrix
}

with open('data/distances.json', 'w') as f:
    json.dump(dist_payload, f, indent=2)
print("Generated data/distances.json")

# 5. Generate load manifests (connecting load_ID to vehicles and destination dealers)
df_loads = pd.read_csv('data/loads_tbl.csv')
df_models = pd.read_csv('data/model_details.csv')
df_hauler_cfg = pd.read_csv('data/hauler_config.csv')

load_details_rows = []

for idx, load_row in df_loads.iterrows():
    load_id = int(load_row['id'])
    vdc = str(load_row['origin_legal_entity']).strip()
    hauler_id = load_row['assigned_hauler_id']
    
    # Capacity lookup
    cap = 9
    if pd.notna(hauler_id):
        matching_h = df_hauler_cfg[df_hauler_cfg['id'] == int(hauler_id)]
        if not matching_h.empty and pd.notna(matching_h.iloc[0]['capacity']):
            cap = int(matching_h.iloc[0]['capacity'])
    
    # Select 2 to 3 target dealers in that VDC's network
    candidate_dealers = [d for d in dealers_data if d['vdc_served'] == vdc]
    if not candidate_dealers:
        candidate_dealers = [d for d in dealers_data if d['vdc_served'] == 'LA']
    
    # For load_id % 4 == 0 or specific long-haul loads, include long-haul dealers to test 11h rule
    if load_id in [244606, 245724, 245356, 227478]:
        # Long haul combination to clearly demonstrate 11-hour driver limit & handover
        if vdc == 'LA':
            chosen_dealers = [d['dealer_id'] for d in candidate_dealers if d['dealer_id'] in ['D_LA_01', 'D_LA_05']]
        elif vdc == 'SF':
            chosen_dealers = [d['dealer_id'] for d in candidate_dealers if d['dealer_id'] in ['D_SF_02', 'D_SF_04']]
        elif vdc == 'PT':
            chosen_dealers = [d['dealer_id'] for d in candidate_dealers if d['dealer_id'] in ['D_PT_01', 'D_PT_05']]
        else:
            chosen_dealers = [d['dealer_id'] for d in candidate_dealers[:2]]
    else:
        # Standard local/regional deliveries (1-2 dealers, < 11h)
        chosen_dealers = [d['dealer_id'] for d in candidate_dealers[:2]]
    
    # Distribute vehicles among chosen dealers
    total_vehicles = min(cap, 8)
    for v_idx in range(total_vehicles):
        model_row = df_models.iloc[v_idx % len(df_models)]
        assigned_dealer = chosen_dealers[v_idx % len(chosen_dealers)]
        vin = f"4T1B{vdc}{load_id % 1000:03d}{v_idx:04d}"
        load_details_rows.append({
            'load_id': load_id,
            'vin': vin,
            'model_id': model_row['id'],
            'model_name': model_row['description'],
            'brand': model_row['brand'],
            'series': model_row['series'],
            'weight_kg': model_row['weight'],
            'length_m': model_row['length'],
            'width_m': model_row['width'],
            'height_m': model_row['height'],
            'destination_dealer_id': assigned_dealer
        })

df_load_details = pd.DataFrame(load_details_rows)
df_load_details.to_csv('data/load_details.csv', index=False)
print(f"Generated {len(df_load_details)} load vehicle items in data/load_details.csv")
