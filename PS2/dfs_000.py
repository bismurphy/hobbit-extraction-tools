###This script will extract a pair of *.DFS and *.000 files to pull out the file payload contained within.
#Place this script into the "DATA" directory, as pulled from the disc. All files extracted from the specified DFS/000 will be placed into the 'extracted'
#folder within DATA (which you will need to create). Call this with:
#'python3 dfs_000.py AUDIO` to extract AUDIO.DFS and AUDIO.000 into the 'extracted' folder.

import sys
chosen_file = sys.argv[1]



#"little endian process". Given a list of bytes, turns it into an integer, little-endian.
def lep(bytelist):
    total = 0
    for i in reversed(bytelist):
        total <<= 8
        total += i
    return total
#"friendly bytes", converts a series of bytes to a nice list of hex values
def fb(bytelist):
    return ", ".join([("0" if b < 16 else "") + hex(b)[2:].upper() for b in bytelist])
#Grabs the given number of bytes from the file. Keeps an internal pointer to track what's been parsed.
def grab(file_bytes,n):
    global file_pointer
    fetched = file_bytes[file_pointer:file_pointer + n]
    file_pointer += n
    return fetched
#From a given start index in the bytestream, returns a string, which terminates when we find a zero byte.
def getString(bytestream,start_index):
    #print("start")
    #print(start_index)
    index = start_index
    outstring = ""
    while(bytestream[index] != 0):
        outstring += chr(bytestream[index])
        index +=1
    #print("done")
    #print(index)
    if index == start_index:
        return getString(bytestream,start_index+1)
    return outstring
global file_pointer
file_pointer = 0
with open(chosen_file + '.DFS','rb') as dfsfile:
    f = dfsfile.read() #f will always hold the raw dfs file that we got
    #Process the first 20 bytes of the file, which gives overall info
    assert(grab(f,4) == bytes("SFDX",'utf-8'))
    folder_count = lep(grab(f,4))
    padding_multiple = lep(grab(f,4))
    unknown = grab(f,4)
    file_count = lep(grab(f,4))
    print(f"{folder_count = }")
    print(f"{padding_multiple = }")
    print(f"{unknown = }")
    print(fb(unknown))
    print(f"{file_count = }")
    
archive_bytes = None
with open(chosen_file + '.000','rb') as arch_file:
    archive_bytes = arch_file.read()
print("-------")
#Header told us how many folders exist. Go through each and gather its data
#However i'm pretty sure there's always only 1 folder :)
for i in range(folder_count):
    name_offset = lep(grab(f,4)) - 1
    unknown2 = grab(f,4)
    unknown3 = grab(f,4)
    dir_offset = grab(f,4)
    filename_dir_offset = lep(grab(f,4))
    unknown4 = grab(f,4)
    print(f"{name_offset = }")
    print(f"{unknown2 = }")
    print(fb(unknown2))
    print(f"{unknown3 = }")
    print(fb(unknown3))
    print(f"{dir_offset = }")
    print(f"{filename_dir_offset = }")
    print(f"{unknown4 = }")
    print(fb(unknown4))
    print(file_pointer)
    print("Starting files")
    #within the folder, iterate across the files (though note this is a bit wrong)
    for file in range(file_count):
        #print("FILE:")
        name_part_1_offset = lep(grab(f,4))
        #print(f"{name_part_1_offset = }")
        name_part_2_offset = lep(grab(f,4))
        #print(f"{name_part_2_offset = }")
        #print(hex(filename_dir_offset + name_part_1_offset))
        #print(hex(filename_dir_offset + name_part_2_offset))

        name_part_1 = getString(f,filename_dir_offset + name_part_1_offset)
        name_part_2 = getString(f,filename_dir_offset + name_part_2_offset)
        #print(name_part_1)
        #print(name_part_2)
        print("----")
        name_part_3_bytes = grab(f,4)
        if lep(name_part_3_bytes) != 0:
            name_part_3 = getString(f,filename_dir_offset + lep(name_part_3_bytes))
        else:
            name_part_3 = ""
        unknown5 = grab(f,4) #always 1b
        name_part_4 = getString(f,filename_dir_offset + lep(unknown5))
        file_offset = lep(grab(f,4))
        file_len = lep(grab(f,4))
        filename = name_part_3 + name_part_1 + name_part_2 + name_part_4
        print(filename)
        extracted_bytes = archive_bytes[file_offset:file_offset + file_len]
        with open('extracted/' + filename,'wb') as writer_file:
            writer_file.write(extracted_bytes)
##        print(f"{file_offset = }")
##        print(f"{file_len = }")
        
print("Script complete. Final value of indexer:")
print(file_pointer)
        
