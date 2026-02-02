import base64

def decode_openlr_base64(encoded_string):
    # Step 1: Base64 decode
    binary_data = base64.b64decode(encoded_string)
    
    # Step 2: Parse binary format
    result = {
        'version': (binary_data[0] >> 5) & 0x07,
        'has_attributes': (binary_data[0] >> 4) & 0x01,
        'area_flag': (binary_data[0] >> 2) & 0x03,
        'point_flag': binary_data[0] & 0x03
    }
    
    # Step 3: Extract coordinates (simplified example)
    # Coordinates are stored as 24-bit signed integers
    offset = 1
    
    # First coordinate
    lon1 = int.from_bytes(binary_data[offset:offset+3], 'big', signed=True)
    lat1 = int.from_bytes(binary_data[offset+3:offset+6], 'big', signed=True)
    
    # Convert to decimal degrees (OpenLR uses deca-micro degrees)
    result['longitude1'] = lon1 / 100000.0
    result['latitude1'] = lat1 / 100000.0
    
    return result

import base64

def encode_openlr_base64(longitude, latitude, frc=0, fow=0, bear=0):
    # Convert decimal degrees to deca-micro degrees
    lon_encoded = int(longitude * 100000)
    lat_encoded = int(latitude * 100000)
    
    # Create header byte
    version = 3  # OpenLR version
    header = (version << 5) | 0x00  # Simplified header
    
    # Pack into bytes
    binary_data = bytearray()
    binary_data.append(header)
    
    # Add longitude (24 bits)
    binary_data.extend(lon_encoded.to_bytes(3, 'big', signed=True))
    
    # Add latitude (24 bits)
    binary_data.extend(lat_encoded.to_bytes(3, 'big', signed=True))
    
    # Add attributes (simplified)
    binary_data.append((frc << 3) | fow)
    binary_data.append(bear)
    
    # Base64 encode
    return base64.b64encode(binary_data).decode('ascii')

decoded=decode_openlr_base64("CCgBEAAkIzPN9w1/OgAJBQQDA60ACgQDA38A/5f/yAAJBQQDAysAMABG")
print(decoded)