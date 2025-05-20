# Address Calculation Function Documentation

## Overview

The `address_calculation()` function parses different address formats from raw text and splits them into standardized components (name, street, postal code, city, and country). It supports various international address formats including European, US, and UK styles.

Templates using this function: 595, 448, 449, 544
(check PR rule)

## Function Signature

```python
def address_calculation(result_dict, fields=[1, 2, 3, 4]):
```

### Parameters

- `result_dict`: Dictionary containing address data
- `fields`: List of address types to process (default: [1, 2, 3, 4])
  - 1: SELLERADDRTOTAL
  - 2: BUYERADDRTOTAL
  - 3: SHIPTOADDRTOTAL
  - 4: INVOICEEADDRTOTAL

### Return Value

- Updated dictionary with parsed address components

## Key Helper Functions

### `find_country_code()`

Converts country names to standardized country codes using fuzzy matching.

- Handles different languages (English, German)
- Supports directional variants (North, South, East, West)
- Uses similarity threshold for matching
- Returns the ISO country code for the matched country

```python
if BuyerCountry:
    code = find_country_code(BuyerCountry, country_id_mapping_dict)
    if code: BuyerCountry = code
else:
    BuyerCountry = "Germany"
```

> "In the realm of data standardization, addresses are like fingerprints—unique, complex, and telling. The true art lies not in collecting the data, but in understanding the patterns hidden within."

### `is_valid_uk_postal_code()`

Validates if a string matches the UK postal code format:

- Checks if all alphabetic characters are uppercase
- Uses regex pattern to validate format
- Returns boolean indicating validity

```python
def is_valid_uk_postal_code(postcode):
    postcode = postcode.strip()
    
    # Check if all alphabetic characters are uppercase
    for char in postcode:
        if char.isalpha() and not char.isupper():
            return False
    
    pattern = r'^[A-Z]{1,2}[0-9][0-9A-Z]? ?[0-9][A-Z]{2}$'
    return bool(re.match(pattern, postcode))
```

### `split_address()`

The core function that parses an address string into components:

1. Splits the address into lines
2. Handles various address formats:
   - Three-line addresses (Name, Street, City+PostCode+Country)
   - UK-specific formats
   - Multi-line addresses with country on the last line

3. Uses regular expressions to recognize specific patterns:
   - EU prefixed postcodes: `F-39210 DOMBLANS`
   ```python
   match = re.match(r"^([A-Z]{1,3}-)?(\d{3,7})\s+(.+)$", last_line)
   ```
   
   - US ZIP+4 codes: `New York, NY 10118-3299`
   ```python
   match := re.match(r"^(.+?,\s+\w{2})\s+(\d{3,7}-\d{3,7})$", last_line)
   ```
   
   - UK postcodes: `London WC1X 0DW`
   ```python
   match := re.match(r"^(.+)\s+([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})$", last_line)
   ```
   
   - Dutch-style postcodes: `NL-8022 AW Zwolle`
   ```python
   match = re.match(r"^([A-Z]{1,3}-)(\d{4}\s[A-Z]{2})\s+([A-Z][a-zA-Z\s\-']+)$", postcode_city_line)
   ```

4. Returns a list containing:
   - Name
   - Street
   - Postal Code
   - City
   - Country Code

## Main Processing Logic

The function processes each address type specified in the `fields` parameter, extracting structured address components and storing them in the appropriate fields in the result dictionary. The function handles seller, buyer, ship-to, and invoicee addresses based on the input parameters.

For example, to process the shipping address:

```python
# Process SHIPTOADDRTOTAL (field 3)
if 3 in fields and "SHIPTOADDRTOTAL" in result_dict[file] and result_dict[file]["SHIPTOADDRTOTAL"][0] not in [None, "<NO KEY>", '']:
    length = length or len(result_dict[file]["SHIPTOADDRTOTAL"])
    
    # splitting the address
    splitted_addr = split_address(result_dict[file]["SHIPTOADDRTOTAL"][0])
    ship_post_code = splitted_addr[2].split('-')[-1]
    
    # assigning address to respective fields
    result_dict[file]["SHIPTONAME1"] = ShipToName
    result_dict[file]["SHIPTOSTREET1"] = ShipToStreet
    result_dict[file]["SHIPTOPOSTCODE"] = ShipToPostCode
    result_dict[file]["SHIPTOCITY"] = ShipToCity
    result_dict[file]["SHIPTOCOUNTRYID"] = ShipToCountryID
```


## Conclusion

The `address_calculation()` function provides a robust solution for standardizing address data from various international formats. By leveraging pattern recognition through regular expressions, it intelligently parses raw address strings into structured components.

Key benefits of this implementation:
- Supports multiple address formats (European, US, UK, and other international standards)
- Handles language variations in country names
- Maintains data consistency across all address types
- Can selectively process different address categories based on need

