def address_calculation(result_dict_original, address_types=[]):
    import re
    from difflib import SequenceMatcher
    
    result_dict = result_dict_original.copy()

    country_id_mapping_dict = {
    "Belgium": "BE",
    "Belgien": "BE",
    "Serbia": "RS",
    "Serbien": "RS",
    "Luxembourg": "LU",
    "Luxemburg": "LU",
    "USA": "US",
    "Vereinigte Staaten": "US",
    "Deutschland": "DE",
    "Germany": "DE",
    "Malaysia": "MY",
    "Malaysia": "MY",
    "India": "IN",
    "Mexico": "MX",
    "Brazil": "BR",
    "France": "FR",
    "Frankreich": "FR",
    "Netherlands": "NL",
    "Niederlande": "NL",
    "Italy": "IT",
    "Italien": "IT",
    "Spain": "ES",
    "Spanien": "ES",
    "Poland": "PL",
    "Polen": "PL",
    "Czech Republic": "CZ",
    "Tschechien": "CZ",
    "Tschechische Republik": "CZ",
    "Austria": "AT",
    "Österreich": "AT",
    "Switzerland": "CH",
    "Schweiz": "CH",
    "United Kingdom": "GB",
    "Großbritannien": "GB",
    "Vereinigtes Königreich": "GB",
    "China": "CN",
    "Japan": "JP",
    "Russia": "RU",
    "Russland": "RU",
    "Sweden": "SE",
    "Schweden": "SE",
    "Denmark": "DK",
    "Dänemark": "DK",
    "Norway": "NO",
    "Norwegen": "NO",
    "Turkey": "TR",
    "Türkei": "TR",
    "Griechenland": "GR"
    }

    prefix_country_map = {
    "F-": "FRANCE",
    "A-": "AUSTRIA",
    "D-": "GERMANY",
    "B-": "BELGIUM",
    "CH-": "SWITZERLAND",
    "I-": "ITALY",
    "NL-": "NETHERLANDS",
    "PL": "POLAND",
    "BRA": "BRAZIL",
    "MEX": "MEXICO"
    }

    # Country Codes Converter
    def get_sequence_ratio(s1, s2):
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

    def get_best_match(matches, search_term):
        search_term = search_term.lower()
        return max(matches, key=lambda x: max(get_sequence_ratio(search_term, x[0]), get_sequence_ratio(search_term.split()[0], x[0])))

    def find_country_code(search_term, country_dict):
        if not search_term: return []
        search_term = search_term.lower().strip()
        parts = search_term.split()
        is_dir = parts[-1] in {'n', 's', 'e', 'w'} if len(parts) > 1 else False
        dir_map = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
        main, direction = ' '.join(parts[:-1]), dir_map.get(parts[-1], '') if is_dir else ('', '')
        
        matches = []
        for name, code in country_dict.items():
            name_l = name.lower()
            if search_term in name_l or (is_dir and main in name_l and direction in name_l) or (len(search_term) > 3 and get_sequence_ratio(search_term, name_l) > 0.82):
                matches.append((name, code))
        
        return get_best_match(matches, search_term)[1] if matches else None

    def split_address(address):
        lines = address.strip().split("\n")
        Name = Street = PostCode = City = Country = None
        debug_format = -1  # Initialize debug flag with -1 (no match)

        if len(lines) == 3:
            Name = lines[0].strip()
            Street = lines[1].strip()
            postcode_city_line = lines[2].strip()

            # 1. EU prefix at start: F-39210 DOMBLANS
            match = re.match(r"^([A-Z]{1,3}-)?(\d{3,7})\s+(.+)$", postcode_city_line)
            if match:
                prefix = match.group(1) or ""
                PostCode = match.group(2)
                City = match.group(3).title()
                Country = prefix_country_map.get(prefix.upper(), Country)
                debug_format = 0

            # 2. US ZIP+4 at end: New York, NY 10118-3299
            elif match := re.match(r"^(.+?,\s+\w{2})\s+(\d{3,7}-\d{3,7})$", postcode_city_line):
                City = match.group(1)
                PostCode = match.group(2)
                Country = "USA"
                debug_format = 1

            # 3. US ZIP (no dash): Washington, DC 20433
            elif match := re.match(r"^(.+?,\s+\w{2})\s+(\d{3,7})$", postcode_city_line):
                City = match.group(1)
                PostCode = match.group(2)
                Country = "USA"
                debug_format = 2

            # 4. UK postcode at end: London WC1X 0DW
            elif match := re.match(r"^(.+)\s+([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})$", postcode_city_line):
                City = match.group(1)
                PostCode = match.group(2)
                Country = "UNITED KINGDOM"
                debug_format = 3

            # 5. EU-style postcode at end: Kempten Bayern 87435
            elif match := re.match(r"^(.+?)\s+(\d{3,7})$", postcode_city_line):
                City = match.group(1).title()
                PostCode = match.group(2)
                debug_format = 4

            # 6. CZ 16900 Praha 6
            elif match := re.match(r"^(.+?)\s+(\d{3,7})$", postcode_city_line):
                prefix = match.group(1)
                PostCode = match.group(2)
                City = match.group(3)
                Country = prefix_country_map.get(prefix.upper(), Country)
                debug_format = 5

            # 6. City then prefixed postcode at end: DOMBLANS F-39210
            elif match := re.match(r"^(.+)\s+([A-Z]{1,3}-\d{3,7})$", postcode_city_line):
                City = match.group(1).title()
                PostCode = match.group(2).split("-")[1]
                prefix = match.group(2).split("-")[0] + "-"
                Country = prefix_country_map.get(prefix.upper(), Country)
                debug_format = 6
            else:
                City = postcode_city_line
                debug_format = 7    
           
        # New block: Handle cases where the last line contains postcode and city without country on separate line
        # address dont having country in the last line
        elif len(lines) >= 2:
            postcode_city_line = lines[-1].strip()
            # Check if last line matches any of the postcode/city patterns
            
            # 1. EU prefix at start: F-39210 DOMBLANS
            match = re.match(r"^([A-Z]{1,3}-)?(\d{3,7})\s+(.+)$", postcode_city_line)
            if match:
                Street = lines[-2].strip() if len(lines) >= 2 else ""
                Name = "\n".join(lines[:-2]).strip()
                
                prefix = match.group(1) or ""
                PostCode = match.group(2)
                City = match.group(3).title()
                Country = prefix_country_map.get(prefix.upper(), Country)
                debug_format = 8
                
            # 2. US ZIP+4 at end: New York, NY 10118-3299
            elif match := re.match(r"^(.+?,\s+\w{2})\s+(\d{3,7}-\d{3,7})$", postcode_city_line):
                Street = lines[-2].strip() if len(lines) >= 2 else ""
                Name = "\n".join(lines[:-2]).strip()
                
                City = match.group(1)
                PostCode = match.group(2)
                Country = "USA"
                debug_format = 9
                
            # 3. US ZIP (no dash): Washington, DC 20433
            elif match := re.match(r"^(.+?,\s+\w{2})\s+(\d{3,7})$", postcode_city_line): 
                Street = lines[-2].strip() if len(lines) >= 2 else ""
                Name = "\n".join(lines[:-2]).strip()
                
                City = match.group(1)
                PostCode = match.group(2)
                Country = "USA"
                debug_format = 10
                
            # 4. UK postcode at end: London WC1X 0DW
            elif match := re.match(r"^(.+)\s+([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})$", postcode_city_line):
                Street = lines[-2].strip() if len(lines) >= 2 else ""
                Name = "\n".join(lines[:-2]).strip()
                
                City = match.group(1)
                PostCode = match.group(2)
                Country = "UNITED KINGDOM"
                debug_format = 11
                
            # 5. EU-style postcode at end: Kempten Bayern 87435 or Larnaca 6012
            elif match := re.match(r"^(.+?)\s+(\d{3,7})$", postcode_city_line):
                Street = lines[-2].strip() if len(lines) >= 2 else ""
                Name = "\n".join(lines[:-2]).strip()
                
                City = match.group(1).title()
                PostCode = match.group(2)
                debug_format = 12
                
            # 6. City then prefixed postcode at end: DOMBLANS F-39210
            elif match := re.match(r"^(.+)\s+([A-Z]{1,3}-\d{3,7})$", postcode_city_line):
                Street = lines[-2].strip() if len(lines) >= 2 else ""
                Name = "\n".join(lines[:-2]).strip()
                
                City = match.group(1).title()
                PostCode = match.group(2).split("-")[1]
                prefix = match.group(2).split("-")[0] + "-"
                Country = prefix_country_map.get(prefix.upper(), Country)
                debug_format = 13

            # 7. BC V5M 0C4 Vancouver
            elif match := re.match(r"^([A-Z]{2})\s+([A-Z]\d[A-Z]\s+\d[A-Z]\d)\s+(.+)$", postcode_city_line):
                Street = lines[-2].strip() if len(lines) >= 2 else ""
                Name = "\n".join(lines[:-2]).strip()

                Country = match.group(1)  # "BC"
                PostCode = match.group(2)  # "V5M 0C4"
                City = match.group(3)  # "Vancouver"
                debug_format = 14

            # 8. 7051DW Varsseveld
            elif match := re.match(r"^(\d{3,5}[A-Z]{1,3})\s+(.+)$", postcode_city_line):
                City = match.group(2)
                PostCode = match.group(1)
                debug_format = 15

            # 09. East Granby, US-06026 CT
            elif match := re.match(r"^(.+?),\s+(?:([A-Z]{1,3})-)?(\d{3,7}\s+[A-Z]{1,3})$", postcode_city_line):
                City = match.group(1)
                prefix = match.group(2) if match.group(2) and len(match.group(2)) > 1 else None # "US"
                PostCode = match.group(3)  
                Country = prefix_country_map.get(prefix.upper(), Country) 
                debug_format = 16
            
            # 10. 546 42 THESSALONIKI (greece)
            elif match := re.match(r"^(\d{3}\s+\d{2})\s+(.+)$", postcode_city_line):
                City = match.group(2)
                PostCode = match.group(1)
                debug_format = 17

            # 11. 1011 DJ AMSTERDAM (Netherlands)
            elif match := re.match(r"^(\d{4}\s+[A-Z]{2})\s+(.+)$", postcode_city_line):
                City = match.group(2)
                PostCode = match.group(1)
                debug_format = 18

            # 12. Simple: 1040 Brussels
            elif match := re.match(r"^(\d{3,7})\s+(.+)$", postcode_city_line):
                Street = lines[-2].strip() if len(lines) >= 2 else ""
                Name = "\n".join(lines[:-2]).strip()
                
                City = match.group(1).title()
                PostCode = match.group(2)
                # PostCode = match.group(2).split("-")[1] # creating errors
                debug_format = 19   

            # 13. PL 58-500 Jelenia Gora (Poland)
            elif match := re.match(r'^([A-Z]{2})\s+(\d{2}-\d{3})\s+(.+)$', postcode_city_line): 
                prefix = match.group(1)
                PostCode = match.group(2)
                City = match.group(3)
                Country = prefix_country_map.get(prefix.upper(), Country)

                Street = lines[-2].strip() 
                Name = "\n".join(lines[:-2]).strip()
                debug_format = 20

            # 14. BRA 370 Campanario-Diadema (Brazil)
            #     MEX 25300 Saltillo, Coahuilla C.P. (Mexico) 
            elif match := re.match(r'^([A-Z]{2,3})\s+(\d{3,6})\s+(.+)$', postcode_city_line): 
                prefix = match.group(1)
                PostCode = match.group(2)
                City = match.group(3)
                Country = prefix_country_map.get(prefix.upper(), Country)

                Street = lines[-2].strip() 
                Name = "\n".join(lines[:-2]).strip() 
                debug_format = 21

            # address having country in the last line
            elif len(lines) >= 3:
                Country = lines[-1].strip()
                postcode_city_line = lines[-2].strip()
                Street = lines[-3].strip() if len(lines) >= 3 else ""
                Name = "\n".join(lines[:-3]).strip()

                PostCode = ""
                City = ""
                
                # "NL-8022 AW Zwolle"
                match = re.match(r"^([A-Z]{1,3}-)(\d{4}\s[A-Z]{2})\s+([A-Z][a-zA-Z\s\-']+)$", postcode_city_line)
                if match:
                    prefix = match.group(1)
                    PostCode = prefix + match.group(2)         
                    City = match.group(3)   
                    Country = prefix_country_map.get(prefix.upper(), Country) 
                    debug_format = 22
                
                # 1. EU-style: B-1049 Brussels or A-1211 Geneva
                elif match := re.match(r"^([A-Z]{1,3}-)(\d+)\s+(.+)$", postcode_city_line):
                    PostCode = match.group(1) + match.group(2)
                    City = match.group(3)
                    debug_format = 23

                # 2. UK-style: London WC1X 0DW
                elif match := re.match(r"^(.+)\s+([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})$", postcode_city_line):
                    City = match.group(1)
                    PostCode = match.group(2)
                    debug_format = 24

                # 3. US ZIP+4 style: New York, NY 10118-3299
                elif match := re.match(r"^(.+),?\s+\w{2}\s+(\d{3,7}-\d{3,7})$", postcode_city_line):
                    City = match.group(1)
                    PostCode = match.group(2)
                    debug_format = 25

                # 4. US ZIP format: Washington, DC 20433
                elif match := re.match(r"^(.+?,\s+\w{2})\s+(\d{3,7}(?:-\d{3,7})?)$", postcode_city_line):
                    City = match.group(1)
                    PostCode = match.group(2)
                    debug_format = 26

                # 5. US-style without comma: Greensboro NC 27407
                elif match := re.match(r"^(.+?)\s+([A-Z]{2})\s+(\d{3,7})$", postcode_city_line):
                    City = match.group(1) + " " + match.group(2)
                    PostCode = match.group(3)
                    debug_format = 27

                # 6. EU: e.g., Kempten Bayern 87435
                elif match := re.match(r"^(.+?)\s+(\d{3,7})$", postcode_city_line):
                    City = match.group(1)
                    PostCode = match.group(2)
                    debug_format = 28

                # 7. UK-stye: GB-DE12 7DS Measham
                elif match := re.match(r"^([A-Z]{1,3}-)([A-Z]{1,2}\d{1,2}\s*\d[A-Z]{2})\s+(.+)$", postcode_city_line):
                    prefix = match.group(1)
                    PostCode = prefix + match.group(2)  
                    City = match.group(3)
                    Country = prefix_country_map.get(prefix.upper(), Country) 
                    debug_format = 29

                # 8. BC V5M 0C4 Vancouver
                elif match := re.match(r"^([A-Z]{2})\s+([A-Z]\d[A-Z]\s+\d[A-Z]\d)\s+(.+)$", postcode_city_line):
                    Street = lines[-2].strip() if len(lines) >= 2 else ""
                    Name = "\n".join(lines[:-2]).strip()

                    Country = match.group(1)  
                    PostCode = match.group(2) 
                    City = match.group(3)     
                    debug_format = 30

                #  9. 7051DW Varsseveld
                elif match := re.match(r"^(\d{3,5}[A-Z]{1,3})\s+(.+)$", postcode_city_line):
                    City = match.group(2)
                    PostCode = match.group(1)
                    debug_format = 31

                # 10. 546 42 THESSALONIKI (greece)
                elif match := re.match(r"^(\d{3}\s+\d{2})\s+(.+)$", postcode_city_line):
                    City = match.group(2)
                    PostCode = match.group(1)
                    debug_format = 32

                # 11. 1011 DJ AMSTERDAM (Netherlands)
                elif match := re.match(r"^(\d{4}\s+[A-Z]{2})\s+(.+)$", postcode_city_line):
                    City = match.group(2)
                    PostCode = match.group(1)
                    debug_format = 33

                # 12. East Granby, US-06026 CT
                elif match := re.match(r"^(.+?),\s+(?:([A-Z]{1,3})-)?(\d{3,7}\s+[A-Z]{1,3})$", postcode_city_line):
                    City = match.group(1)
                    prefix = match.group(2) if match.group(2) and len(match.group(2)) > 1 else None # "US"
                    PostCode = match.group(3)  
                    Country = prefix_country_map.get(prefix.upper(), Country) 
                    debug_format = 34

                # ------------------------------
                # MATCHING UK POSTCODE FORMATS
                # ------------------------------

                # 13. AN NAA (e.g., M1 1AA)
                elif match := re.match(r'^[A-Z]{1}[0-9]{1}\s?[0-9]{1}[A-Z]{2}$', postcode_city_line):
                    Name = "\n".join(lines[:-4]).strip()
                    Street = lines[-4].strip()
                    City = lines[-3].strip()
                    PostCode = lines[-2].strip()
                    Country = lines[-1].strip()
                    debug_format = 35

                # 14. ANN NAA (e.g., M60 1NW)
                elif match := re.match(r'^[A-Z]{1}[0-9]{2}\s?[0-9]{1}[A-Z]{2}$', postcode_city_line):
                    Name = "\n".join(lines[:-4]).strip()
                    Street = lines[-4].strip()
                    City = lines[-3].strip()
                    PostCode = lines[-2].strip()
                    Country = lines[-1].strip()
                    debug_format = 36

                # 15. AAN NAA (e.g., CR2 6XH)
                elif match := re.match(r'^[A-Z]{2}[0-9]{1}\s?[0-9]{1}[A-Z]{2}$', postcode_city_line):
                    Name = "\n".join(lines[:-4]).strip()
                    Street = lines[-4].strip()
                    City = lines[-3].strip()
                    PostCode = lines[-2].strip()
                    Country = lines[-1].strip()
                    debug_format = 37

                # 16. AANN NAA (e.g., DN55 1PT)
                elif match := re.match(r'^[A-Z]{2}[0-9]{2}\s?[0-9]{1}[A-Z]{2}$', postcode_city_line):
                    Name = "\n".join(lines[:-4]).strip()
                    Street = lines[-4].strip()
                    City = lines[-3].strip()
                    PostCode = lines[-2].strip()
                    Country = lines[-1].strip()
                    debug_format = 38

                # 17. ANA NAA (e.g., W1A 1HQ)
                elif match := re.match(r'^[A-Z]{1}[0-9]{1}[A-Z]{1}\s?[0-9]{1}[A-Z]{2}$', postcode_city_line):
                    Name = "\n".join(lines[:-4]).strip()
                    Street = lines[-4].strip()
                    City = lines[-3].strip()
                    PostCode = lines[-2].strip()
                    Country = lines[-1].strip()
                    debug_format = 39

                # 18. AANA NAA (e.g., EC1A 1BB)
                elif match := re.match(r'^[A-Z]{2}[0-9]{1}[A-Z]{1}\s?[0-9]{1}[A-Z]{2}$', postcode_city_line):
                    Name = "\n".join(lines[:-4]).strip()
                    Street = lines[-4].strip()
                    City = lines[-3].strip()
                    PostCode = lines[-2].strip()
                    Country = lines[-1].strip()
                    debug_format = 40

                # --------------------------------------------------------

                # 19. PL 58-500 Jelenia Gora (Poland)
                elif match := re.match(r'^([A-Z]{2})\s+(\d{2}-\d{3})\s+(.+)$', postcode_city_line): 
                    prefix = match.group(1)
                    PostCode = match.group(2)
                    City = match.group(3)
                    Country = prefix_country_map.get(prefix.upper(), Country)

                    Street = lines[-2].strip() 
                    Name = "\n".join(lines[:-2]).strip() 
                    debug_format = 41

                # 20. BRA 370 Campanario-Diadema (Brazil)
                #     MEX 25300 Saltillo, Coahuilla C.P. (Mexico) 
                elif match := re.match(r'^([A-Z]{2,3})\s+(\d{3,6})\s+(.+)$', postcode_city_line): 
                    prefix = match.group(1)
                    PostCode = match.group(2)
                    City = match.group(3)
                    Country = prefix_country_map.get(prefix.upper(), Country)

                    Street = lines[-2].strip() 
                    Name = "\n".join(lines[:-2]).strip()
                    debug_format = 42

                # Simple: 1040 Brussels
                elif match := re.match(r"^(\d{3,7})\s+(.+)$", postcode_city_line):
                    PostCode = match.group(1)
                    City = match.group(2)
                    debug_format = 43
                else:
                    City = postcode_city_line
                    debug_format = 44
        
        if Country:
            code = find_country_code(Country, country_id_mapping_dict)
            if code: Country = code
        else:
            Country = "DE" # Germany
        
        if PostCode:
            if "-" in PostCode:
                PostCode = PostCode.split("-")[1]

        return [Name, Street, PostCode, City, Country, debug_format]

    # Process address fields based on address types
    supported_address_types = ['SELLER', 'BUYER', 'SHIPTO', 'INVOICEE']
    
    for file in result_dict:
        # Process each address type
        for addr_type in address_types:
            addr_total_key = f"{addr_type}ADDRTOTAL"
            
            # If addr_type not present in the supported_address_types, then ignore and dont process
            if addr_type not in supported_address_types:
                continue

            # Skip if the key doesn't exist or value is empty
            if addr_total_key not in result_dict[file] or result_dict[file][addr_total_key][0] in [None, "<NO KEY>", '']:
                continue
                
            # Get the length of this field's data
            length = len(result_dict[file][addr_total_key])
            
            # splitting the address
            splitted_addr = split_address(result_dict[file][addr_total_key][0])
            name, street, postcode, city, countryid = splitted_addr[0:5]

            # Handle special case, if postcode has any hypen(-)
            # for eg, "FR-40021"
            # But normally, it shouldn't be used as there are many countries using hypen(-) 
            # in their postcode, like Japan, Poland, etc hence commented
            # if addr_type in ['SHIPTO', 'INVOICEE']:
            #     postcode = splitted_addr[2].split('-')[-1]
            
            # Prepare field keys
            name_key = f"{addr_type}NAME1"
            street_key = f"{addr_type}STREET1"
            postcode_key = f"{addr_type}POSTCODE"
            city_key = f"{addr_type}CITY"
            country_key = f"{addr_type}COUNTRYID"
            
            # Assign values to respective fields
            result_dict[file][name_key] = length * [name]
            result_dict[file][street_key] = length * [street]
            result_dict[file][postcode_key] = length * [postcode]
            result_dict[file][city_key] = length * [city]
            result_dict[file][country_key] = length * [countryid]
            
            # Debug Regex Format(which format (regular expression) has been selected from this specific address)
            # In case, you to debug, uncomment the below 2 lines
            # debug_format = splitted_addr[5]
            # print(debug_format)

            # Clear the ADDRTOTAL field, if all the individuals fields have content
            # if all the individual fields, dont have content, this means:
            # there is address issue in the document or some error in address calculation
            # in that case we would not clear address total field for debugging purpose
            if name and street and postcode and city and countryid:
                result_dict[file][addr_total_key] = length * [None]
    
    return result_dict

