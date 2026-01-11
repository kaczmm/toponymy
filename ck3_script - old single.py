# CK3 Toponymy Script
#  1. load the csv and get a dictionary of titles:cn
#  2. insert name list / cname blocks wherever needed (need to check if there's already a cname for the culture in titles)	
#  3. make a localisation file with all the new localisation tags...

def main():
    # Go thr
        
    # output mode: controls which messages get printed
    outputMode = 0
    print("Choose an output mode: \n[0] All log output \n[1] New localisation only \n[2] Localisation conflicts only")
    try:
        outputMode = int(input())
    except:
        print("Error! Invalid option")
        input()
        exit()

    # scrape the csv
    with open("toponymy.csv","r",encoding="utf-8-sig") as f:
        lines = f.readlines()
        T = len(lines)
    csv = []
    for line in lines:
        csv.append(line.strip().split(','))
    csv[0] = [l.lower() for l in csv[0]]
    if outputMode==0: print("csv scraped successfully")

    # find the column for our target culture
    culture_pos = -1
    culture_pos = csv[0].index(culture)
    if culture_pos == -1:
        print("Fatal error: no such culture in toponymy csv")
        input()
        exit()
    if outputMode==0: print("Culture <",culture,"> found in csv at column number", culture_pos)

    # build a dictionary from the csv
    list_of_pairs = []
    for i in range(1,T): # skip line 0 (column labels)
        # csv[i][0] must be defined (ie this row is a ck3 title)
        # csv[i][culture_pos] must be defined (ie the culture must have a name for this title)
        # csv[i][culture_pos] must not be the same as csv[i][1] (ie the sanitised title; it must have a distinct cultural name)
        if csv[i][0]!="" and csv[i][culture_pos]!="" and csv[i][culture_pos]!=csv[i][1]:
            list_of_pairs.append( (csv[i][0],csv[i][culture_pos]) )
    toponymy = dict(list_of_pairs)
    if outputMode==0: print("dictionary built successfully")

    # the array of lines of text from landed_titles.txt
    with open("00_landed_titles.txt","r",encoding="utf-8-sig") as f:
        titles = f.readlines()
    if outputMode==0: print("00_landed_titles.txt read successfully")

    # line pointer
    i = 0

    # remember where opening brackets are (-1 means not found)
    title_start = -1
    cn_start = -1

    # stuff for keeping track of title name and ws
    title = ""
    ws = ""
    
    # name list name - used for checking definitions
    name_list = "name_list_"+culture # ie name_list_polish

    if outputMode==0: print("Looking for titles...")
    while (i < len(titles)):
        # check if line is a title
        i+=1
        if (i == len(titles)):
            if outputMode==0: print("Finished reading titles! Last read title was:",title)
            break
        line = titles[i].strip()
        if line[0:2] in ['e_','k_','d_','c_','b_']:
            # title name is from start of line until =
            # strip method removes leading and trailing ws
            title = line.split("=")[0].strip()
            
            # check if title has a cultural name
            if title in toponymy:
                if outputMode==0: print("Found definable title:",title)
                # remember this line number
                title_start = i
                
                # copy the indentation plus one tab
                ws = lws(titles[i]) + "\t"
                
                # keep going until either "cultural_names" OR another title
                # -1 indicates none found
                cn_start = -1
                if outputMode==0: print("Looking for cultural_names block...")
                while True:
                    i+=1
                    line = titles[i].strip()
                    
                    # Found cultural_names block
                    if line[:14] == "cultural_names":
                        if outputMode==0: print("  Found cultural_names block at line",i)
                        cn_start = i
                    # Found next title -> no cn block
                    elif line[0:2] in ['e_','k_','d_','c_','b_']:
                        if outputMode==0: print("    Found next title",titles[i].split("=")[0].strip(),"at line",i)
                        break
                    # Found cn definition for this culture already
                    elif name_list in line:
                        if outputMode!=1: print("    Found existing definition",line,"at line",i)
                        cn_start = -2 # special value to show definition exists (do nothing)
                        break
                    elif i >= len(titles):
                        if outputMode==0: print("    Reached end of titles, nothing found.")
                        break
                i = title_start

                # if it has a CN block, add to it
                if cn_start > -1:
                    titles.insert(cn_start+1, ws+"\tname_list_"+culture+" = "+"cn_"+title+"_"+culture+"\n")
                    i = cn_start+1 #skip the new lines
                    if outputMode!=2: print("Found cn block and added definition for",title,"-",toponymy[title])

                # if it doesn't have a CN block, make one and add to it
                # Add a line directly underneath cn_start
                elif cn_start == -1:
                    titles.insert(title_start+1, ws+"cultural_names = {\n")
                    titles.insert(title_start+2, ws+"\tname_list_"+culture+" = "+"cn_"+title+"_"+culture+"\n")
                    titles.insert(title_start+3, ws+"}\n")
                    titles.insert(title_start+4, "\n")
                    i = title_start+4 #skip the new lines and close bracket
                    if outputMode!=2: print("Added new cn block and definition for",title,"-",toponymy[title])
                
                else:
                    i = title_start
                    if outputMode==0: print("Got lost, nothing found or added")
                    
                    
    # write the new 00_landed_titles
    with open("zz_00_landed_titles.txt","w",encoding="utf-8-sig") as f:
        f.writelines(titles)
    
    # create a localisation file
    loc = ['l_english:\n', ' # '+culture+' cultural names, from toponymy project\n']
    for (t,c) in list_of_pairs:
        loc.append(' cn_'+t+'_'+culture+':0 "'+c+'"\n')
        loc.append(' cn_'+t+'_'+culture+'_adj:0 "'+c+'"\n')

    # then just write this to a new file
    loc_file_name = "zz_cn_"+culture+"_l_english.yml"
    with open(loc_file_name,"w",encoding="utf-8-sig") as f:
        f.writelines(loc)

    print("Done!\n")


# method for extracting exact lefthand whitespace
def lws(input_string):
	ws = ""
	i = 0
	for i in range(len(input_string)):
		if input_string[i] == " ":
			ws += " "
		elif input_string[i] == "\t":
			ws += "\t"
			i+=1
		else:
			break
	return ws


if __name__ == '__main__':
    main()