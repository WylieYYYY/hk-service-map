#!/usr/bin/env python3
import contextlib
import datetime
import grequests
import json
import os
import random
import re
import requests
import sys
import time
import urllib.parse
import xml.etree.ElementTree
import xmljson

# handle request to the XML service, parse and dump
def request_service_xml(xml_url):
	response = requests.get(xml_url)
	if not response:
		print(f'XML request for "{xml_url}" HTTP error')
		sys.exit()
	return xml.etree.ElementTree.fromstring(response.text)

# create or read address override table
def get_override_table(xml_url):
	table = {}
	if not os.path.exists('override.csv'):
		print('Creating address override table')
		# UTF8 BOM for Excel
		with open('override.csv', 'w', encoding='utf-8-sig') as f:
			f.write('See README for usage\n[Traditional Chinese Name]\t[Proposed Address]'
				'\t[Longtitude Offset]\t[Latitude Offset]\t[Registered Address]\nxml_url\t' + xml_url)
	else:
		print('Reading address override table')
		with open('override.csv', 'r', encoding='utf-8-sig') as f:
			for line in f:
				fields = line.split('\t')
				if fields[0] == 'xml_url' and xml_url == '':
					xml_url = fields[1].rstrip()
				# ignore any entry key with lowercase character
				if any(char.islower() for char in fields[0]):
					continue
				table[fields[0]] = '\t'.join(map(lambda field: field.strip(), fields[1:]))
	return [xml_url, table]

# take in XML root with specific tags and parse address
def parse_address(root, xmlns_url, override_table):
	xmlns = {'xmlns': xmlns_url}
	parsed_index, parsed_address = ([] for i in range(2))
	unparsed_count = 0
	for unit_index, unit in enumerate(root.iter(f'{{{xmlns_url}}}serviceUnit')):
		location = unit.find('xmlns:addressEnglish', xmlns).text.upper()
		# replace plate number list and stray double quote
		location = re.sub(r'([0-9]+[A-Z]{0,2}, )(?=[0-9]+[A-Z]{0,2})', '', location)
		location = location.replace('"', '');
		# remove LOT and DD, use ALSO KNOWN AS tag to avoid
		location = re.sub(r'LOTS? .* IN D\.?D\.? ?[0-9]+', '', location)
		location = re.sub(r'D\.?D\.? [0-9]+ LOT [0-9]+', '', location)
		alternative = re.search(r'(\(ALSO KNOWN AS )([^\)]*)(\)$)', location)
		if alternative:
			location = alternative.group(2)
		# remove bracket from address and split into fields
		bracket_regex = r'(\uFF08|\().*(\uFF09|\))'
		location = re.sub(bracket_regex, '', location)
		fields = location.split(',')
		# strip trailig or leading space by comma
		fields[:] = [field.strip() for field in fields]
		# reset flags detail decides if the scope is large enough
		detail = True
		# when to start keeping for correct scope
		trim_index = 0
		# the scope maybe large enough, but keep searching
		weak_large = False
		override_f = open('override.csv', 'a', encoding='utf-8-sig')
		for index in range(len(fields)):
			# remove additional number
			strip_num_regex = r'([A-Z]{0,2}[0-9]+[A-Z]{0,2}(/F)? ?AND ?)(?=[A-Z]{0,2}[0-9]+[A-Z]{0,2}(/F)?)'
			for symbol in ['AND', '-', '&']:
				fields[index] = re.sub(strip_num_regex.replace('AND', symbol), '', fields[index])
			# large enough scope, accept all
			if not detail:
				continue
			# do not attemp to parse address with lot number
			if re.search(r'(( |^)LOT ?[0-9]+|( |^)D\.?D\.? ?[0-9]+)', fields[index]):
				break
			# remove all floor number but keep house info
			while re.search(r'(G|[0-9])\/F', fields[index], re.I):
				replaced = re.subn(r'(.*(G|[0-9])\/F (OF ?)?)(?=\S+)', '', fields[index])
				if replaced[1]:
					fields[index] = replaced[0].strip()
					trim_index = index
					# the info following may not be useful
					weak_large = True
				else:
					trim_index = index + 1
					break
			# house number and street regex
			num_regex = r'^(.* )?(NOS?\.? ?)?[0-9]+[A-Z]{0,2}'
			rural_road = r'|KAM TIN SHI|SHEUNG LING PEI|SHEUNG WO CHE'
			road_regex = (r'.*(AVENUE|CIRCUIT|COURT|CRESCENT|DRIVE|LANE|LAU'
				r'|PATH|ROAD|RD|STREET|TERRACE|TSUEN|VILLA(GE)?' + rural_road + r')')
			strip_num_regex = r'^.*[^0-9]+(?=[0-9]+)'
			# house number is put alongside street name
			if re.search(num_regex + road_regex, fields[index], re.I):
				fields[index] = re.sub(strip_num_regex, '', fields[index])
				trim_index = index
				detail = False
				continue
			# house number in the field before street name
			if (re.search(num_regex + r'$', fields[index]) and len(fields) != index + 1
				and re.search(road_regex, fields[index + 1])):
				re.sub(strip_num_regex, '', fields[index])
				# it will be picked up in the next loop
				fields[index + 1] = fields[index] + ' ' + fields[index + 1]
			# check building name
			rural_unit = r'|PAK SHE'
			if re.search(r'(BLOCK|BUILDING|CENT(ER|RE)|CHUEN|COURT|DAI HA|ESTATE|HOUSE|MALL|MANSION|TSUEN' +
				rural_unit + r')$', fields[index]):
				# strip unclean floor name
				fields[index] = re.sub(r'.* OF ', '', fields[index])
				# strip flat number
				fields[index] = re.sub(r'[^0-9]*[0-9]+ ', '', fields[index])
				trim_index = index
				detail = False
				continue
			# strip unclean unit name
			fields[index] = re.sub(r'(.* AT )(?=.*)', '', fields[index])
		# scope not large enough, address is unparsed
		if detail and not weak_large:
			name = unit.find('xmlns:nameTChinese', xmlns).text
			address = unit.find('xmlns:addressTChinese', xmlns).text
			if not name in override_table:
				override_f.write(f'\n{name}\t[NO OVERRIDE]\t0\t0\t{address}')
			unparsed_count += 1
			print('Unable to parse ' + address)
		else:
			parsed_index.append(unit_index)
			# trim detail and join the address
			address = ', '.join(fields[trim_index:])
			address = re.sub(r', ?,', ',', address)
			parsed_address.append(address)
			print('Parsed ' + address)
	override_f.close()
	print(f'Parsing ratio is {len(parsed_address)}:{unparsed_count}')
	# return all required data for traversing XML
	return [parsed_index, parsed_address, [len(parsed_address), unparsed_count]]

# take in valid address list and perform API request
def batch_req(parsed_index, parsed_address, root, xmlns_url, ratio, override_table):
	lookup_url = 'https://www.als.ogcio.gov.hk/lookup?n=1&q='
	xmlns = {'xmlns': xmlns_url}
	# allocate full length longlat list
	unit_list = root.find('xmlns:serviceUnits', xmlns).findall('xmlns:serviceUnit', xmlns)
	longlat_list = [[0,-91]] * len(unit_list)
	# for finishing time estimation
	start_time = time.time()
	# encode and request multiple URL simultaneously
	request_gen = (grequests.get(lookup_url + urllib.parse.quote(address) + '&i=' + str(parsed_index[request_index]))
		for request_index, address in enumerate(parsed_address))
	override_f = open('override.csv', 'a', encoding='utf-8-sig')
	for time_index, response in enumerate(grequests.imap(request_gen, size=50)):
		address = urllib.parse.unquote(response.request.url.split('&q=')[1].split('&i=')[0])
		# recovery prompt
		if not response:
			print('Request failed for ' + address + ', trying again')
			response = requests.get(response.request.url)
			if not response:
				print('Giving up, try diagnose network and rerun later')
				sys.exit()
		print('Got response for ' + address)
		# traverse into the tree
		longlat_root = xml.etree.ElementTree.fromstring(response.text)
		# check district correctness
		unit_index = int(response.request.url.split('&i=')[1])
		target_unit = unit_list[unit_index]
		parsed_district = target_unit.find('xmlns:districtEnglish', xmlns).text.upper().replace(' AND ', ' & ')
		address_prefix = 'SuggestedAddress/Address/PremisesAddress/'
		longlat_district = longlat_root.find(address_prefix + 'EngPremisesAddress/EngDistrict/DcDistrict').text
		name = target_unit.find('xmlns:nameTChinese', xmlns).text
		# append to override table if district test failed and no entry exists
		if parsed_district not in longlat_district and name not in override_table:
			print('District test failed for ' + address)
			tcaddress = target_unit.find('xmlns:addressTChinese', xmlns).text
			override_f.write(f'\n{name}\t[NO OVERRIDE]\t0\t0\t{tcaddress}')
			ratio[0] -= 1
			ratio[1] += 1
			continue
		lon = float(longlat_root.find(address_prefix + 'GeospatialInformation/Longitude').text)
		lat = float(longlat_root.find(address_prefix + 'GeospatialInformation/Latitude').text)
		# distort slightly to reduce the chance of overlap
		lon += random.randrange(-50, 50) / 1000000
		lat += random.randrange(-50, 50) / 1000000
		longlat_list[unit_index] = [round(lon, 6), round(lat, 6)]
		# scale used time to estimate time
		estimate_sec = (len(parsed_index) / (time_index + 1) - 1) * (time.time() - start_time)
		print('[Estimated time left: ' + str(datetime.timedelta(seconds=estimate_sec)) + ']')
	print(f'Query ratio is {ratio[0]}:{ratio[1]}')
	override_f.close()
	print('Requesting override table')
	request_gen = (grequests.get(lookup_url + urllib.parse.quote(value.split('\t')[0]) + '&i=' + urllib.parse.quote(key))
		for key, value in override_table.items() if value.split('\t')[0] != '[NO OVERRIDE]')
	for time_index, response in enumerate(grequests.imap(request_gen, size=50)):
		address = urllib.parse.unquote(response.request.url.split('&q=')[1].split('&i=')[0])
		# recovery prompt
		if not response:
			print('Request failed for ' + address + ', trying again')
			response = requests.get(response.request.url)
			if not response:
				print('Giving up, try diagnose network and rerun later')
				sys.exit()
		print('Got response for ' + address)
		longlat_root = xml.etree.ElementTree.fromstring(response.text)
		address_prefix = 'SuggestedAddress/Address/PremisesAddress/'
		lon = float(longlat_root.find(address_prefix + 'GeospatialInformation/Longitude').text)
		lat = float(longlat_root.find(address_prefix + 'GeospatialInformation/Latitude').text)
		# distort slightly to reduce the chance of overlap
		lon += random.randrange(-50, 50) / 1000000
		lat += random.randrange(-50, 50) / 1000000
		table_key = urllib.parse.unquote(response.request.url.split('&i=')[1])
		offset = override_table[table_key].split('\t')[1:3]
		override_table[table_key + '\tLongLat'] = [round(lon + float(offset[0]), 6), round(lat + float(offset[1]), 6)]
	print('Applying override table')
	unit_dict_list = xmljson.parker.data(root)[f'{{{xmlns_url}}}serviceUnits'][f'{{{xmlns_url}}}serviceUnit']
	for index, unit in enumerate(unit_dict_list):
		# define None for default address override
		unit_dict_list[index][f'{{{xmlns_url}}}addressOverride'] = None
		name_key = unit[f'{{{xmlns_url}}}nameTChinese']
		if name_key + '\tLongLat' in override_table:
			longlat_list[index] = override_table[name_key + '\tLongLat']
			unit_dict_list[index][f'{{{xmlns_url}}}addressOverride'] = override_table[name_key].split('\t')[0]
	print('Reordering data by decreasing latitude')
	lat_unit_map, longlat_list = zip(*sorted(zip(range(len(longlat_list)), longlat_list),
		key=lambda unit: unit[1][1], reverse=True))
	# uses JS to avoid CORS
	print('Writing langlat and dumping XML as JS to unitinfo.js')
	with open('scripts/unitinfo.js', 'w', encoding='utf-8') as f:
		f.write('var longlat = ')
		json.dump(longlat_list, f, ensure_ascii=False, separators=(',', ':'))
		f.write(';\nvar unitinfo = [')
		# strip namespace from key
		xml_key = [re.sub(r'^\{[^\}]*\}', '', key) for key in list(unit_dict_list[0].keys())]
		json.dump(xml_key, f, ensure_ascii=False, separators=(',', ':'))
		for unit_index in lat_unit_map:
			f.write(',')
			json.dump(list(unit_dict_list[unit_index].values()), f, ensure_ascii=False, separators=(',', ':'))
		f.write('];')
	print('Finished unitinfo.js')


print('All data generated by this script is contained in scripts/unitinfo.js')
service_url = input('Enter URL of target XML (Leave empty if using the same URL as previous run): ')
service_url, override_table = get_override_table(service_url)
print('XML request sent')
service_root = request_service_xml(service_url)
xmlns_url = re.search(r'(?<=^{)[^}]*(?=})', service_root.tag)
xmlns_url = xmlns_url[0] if xmlns_url else ''
print('Parsing address')
result_list = parse_address(service_root, xmlns_url, override_table)
print('Requesting for geospatial information')
batch_req(result_list[0], result_list[1], service_root, xmlns_url, result_list[2], override_table)
print('Succesfully execute getlonglat.py')
