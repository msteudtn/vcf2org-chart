# vcf2org-chart +++ Contacts-to-organization-chart-converter
# License: MIT
# Version: 0.1.20260619

# ######################################################################
# DEFINE VARIABLES
#
# ######################################################################

# Look for these elements from the vCard.
# The first four items: "FN", "NOTE", " ", "CATEGORIES" must be in the list! Anything else is optional.
list_of_vcf_property_types = ["FN", "NOTE", " ", "CATEGORIES", "ADR", "TEL", "EMAIL", "BDAY", "URL", "PHOTO"]

# The dictionary (array) that's going to be filled with the contact details and turned into a JSON.
dictionary_of_contacts = {}

# A list (array) of categories from the vCard, like "Family" or "Friends"
# This is going to be turned into a contact-entry later, so we can put the children under it.
# Example: ["FN": "Bart Simpson", CATEGORIES:"My Family"] -> Main: Homer (###) -> first contact: MyFamily (##) -> contact: Bart 
list_of_categories = []

# A  dictionary (array) of parent-nodes and their respective ID
# Example: ["14": {FN:"Lisa Simpson", NOTE:"She's the daughter. ##lisa"} } -> Save {"14":"##lisa"}
dictionary_of_known_parents = {}

# A dictionary (array) of child-nodes and their respective ID
# Example: ["10": {FN:"Elizabeth Hoover", NOTE:"Teacher of Lisa Simpson. #lisa"} } -> Save {"#lisa":"[10, ...] "}
# Example: ["22": {FN:"Ralph Wiggum", NOTE:"He's a classmate. #lisa"} } -> Save {"#lisa":"[10, 22, ...] "}
dictionary_of_known_children = {}

# A dictionary for the final ORG-CHART. It's going to be turned into a JSON later.
dictionary_for_org_chart_json = {}

# A counter for the number of contacts.
# This is used as an ID later.
contact_counter = 0

# The ID of the persons address book = You = identified by three hashes (###)
id_number_of_main_character = 0

# ######################################################################
# DEFINE FUNCTIONS
#
# ######################################################################

# Function to "clean" the contact details from special characters.
# Example: " A text with 'special' characters \n" -> "A text with &apos;special&apos; characters" 
def function_clean_contact_details(vcf_file_line, vcf_property_value, length_corrector):

	# Get the length of the property-type because it has to be cut out later.
	vcf_property_type_to_search_length = len(vcf_property_type_to_search) + length_corrector


	# Save the property-value in a variable and ...
	# ... cut out the leading property-type, like "FN", "NOTE", "TEL", etc.
	# Example: "FN:Homer Simpson" minus THREE characters (length of "FN" + 1) = "Homer Simpson"
	# Example: " the second line of a note continues here" minus ONE characters (length of " " + 0) = "the note continues here"
	vcf_property_value = vcf_file_line[vcf_property_type_to_search_length:]


	# Do not use strip() on NOTE, because it clears the white spaces in the "NOTE"-section. This leads to spelling mistakes. :(
	# Example: "A note with \n two lines." -> strip() -> "A note withtwo lines."
	if ( (vcf_property_value != "NOTE") or (vcf_property_value != " ") ):
		pass
	else:
		vcf_property_value = vcf_property_value.strip()	

	# ... replace special characters with space
	vcf_property_value = vcf_property_value.replace("\n", "")	# replace the "new line" at the end of the string.
	vcf_property_value = vcf_property_value.replace("\\n", " ")	# replace the string "\n" - mainly in the "NOTE"-section
	vcf_property_value = vcf_property_value.replace("\\", " ")	# replace \
	vcf_property_value = vcf_property_value.replace("\'", "&apos;")	# replace ' with it's HTML entity
	vcf_property_value = vcf_property_value.replace("\"", "&quot;")	# replace " with it's HTML entity

	return vcf_property_value

# print out colorful text messages to the terminal.
# Example: fn_color_message("RED", "This is an error message")
def fn_color_message(color, text):

	if (color == "RED"):
		color = '\033[91m'
	elif (color == "YELLOW"):
		color = '\033[93m'
	elif (color == "GREEN"):
		color = '\033[92m'
	elif (color == "BLUE"):
		color = '\033[94m'
	elif (color == "CYAN"):
		color = '\033[96m'
	elif (color == "GREY"):
		color = '\033[95m'
	else:
		color = ""

	RESET = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

	print(color, text, RESET)


# ######################################################################
# READ FILE-NAME FROM STD IN
#
# ######################################################################

import sys

if ( len(sys.argv) > 1 ): 
	vcf_file_name = sys.argv[1]
	fn_color_message("GREEN", "\n OK: Filename passed to the script. ")
else:
	fn_color_message("RED", "\n ERROR: No filename given. Example: python SCRIPTNAME.PY 'My Contacts.vcf' \n")
	sys.exit([args]) 

try:
	vcf_file_handle = open(vcf_file_name)
	fn_color_message("GREEN", "\n OK: File found and accessible.")
except FileNotFoundError:
	fn_color_message("RED", "\n ERROR: File was not found. Maybe there's a typo?' \n")
	sys.exit([args]) 

# ######################################################################
# VCARD FILE HANDLING
# Go through the vCard-file and get the line number of "BEGIN:VCARD" and "END:VCARD" of each contact into a dictionary{} for further processing
# ######################################################################

fn_color_message("YELLOW", "\n Start: Going through the contact-file.")

# Keep the name of the last property type (FN, NOTE, URL, TEL, ...) in case of long lines (starting with space " ").
last_known_vcf_property_type = ""

with vcf_file_handle as vcf_file:

	for vcf_file_line in vcf_file:

		# If the line starts with "BEGIN:VCARD" we have a new contact.
		if  (vcf_file_line.startswith("BEGIN:VCARD")):
			begin_vcard = True

			# Count the number of contacts for the python-dictionary (array) and convert it to a string, so it can be used as an ID.
			contact_counter = contact_counter + 1
			contact_counter_as_string = str(contact_counter)

			# Create an empty dictionary with the counter as ID (string) 
			# Example: dictionary_of_contacts{ "1":{}, "2":{}, "3":{} }
			dictionary_of_contacts[contact_counter_as_string] = {}

		# Reset the boolean "begin_vcard" when finished.
		elif (vcf_file_line.startswith("END:VCARD")):
			begin_vcard = False


		# We're still in a line with contact details while going through the file.
		if (begin_vcard == True):

			# Go through the list (array) of property-types ["FN", "TEL", ...] from 0 to the end
			for i in range(len(list_of_vcf_property_types)):

				# Get the property-type number i from the list
				# Example: i = 0 = "FN" , i = 1 = "NOTE"
				vcf_property_type_to_search = list_of_vcf_property_types[i]

				# If the property-type from our search-list is at the beginning of the file-line, do something.
				# Example: "FN:Homer Simpson" starts with "FN" = do something
				# Example: "UID" is not in list = do nothing / ignore line
				if (vcf_file_line.startswith(vcf_property_type_to_search)):

					# Save the file-line in a temporary variable
					vcf_property_value = vcf_file_line

					# All properties ("FN", "UID", ...) are usualy one line, except "NOTE:". This has to be handled separately. 
					if (vcf_property_type_to_search == "NOTE"):

						last_known_vcf_property_type = "NOTE"

						# There should *not* be a NOTE in the dictionary, but better save (try, if it exists) than sorry. 
						try:
							vcf_property_value_before = dictionary_of_contacts[contact_counter_as_string]["NOTE"]
							vcf_property_value = function_clean_contact_details(vcf_file_line, vcf_property_value, 1)
							dictionary_of_contacts[contact_counter_as_string]["NOTE"] = vcf_property_value_before + "" + vcf_property_value

						# If the NOTE doesn't exist in the dictionary, create it.
						except KeyError:
							# Clean the VCF-line and create a new key "NOTE" in the dictionary
							# Example: dictionary_of_contacts{ "1":{ "FN":"Homer Simpsons", "NOTE":"a note on Homer"}, "2":{}, "3":{} }
							vcf_property_value = function_clean_contact_details(vcf_file_line, vcf_property_value, 1)
							dictionary_of_contacts[contact_counter_as_string][vcf_property_type_to_search] = vcf_property_value

					# A space as first character is most likely part of a big NOTE or a very long entry (like URL, PRODID, ...).
					# So, we have to put it in the last known property-type
					elif ( (vcf_property_type_to_search == " ") ):

						# If the space character is part of a vCard-NOTE, a dictionary-entry [NOTE] should already exist and we'll add it. 
						try:
							vcf_property_value_before = dictionary_of_contacts[contact_counter_as_string][last_known_vcf_property_type]
							vcf_property_value = function_clean_contact_details(vcf_file_line, vcf_property_value, 0)
							dictionary_of_contacts[contact_counter_as_string][last_known_vcf_property_type] = vcf_property_value_before + "" + vcf_property_value

						# If the NOTE doesn't exist, we'll add the value, to the corresponding property.
						# In practice, this case should't happen, because most properties are only one line and don't need a space character.
						except KeyError:
							# Clean the VCF-line and create a new key "PROPERTY-VALUE" in the dictionary
							# Example: dictionary_of_contacts{ "1":{ "FN":"Homer Simpsons", "PRODID":"Thunderbird CardBook"}, "2":{}, "3":{} }
							vcf_property_value = function_clean_contact_details(vcf_file_line, vcf_property_value, 0)
							dictionary_of_contacts[contact_counter_as_string][last_known_vcf_property_type] = vcf_property_value

					# CATEGORIES will be upgraded to their own contact-name later. So, we have to find them, too.
					elif (vcf_property_type_to_search == "CATEGORIES"):

						last_known_vcf_property_type = "CATEGORIES"

						# 1.) Clean and save the category as a normal entry to the dictionary.
						# Example: dictionary_of_contacts{ "14":{ "FN":"Lisa Simpsons", "CATEGORIES":"My Family"}, "15":{}, "16":{} }
						vcf_property_value = function_clean_contact_details(vcf_file_line, vcf_property_value, 1)
						dictionary_of_contacts[contact_counter_as_string][vcf_property_type_to_search] = vcf_property_value

						# 2.) Save the name of the category in an extra category-list. Categories can appear multiple times.  
						# So, we're turning it into an extra dictionary-entry later.
						# Example: "FN: Bart / CAT: Family", "FN: Lisa / CAT: Family" -> new ID with FN "Family" later.

						# Split the CATEGORIES on comma "," in case we have multiple categories 
						# Example: "My Family, Friends" -> ["My Family", "Friends"]
						list_of_split_categories = vcf_property_value.split(",")

						# Go through the list of categories ["My Family", "Friends"] and add it to the general category-list.
						for category in list_of_split_categories:

#							list_of_categories.append(category.lower())
							list_of_categories.append(category)

						# 3.) Also add the category name as a hashtag to the contact NOTE
						# Example: CATEGORIES:"My Family" -> NOTE:"#myfamily"
						try:
							vcf_property_value_before = dictionary_of_contacts[contact_counter_as_string]["NOTE"]
							dictionary_of_contacts[contact_counter_as_string]["NOTE"] = vcf_property_value_before + " #" + vcf_property_value.replace(" ", "").lower() + " "

						except KeyError:
							dictionary_of_contacts[contact_counter_as_string]["NOTE"] = " #" + category.replace(" ", "").lower() + " "

					# All other properties, like "FN", "TEL", etc. (that are not "NOTE" or " " or "CATEGORIES") are processed here
					else:

						last_known_vcf_property_type = vcf_property_type_to_search

						# Check if the key already exists and add the new entry to the old one.
						# Example: dictionary_of_contacts{ "11":{ "FN":"Homer", "TEL":"123"}, "2":{}, "3":{} }
						# Example: dictionary_of_contacts{ "11":{ "FN":"Homer", "TEL":"123 456"}, "2":{}, "3":{} }
						try:
							dictionary_of_contacts[contact_counter_as_string][vcf_property_type_to_search]
							vcf_property_value = function_clean_contact_details(vcf_file_line, vcf_property_value, 1)
							vcf_property_value_before = dictionary_of_contacts[contact_counter_as_string][vcf_property_type_to_search]
							dictionary_of_contacts[contact_counter_as_string][vcf_property_type_to_search] = vcf_property_value_before + " " + vcf_property_value

						# The normal behaviour if the key doesn't exist already.
						except KeyError:
							vcf_property_value = function_clean_contact_details(vcf_file_line, vcf_property_value, 1)
							dictionary_of_contacts[contact_counter_as_string][vcf_property_type_to_search] = vcf_property_value

				# The line starts with something else, but not an item from the seach-list [FN, NOTE, ...] -> ignore!
				else:
					pass

# Close the file handle.
vcf_file_handle.close()

fn_color_message("YELLOW", "Finished: Going through the contact-file.")


# Warning messages
if (contact_counter > 0):
	fn_color_message("GREEN", "\n OK: {} contacts found in vCard VCF file.".format(contact_counter))
else:
	fn_color_message("RED", "\n Error: No contacts found in VCF file. Is it really a vCard-format?")



# ######################################################################
# FIND THE PARENT AND CHILD HASHES (###,##,#)
# Go through dictionary of contacs (array) and put ##PARENTS and ##CHILDREN into their own dictionaries
# ######################################################################

fn_color_message("YELLOW", "\n Start: Looking for hash-tags in the NOTE-part.")

# Go through all the contact IDs and look for the NOTE-part
# Example: "1": {FN: Homer, TEL: "12345"}, "2": {FN: "Bart", NOTE: "a note"}
for contact_key, contact_value in dictionary_of_contacts.items():

	note_found = False

	# Check if the contact has a NOTE
	try:
		note_value = dictionary_of_contacts[contact_key]["NOTE"]
		note_found = True
	except KeyError:
		note_found = False

	# The NOTE-part was found. It contains information on the relations.
	if (note_found == True):

		# See, if there's at least on hash in the note. (False-positive may be possible, also. :( )
		if (note_value.find("#") > -1):

			# Split the NOTE at the space-character and save as a list (array).
			# Example: "a note on Bart ##bart" -> ["a", "note", "on", "Bart", "##bart"]
			list_of_split_note = note_value.split(" ")

			# Go through the list and find all entries with a hash "#". 
			for word in list_of_split_note:

				# Count the number of hashes in the entry
				# Example: ["##bart"] = 2x
				if (word.find("#") > -1):

					# Find the main node with three hashes "###" and save its ID.
					if (word.count("#") == 3):
						# Check if the ID number has been set before = more than one entry with "###"
						if (int(id_number_of_main_character) > 0):
							fn_color_message("RED", " Error: There is more than one entry with three hashes '###'. Can't decide who the main contact is. Last found contact is: {}".format(contact_value))
						else:
							id_number_of_main_character = contact_key
							fn_color_message("GREEN", " OK: Found the main contact: {} ".format(contact_value["FN"]))

					# Find the parent-nodes with two hashes "##" and save it to a dictionary for easier processing in the next run.
					# Example: ["14": {FN:"Lisa Simpson", NOTE:"She's the daughter. ##lisa"} } -> Save {"14":"##lisa"}
					elif (word.count("#") == 2):

						# Check, if the ID is already in the list of KNOWN PARENTS or add it to the existing ID
						try:
							dictionary_of_known_parents[contact_key].append(word)
						except KeyError:
							dictionary_of_known_parents[contact_key] = []
							dictionary_of_known_parents[contact_key].append(word)

					# Find the child-nodes with one hash "#" and save it to a dictionary for easier processing in the next run.
					# Example: ["22": {FN:"Ralph Wiggum", NOTE:"Classmate #lisa"} } -> Save {"#lisa":"[22, 27, ...] "}
					elif (word.count("#") == 1):

						# Check, if the #CHILD is already in the list of KNOWN CHILDREN or add it to the existing #child-hash
						try:
							dictionary_of_known_children[word].append( str(contact_key) )
						except KeyError:
							dictionary_of_known_children[word] = []
							dictionary_of_known_children[word].append( str(contact_key) )

					# All other hash-findings, like four hashes "####" are ignored.
					else:
						pass

				# ELSE #hash-counting: no hash counted -> ignore.
				else:
					pass

		# ELSE: #hash-finding: No hash found in NOTE-part -> add a parent / a NOTE "#nocategory" for this ID
		# Example: [FN:"Skinner", NOTE:"no hashtags here"] -> [FN:"Skinner", NOTE:"no hashtags here #nocategory"]  
		else:
			old_note =  dictionary_of_contacts[contact_key]["NOTE"]
			dictionary_of_contacts[contact_key]["NOTE"] = old_note + " #nocategory"

			# Add the ID number to the list of KNOWN CHILDREN at "#nocategory"
			# Example: ['#nocategory': '1, 21, ...']  
			try:
				dictionary_of_known_children["#nocategory"].append( str(contact_key) )
			except KeyError:
				dictionary_of_known_children["#nocategory"] = []
				dictionary_of_known_children["#nocategory"].append( str(contact_key) )

	# ELSE NOTE-finding: The contact has no NOTE-element. -> add "#nocategory" to the contact as NOTE
	else:

		# Add a new NOTE to the contact.
		dictionary_of_contacts[contact_key]["NOTE"] = " #nocategory"

		# Add the ID number to the list of KNOWN CHILDREN at "#nocategory"
		try:
			dictionary_of_known_children["#nocategory"].append( str(contact_key) )
		except KeyError:
			dictionary_of_known_children["#nocategory"] = []
			dictionary_of_known_children["#nocategory"].append( str(contact_key) )

fn_color_message("YELLOW", "Finished: Looking for hash-tags in the NOTE-part.")


# Error messages
if ( len(dictionary_of_known_children) > 0):
	fn_color_message("GREEN", "\n OK: Single #hash-tags (as children) were found in the contacts.")
else:
	fn_color_message("RED", "\n Error: No single #hash-tags were found in the contacts.")

if ( len(dictionary_of_known_parents) > 0):
	fn_color_message("GREEN", "\n OK: Double ##hash-tags (as parents) were found in the contacts.")
else:
	fn_color_message("RED", "\n Error: No double ##hash-tags were found in the contacts.")

if ( id_number_of_main_character != ""):
	fn_color_message("GREEN", "\n OK: A person with three ###hash-tags was found as main person.")
else:
	fn_color_message("RED", "\n Error: No person with three ###hash-tags was found as main person.")


# ######################################################################
# UPDATE "DICTIONARY OF CONTACTS" WITH CATEGORIES AND PARENTS
# Go through the dictionary (array) and add the CATEGORIES as "FN"
# ######################################################################

# (1.) Always create a new contact "No category" in the CONTACT-dictionary as future parent.
fn_color_message("YELLOW", "\n Start: Adding a new contact 'No Category' to the existing contacts.")

# Count the number of contacts for the python-dictionary (array) and convert it to a string, so it can be used as an ID in JSON.
contact_counter = contact_counter + 1
contact_counter_as_string = str(contact_counter)

# Create an empty nested dictionary with the counter as ID (string) 
# Example: dictionary_of_contacts{ "10":{}, "11":{}, "12":{} }
dictionary_of_contacts[contact_counter_as_string] = {}

# Add "No category" as name ("FN") into the new ID
dictionary_of_contacts[contact_counter_as_string]["FN"] = "No category"

# Add "##nocategory" as hastag into the NOTE-field
dictionary_of_contacts[contact_counter_as_string]["NOTE"] = "##nocategory".lower()

# Add "##nocategory" to the dictionary of known parents
dictionary_of_known_parents[contact_counter_as_string] = []
dictionary_of_known_parents[contact_counter_as_string].append("##nocategory".lower())

# Add the "#nocategory" to the list of KNOWN CHILDREN, in case, it is not there yet.
try:
	test_child = dictionary_of_known_children["#nocategory"]
except KeyError:
	dictionary_of_known_children["#nocategory"] = []


# Add the main contact as parent to the ##nocategory-entry
dictionary_of_contacts[contact_counter_as_string]["PARENTS"] = str(id_number_of_main_character)

fn_color_message("YELLOW", "Finished: Adding a new contact 'No Category' to the existing contacts.")


# (2.) Go through the list of CATEGORIES ["My Family", "Friends"] and add it to the dictionary of contacts with the PARENT of the MAIN CONTACT
fn_color_message("YELLOW", "\n Start: Looking for CATEGORIES within the contacts and add them as new contact.")


# Remove all duplicates from the list
list_of_unique_categories = list(dict.fromkeys(list_of_categories))

# Go through the list of categories ["My Family", "Friends"] and add a new ID and a "FN" entry.
for category in list_of_unique_categories:

	# Count the number of contacts for the python-dictionary (array) and convert it to a string, so it can be used as an ID in JSON.
	contact_counter = contact_counter + 1
	contact_counter_as_string = str(contact_counter)

	# Create an empty nested dictionary with the counter as ID (string) 
	# Example: dictionary_of_contacts{ "10":{}, "11":{}, "12":{} }
	dictionary_of_contacts[contact_counter_as_string] = {}

	# Add the category ["My Family", "Friends", ...] as name ("FN") into the new ID
	dictionary_of_contacts[contact_counter_as_string]["FN"] = category 
	# Add the category as note ("NOTE") into the new ID but replace all spaces and add a two hashes because the category is going to be a parent-node.
	# Example: "My Family" -> "##myfamily"
	dictionary_of_contacts[contact_counter_as_string]["NOTE"] = "##" + category.replace(" ", "").lower()

	# Add the main contact as parent to the entry
	dictionary_of_contacts[contact_counter_as_string]["PARENTS"] = str(id_number_of_main_character)

	# Add the new CONTACT-ID to the dictionary of parents ...
	dictionary_of_known_parents[contact_counter_as_string] = []
	dictionary_of_known_parents[contact_counter_as_string].append( "##" + category.replace(" ", "").lower() )

fn_color_message("YELLOW", "Finished: Looking for CATEGORIES within the contacts and add them as new contact.")


# ######################################################################
# SEARCH FOR MISSING PARENTS
# Go through the list of parents and children and add look for missing parents
# Example: The child "#work" is in the contact-NOTE but there's no parent "##work" for it.
# ######################################################################

fn_color_message("YELLOW", "\n Start: Looking for child-nodes without any parent-nodes and create new parent-contacts.")

# Create a temporary list
temporary_list_of_unknown_parents = []

# The child-dictionary has a list of IDs [1,5,13,22] after it's key-string ["#bart"]. 
# So, it's labeled the other way around here ("value, keys" instead of the correct "key, value").
# Example: child{'#bart': '1,5,13,22'}
for child_value, child_keys in dictionary_of_known_children.items():

	# Loop through the dictionary of parents
	# Example: parent{'11': '##bart-school,##bart-kindergarten', '12':'##myfamily'}
	for parent_key, parent_values in dictionary_of_known_parents.items():

		# Split the parent-value into a list (array)
		# Example: {'1': '##bart-school,##bart-kindergarten'} -> ['##bart-school','##bart-kindergarten']
		bool_parent_found = False

		for parent_value in parent_values:

			# If parent and child match together, we don't need the child value
			# Example: ##bart-school[2:] == #bart-school[1:]
			if ( parent_value[2:] == child_value[1:] ):
				bool_parent_found = True
				child_value = ""
				break
			else:
				pass

		if (bool_parent_found == True):
			break
		else:
			pass

	# Save the current #child value to the temporary list of UNKNOWN ##PARENTS
	if ( len(child_value) >  0):
		temporary_list_of_unknown_parents.append("#"+child_value)


# ADD THE UNKNOWN PARENTS TO THE FIRST LEVEL (LIKE CATEGORIES)
for parent_value in temporary_list_of_unknown_parents:

	# Count the number of contacts for the python-dictionary (array) and convert it to a string, so it can be used as an ID in JSON.
	contact_counter = contact_counter + 1
	contact_counter_as_string = str(contact_counter)

	# Create an empty nested dictionary with the counter as ID (string) 
	# Example: dictionary_of_contacts{ "10":{}, "11":{}, "12":{} }
	dictionary_of_contacts[contact_counter_as_string] = {}

	# Add the category as name ("FN") into the new ID
	dictionary_of_contacts[contact_counter_as_string]["FN"] = parent_value 
	# Add the category as note ("NOTE") into the new ID but replace all spaces and add a two hashes because the category is going to be a parent-node.
	# Example: "My Family" -> "##MyFamily"
	dictionary_of_contacts[contact_counter_as_string]["NOTE"] = "" + parent_value.replace(" ", "").lower()

	# Add the parent (main contact) to the entry
	dictionary_of_contacts[contact_counter_as_string]["PARENTS"] = str(id_number_of_main_character)

	# Add the new CONTACT-ID to the dictionary of parents ...
	dictionary_of_known_parents[contact_counter_as_string] = []
	dictionary_of_known_parents[contact_counter_as_string].append( "" + parent_value.replace(" ", "").lower() )


fn_color_message("YELLOW", "Finished: Looking for child-nodes without any parent-nodes and create new parent-contacts.")


# ######################################################################
# FIND PARENTS WITH MULTIPLE CHILDREN AND UPDATE THE KNOW PARENTS AND CONTACTS
# Example: before: {'1': ['##bart-school','##bart-kindergarten']} -> after: {99:['bart-school'], 100:['bart-kindergarten']}
# ######################################################################

fn_color_message("YELLOW", "\n Start: Find parents with multiple children and save their values.")

temporary_list_of_known_parents_to_delete = []
temporary_dictionary_of_known_parents_to_add = {}

# (1.) Check, if there's a KNOWN PARENT-ID with multiple hash-entries, we'll set it as new CONTACT
# Example: KNOWN PARENT{'3': '##bart-school,##bart-kindergarten'} -> new CONTACT{'99', {'FN':'bart-school', 'PARENTS':3} }
for parent_key, parent_values in dictionary_of_known_parents.items():

	# If there's more than one entry for this parent.
	if ( len(parent_values) >  1):

		for parent_value in parent_values:

			# Count the number of contacts for the dictionary (array) and convert it to a string, so it can be used as an ID in JSON.
			contact_counter = contact_counter + 1
			contact_counter_as_string = str(contact_counter)

			# Create an empty nested dictionary with the counter as ID (string) 
			# Example: dictionary_of_contacts{ "10":{}, "11":{}, "12":{} }
			dictionary_of_contacts[contact_counter_as_string] = {}

			# Add the category as name ("FN") into the new ID (and cut off the two hashes "##")
			# Example: ##bart-school -> bart-school
			dictionary_of_contacts[contact_counter_as_string]["FN"] = parent_value[2:] 
			# Add the category as note ("NOTE") into the new ID 
			# (No need to replace all spaces or add two hashes, because the parent_value from the dictionary of KNOWN PARENTS already has it.
			dictionary_of_contacts[contact_counter_as_string]["NOTE"] = parent_value

			# Add the parent ID to the new entry in the CONTACTS
			# Example: KNOWN PARENT{'3': '##bart-school,##bart-kindergarten'} -> new CONTACT{'99', {'FN':'bart-school', 'PARENTS':3} }
			dictionary_of_contacts[contact_counter_as_string]["PARENTS"] = str(parent_key)

# (2a.) Check (again), if there's a KNOWN PARENT-ID with multiple hash-entries, we'll set it as new KNOWN-PARENT and update the old KNOWN-PARENT-entry
for parent_key, parent_values in dictionary_of_known_parents.items():

	# If there's more than one entry for this parent.
	if ( len(parent_values) >  1):

		for parent_value in parent_values:

			for contact_key, contact_value in dictionary_of_contacts.items():

				contact_name = contact_value["FN"].replace(" ", "").lower()

				# If the parent-name matches the contact-name
				# Example: known_parents{"3" : "##bart-school[2:]" == contacts{"FN" : "bart-school"}
				if (parent_value[2:] == contact_name):

					# Add the existing contact-ID to the KNOWN PARENTS TO DELETE
					temporary_list_of_known_parents_to_delete.append(parent_key)

					# Add the new parent-name to the KNOWN PARENTS TO ADD
					temporary_dictionary_of_known_parents_to_add[str(contact_key)] = "##"+contact_name

# (2b.) Remove all duplicates from the list
temporary_list_of_known_parents_to_delete_cleaned = list(dict.fromkeys(temporary_list_of_known_parents_to_delete))

# (2c.) Add the newly found key and value to the existing KNOWN PARENTS
for temp_new_parent_key, temp_parent_value in temporary_dictionary_of_known_parents_to_add.items():

	dictionary_of_known_parents[temp_new_parent_key] = []
	dictionary_of_known_parents[temp_new_parent_key].append(temp_parent_value)

# (2d.) Delete the old parent-ID from the KNOWN PARENTS
# Example: known_parents{"3" : "##bart-school,##bart-kindergarten, "4":"##lisa"} -> {"4":"##lisa"}
for temp_old_parent_key in temporary_list_of_known_parents_to_delete_cleaned:

	dictionary_of_known_parents.pop(str(temp_old_parent_key))

fn_color_message("YELLOW", "Finished: Find parents with multiple children and save their values.")

# ######################################################################
# ADD THE KNOWN PARENTS TO THE CORRESPONDING CONTACTS
# Example: Contact{FN:"Bart"} -> Contact{FN:"Bart", "PARENTS":99}
# ######################################################################

fn_color_message("YELLOW", "\n Start: Add the found values as new parent-contact.")

for contact_key, contact_value in dictionary_of_contacts.items():

	# Check if there's already a parent for this contact 
	# (unlikely for most contact-details except the categories, like ##myfamily or ##friends)
	try:
		dictionary_of_contacts[contact_key]["PARENTS"]
		# nothing to do. This contact already has a PARENTS-element
		pass
	except KeyError:

		# Go though the dictionary of KNOWN CHILDREN and see, if we have a matching entry
		# Example: contacts{'10': {'FN': 'Bart Simpson', 'NOTE': 'a note on Bart'} -> know_children{'#myfamily': '10,2,3'} -> ID = 10, parent = #myfamily
		for child_value, child_keys in dictionary_of_known_children.items():

			# Go through the child-values 
			# Example: {'#myfamily': [10,2,3]} -> 10,2,3
			for child_key in child_keys:

				# Good, the child-ID matches the contact-key
				# Example:  KNOWN_CHILDREN '#myfamily': 10 = CONTACT key "10" (Bart) 
				if (child_key == contact_key):

					# Go through the dictionary of KNOWN PARENTS and look for the parent, that matches the child_value
					# Example: parent of child 10 (Bart) = "#myfamily" -> ID of parent ##myfamily = 8 
					for parent_key, parent_values in dictionary_of_known_parents.items():

						for parent_value in parent_values:

							# Check if the values match
							if (parent_value[2:] == child_value[1:]):	
								dictionary_of_contacts[child_key]["PARENTS"] = str(parent_key)
								break
							else:
								# Mismatch, nothing to do
								pass

fn_color_message("YELLOW", "Finished: Add the found values as new parent-contact.")

# ######################################################################
# LOOK FOR DOUBLE-CHILDREN-IDS AND REMOVE THE PARENT-ID IF IT IS A NORMAL *CATEGORY*
# Some 
# Example: "6":"Carl" -> "#friends":["2","6","13","18"] and "#work": ["6","7","13","24"] 
#           -> becomes   "#friends":["2","13","18"]     and "#work": ["6","7","13","24"] 
# ######################################################################

# (1.) Find children, that are in both the categories and known_children.

# Create a dictionary for the double children
# Example: {'#friends': ['13', '6'], '#myfamily': ['24']}
dictionary_of_double_children = {}

# Loop through the known CATEGORIES
for category in list_of_unique_categories:

	category = "#" + category.replace(" ", "").lower() + ""

	# Loop through the KNOWN CHILDREN
	for child_value, child_keys in dictionary_of_known_children.items():

		# If the CATEGORY equals the KNOWN CHILD
		# Example: #myfamily == #myfamily
		if (child_value == category):

			# Create an empty list in the dictionary with key #category
			dictionary_of_double_children[child_value] = []


			# Go through the same list of KNOWN CHILDREN again but look for duplicates
			for child_value2, child_keys2 in dictionary_of_known_children.items():

				# Use the SET()-Method to find duplicates
				double_child = set(child_keys) & set(child_keys2)

				# If there's a child twice in the lists AND it's not the category (child_value != child_value2)
				# Example: ['24'] AND ( #myfamily != #work )
				if (double_child) and (child_value != child_value2):

					# Turn the set() into a list[]
					list_of_double_children = list(double_child)

					# Loop through the list of double children and add it to the dictionary of double of children
					# Example: ['13', '6'] -> '#friends': ['13', '6'] 
					for double_child_key in list_of_double_children:

						# Add the double child to the dictionary of double children.  
						dictionary_of_double_children[child_value].append(double_child_key)

			break
		# nothing to do. 
		else:
			pass


# (2.) Delete the DOUBLE CHILDREN from the CATEGORY-element in KNOWN CHILDREN

list_of_unique_children = []

for child_value, child_keys in dictionary_of_double_children.items():

	# Find only unique elements in the two lists
	# Source: https://stackoverflow.com/questions/28444561/get-only-unique-elements-from-two-lists
	temporary_list_from_double_children = dictionary_of_double_children[child_value]
	temporary_list_from_known_children = dictionary_of_known_children[child_value]

	list_of_unique_children = list(set(temporary_list_from_double_children).symmetric_difference(set(temporary_list_from_known_children)))

	# Replace the old list of known children at the CATEGORY with the new list of unique children

	dictionary_of_known_children[child_value] = list_of_unique_children

# (3.) Update the PARENTS-entry in the CONTACTS-dictionary one last time based on the updated KNOWN CHILDREN.

# Loop through the KNOWN PARENTS (because the lister is usually shorter) and get the parent-name and ID
for parent_key, parent_value in dictionary_of_known_parents.items():

	# Loop through the KNOWN CHILDREN and find the corresponding value
	for child_value, child_keys in dictionary_of_known_children.items():

		# Check if the values match
		# Example: children:"#friends" == parents:"##friends"
		if ("#"+child_value == parent_value[0]):

			# Loop through the child-IDs ['6', '7', '13', '24'] and update the contact-PARENTS
			for child_key in child_keys:

				# If the contact is a prent of "##no", we'll delete the whole contact. So, it doesnt'show up in the JSON-export, later.
				if (parent_value[0] == "##no"):
					dictionary_of_contacts.pop( str(child_key) )

				# If it's a normal contact, we'll update CONTACT with the new parent
				else:
					dictionary_of_contacts[str(child_key)]["PARENTS"] = parent_key

		# The parent and child-value don't match. Nothing to do
		# Example: #friends != ##family
		else:
			pass

# (4.) Delete the CONTACT named "#no" (keyword for ignored parents)
# Loop thourgh the KNOWN PARENTS and find the ID of "##no"
for parent_key, parent_value in dictionary_of_known_parents.items():

	if ( parent_value[0] == "##no" ):
		dictionary_of_contacts.pop( str(parent_key) )
	else:
		pass

# (5.) We might have empty parents / categories now. 
# So, we'll delete the entry in the contacts

# Loop through the KNOWN CHILDREN and see if there are any empty key-lists
for child_value, child_keys in dictionary_of_known_children.items():

	# If the value has IDs in it, there's nothing to do.
	# Example: #myfamily:['6', '7', '13', '24'] 
	if ( len(child_keys) > 0):
		pass
	else:
		for parent_key, parent_value in dictionary_of_known_parents.items():

		# Check if the values match
		# Example: children:"#friends" == parents:"##friends"
			if ("#"+child_value == parent_value[0]):

				# Delete the element from the dictionary of CONTACTS
				dictionary_of_contacts.pop( str(parent_key) )



# ######################################################################
# CREATE THE JSON-DATA OUT OF THE DICTIONARAY OF CONTACTS
# 
# ######################################################################

fn_color_message("YELLOW", "\n Start: Going through the dictionary and create JSON-data.")

# (1.) Get the main contact as first entry

# Create an empty dictionary (array) for the JSON-data
dictionary_of_json_data = {}

# Get the main-ID's name from FN as JSON "value"
json_value = dictionary_of_contacts[str(id_number_of_main_character)]["FN"]

# Get the main-ID's contact details from FN as JSON "details"
json_parent = ""
json_details = ""
json_photo = ""

# Try the different contact-values and add it to the JSON-data
for property_type in list_of_vcf_property_types:

	# Skip these property_types
	if ( (property_type == "FN") or (property_type == " ") ):
		pass
	elif (property_type == "PHOTO"):
		try:
			json_photo = dictionary_of_contacts[str(id_number_of_main_character)]["PHOTO"]
			json_photo = json_photo.replace("ENCODING=B;TYPE=PNG:","data:image/png;base64,")
		except KeyError:
			json_photo = ""
	else:

		try:
			json_details = json_details + "<p>" + dictionary_of_contacts[str(id_number_of_main_character)][property_type] + "</p>"
		except KeyError:
			json_details = "" + json_details + ""

dictionary_of_json_data[ "p"+str(id_number_of_main_character) ] = {"id":"mainPerson" ,"value":json_value, "details":json_details, "parent":"", "photo":json_photo}


# (2.) Get all the children and their parents
for contact_key, contact_value in dictionary_of_contacts.items():

	# Skip the ID for the main contact, because we already have an entry on the first position
	if (str(contact_key) == str(id_number_of_main_character)):
		continue

	json_details = ""
	json_parent = ""

	json_value = dictionary_of_contacts[str(contact_key)]["FN"]

	# Try the different contact-values and add it to the JSON-data
	for property_type in list_of_vcf_property_types:

		# Skip these property_types but add all others to the DETAILS-part
		if ( (property_type == "FN") or (property_type == " ") or (property_type == "CATEGORIES")):
			pass
		elif (property_type == "PHOTO"):
			try:
				json_photo = dictionary_of_contacts[str(contact_key)]["PHOTO"]
				json_photo = json_photo.replace("ENCODING=B;TYPE=PNG:","data:image/png;base64,")
			except KeyError:
				json_photo = ""
		else:
			try:
				json_details = json_details + "<p>" + dictionary_of_contacts[str(contact_key)][property_type] + "</p>"
			except KeyError:
				json_details = "" + json_details + ""

	try:
		json_parent = json_parent + "p" + dictionary_of_contacts[str(contact_key)]["PARENTS"]
	except KeyError:
		pass

	dictionary_of_json_data[ "p"+str(contact_key) ] = {"id":"p"+str(contact_key), "value":json_value, "details":json_details, "parent":json_parent, "photo":json_photo}

fn_color_message("YELLOW", "Finished: Going through the dictionary and create JSON-data.")

# ######################################################################
# WRITE FAMILY-TREE-HTML-FILE
# 
# ######################################################################

fn_color_message("YELLOW", "\n Start: Creating the HTML file.")

index_template_file_handle = open("assets/index_template.html")
index_contacts_file_handle = open("index_contacts.html", "w")


with index_template_file_handle as index_template_file:

	for index_template_file_line in index_template_file:

		if (index_template_file_line.strip() == "PLACEHOLDER-FOR-JSON-DATA"):
			index_template_file_line = dictionary_of_json_data
		else:
			pass

		index_contacts_file_handle.write(str(index_template_file_line))

fn_color_message("YELLOW", "Finished: Creating the HTML file.")
	

# ######################################################################
# OPEN BROWSER
# 
# ######################################################################

fn_color_message("YELLOW", "\n Start: Opening HTML file.")

filepath = "index_contacts.html"

import subprocess, os, platform
if platform.system() == 'Darwin':       # macOS
	subprocess.call(('open', filepath))
elif platform.system() == 'Windows':    # Windows
	os.startfile(filepath)
else:                                   # linux variants
	subprocess.call(('xdg-open', filepath))
	pass

fn_color_message("YELLOW", "Finished: Opening HTML file.")

# Finished

if (contact_counter > 0):
	fn_color_message("GREEN", "\n {} contacts processed.".format(contact_counter))
else:
	fn_color_message("RED", "\n Error: no contacts found.")


fn_color_message("GREEN", "\n All finished.")

#import json
#print("\n END: CATEGORIES []", list_of_categories )
#print("\n END: CATEGORIES unique", list_of_unique_categories )
#print("\n END: DOUBLE CHILDREN", dictionary_of_double_children)
#print("\n END: PARENTS", json.dumps(dictionary_of_known_parents, indent=4) )
#print("\n END: CHILDREN", json.dumps(dictionary_of_known_children, indent=4) )
#print("\n END: CONTACTS", json.dumps(dictionary_of_contacts, indent=4) )
#print("\n END: CONTACTS", json.dumps(dictionary_of_json_data, indent=4) )


