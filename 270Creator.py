# 270Creator - a lightweight CLI program for creating EDI-compliant
# 270 files.
#
# Copyright (C) 2015 Derek John Miller
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see 
# http://www.gnu.org/licenses/gpl.txt

import ConfigParser
import os
import segment
import time
import csv
import argparse

# parse cli arguments
parser = argparse.ArgumentParser(description = "Create EDI 270 files from CSV")
parser.add_argument('-i', '--input', help='Input file name', required=True)
parser.add_argument('-d', '--destination', help='Output destination', required=True)

args = parser.parse_args()

# create output file
out_file = open('%s/to_emedny.270' % args.destination, 'w')

# Get initial values from configuration file using ConfigParser module
config=ConfigParser.RawConfigParser()
config.read('270_configuration.cfg')

etin = config.get('Interchange_Control_Header', 'ETIN')
icsi = config.get('Interchange_Control_Header', 'ICSI')
ind_ID = config.get('Functional_Group_Header', 'indID')
payer_name = config.get('Transaction_Set_Header','payerName')
payer_primary_ID = config.get('Transaction_Set_Header','payerPrimaryID')
information_source_name = config.get('Transaction_Set_Header','informationSourceName')
information_primary_ID = config.get('Transaction_Set_Header','informationPrimaryID')   
icn = config.get('Interchange_Control_Number','ICN')

# HL segment counter
hl_num = 1

# need to test whether values exist for variables. if not, raise exception.

# current date and time variables
today = time.localtime()
current_date_short = time.strftime("%y%m%d", today)
current_date_long = time.strftime("%Y%m%d",today)
current_time = time.strftime("%H%M", today)

# construct ISA 
seg = segment.make_segment("ISA", ["00", "          ", "00", "          ",
    "ZZ", etin + "            " , "ZZ", "EMEDNYBAT      ", current_date_short,
    current_time, "^", icsi, str("%09d" % int(icn)),
    "0","P",":"])

text = seg

# construct GS
seg = segment.make_segment("GS", ["HS", etin, "EMEDNYBAT", current_date_long,
    current_time, "1", "X", ind_ID])

text = text + seg

# construct ST
seg = segment.make_segment("ST", ["270", "0001", ind_ID])

text = text + seg

# construct BHT
seg = segment.make_segment("BHT", ["0022", "13", "0", current_date_long,
    current_time])

text = text + seg

# construct HL (payer)
seg = segment.make_segment("HL", [hl_num, "", "20", "1"])

text = text + seg
hl_num += 1

# construct NM (payer)
seg = segment.make_segment("NM1", ["PR", "2", payer_name,"", "", "", "", "FI",
    payer_primary_ID])

text = text + seg

# construct HL (information source)
seg = segment.make_segment("HL", [hl_num, hl_num-1, "21", "1"])
hl_num += 1

text = text + seg

# construct NM (information source)
seg = segment.make_segment("NM1", ["1P", "2", payer_name, "", "", "", "", "XX",
    "1356390918"])

text = text + seg

# construct segments for each person being checked

# import csv and iterate through the entries, adding each of the following 
with open (args.input) as csvfile:
    clientreader = csv.DictReader(csvfile)
    for row in clientreader:
        first_name = row["FirstName"]
        last_name = row["LastName"]
        dob = row["DOB"]
        cin = row["CIN"]
        # construct HL segment
        seg = segment.make_segment("HL", [hl_num, hl_num-1, "22", "0"])       
        hl_num +=1
        text = text + seg
        # construct NM segment
        seg = segment.make_segment("NM1",["IL", "1", last_name.strip(),
            first_name.strip(), "",
            "", "", "MI", cin])
        text = text + seg
        # construct DMG segment
        str_dob = time.strptime(dob, "%m/%d/%Y")
        seg = segment.make_segment("DMG",["D8",time.strftime("%Y%m%d",
            str_dob)])
        text = text + seg
        # construct DTP segment
        seg = segment.make_segment("DTP",["291", "RD8",
            current_date_long+"-"+current_date_long])
        text = text + seg
        # construct EQ segment
        seg = segment.make_segment("EQ", ["30"])
        text = text + seg

# construct SE segment
# get number of segments in text string so far by counting occurrences of '~'
# and adding one
num_of_segments = text.count('~')-1
seg = segment.make_segment("SE", [num_of_segments, "0001"])

text = text + seg

# construct GE segment
seg = segment.make_segment("GE", ["1", "1"])

text = text + seg

# construct IEA segment
seg = segment.make_segment("IEA", ["1", str("%09d" % int(icn))])

text = text + seg

# increment ICD number for next 270 file creation
config.set("Interchange_Control_Number", "ICN", str(int(icn)+1))

# write back configuration file
with open('270_configuration.cfg', 'wb') as configfile:
     config.write(configfile)

# write final 270 form)
out_file.write(text)
out_file.close()

print "File created"
