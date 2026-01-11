# CK3 Toponymy Script
#  1. load landed_titles.txt and make a list of its lines
#  2. load the csv and get A) 2d list of cnames B) list of sets (index,culture)
#  3. go through each culture (in list of sets) and create a list of dictionairies
#  4. go through each line in landed_titles and check if it has a cname that can be updated
#  5. export the result as a new landed_titles file

def main():
    titles = []
    toponymy = []
    cultures = []
    new_titles = []
    dictionairies = []
    qp = [] # quickpaste - temp store for lists so i dont have to write long lines

    #  1. load landed_titles.txt and make a list of its lines
    with open("00_landed_titles.txt","r",encoding="utf-8-sig") as f:
        titles = f.readlines()

    #  2. load the csv and get A) 2d list of cnames B) list of sets (index,culture)
    with open("Toponymy Project - output.csv","r",encoding="utf-8-sig") as f:
        # cultures = [(index,"name"),(index,"name"),..]
        qp = f.readline().split(',')
        reserved = ['ck3','sanitised','desc','iotised','?']
        for i in range(len(qp)):
            qp[i] = qp[i].replace("\n","").lower()
            if not any(r in qp[i] for r in reserved):
                if qp[i]!="": cultures.append((int(i),qp[i].lower().strip()))

        for line in f.readlines():
            toponymy.append(line.split(','))

    #  3. go through each culture (in list of sets) and create a list of dictionairies
    for c in cultures:
        dictionairies.append(csv_scrape(titles,toponymy,c))

    #  4. go through each line in landed_titles and check if it has a cname that can be updated
    new_titles = titles
    for d in dictionairies:
        new_titles = culture_filter(new_titles,d)

    # remember where opening brackets are (-1 means not found)
    title_start = -1
    cn_start = -1
    last_space = -1 # makes the block look nicer

    # stuff for keeping track of title name and ws
    title = ""
    ws = ""

    #  5. export the result as a new landed_titles file
    with open("NEW_landed_titles.txt","w",encoding="utf-8-sig") as f:
        f.writelines(new_titles)

    #  6. create localisation files
    for d in dictionairies:
        if len(list(d.items()))>3:
            gen_localisation(d)

    #  7. create a loc replace for the sanitised title names which should be fixed/changed
    
    print("Done!\n")

# takes a dictionary and creates a localisation file
def gen_localisation(d):
    culture = d["culture_name"]

    # create a localisation file
    loc = ['l_english:\n', ' # '+culture+' cultural names, from toponymy project\n']
    for (t,c) in list(d.items()):
        if t!="culture_pos" and t!="culture_name":
            loc.append(' cn_'+t+'_'+culture+':0 "'+c+'"\n')
            loc.append(' cn_'+t+'_'+culture+'_adj:0 "'+c+'"\n')

    # then just write this to a new file
    loc_file_name = "zztp_cn_"+culture+"_l_english.yml"
    with open(loc_file_name,"w",encoding="utf-8-sig") as f:
        f.writelines(loc)

# method that goes through a titles file and inserts cultural names for 1 culture
def culture_filter(titles,d):
    ts = titles
    culture = d["culture_name"] # name of the culture being worked on
    #culture_pos = int(d["culture_pos"]) # culture column position in toponymy
    title_start = -1 # start of title block
    nice_spot = -1
    cn_start = -1 # start of cname block
    t = "" # current title being looked at
    ws = "" # placeholder for intentation whitespace
    i = 0 # line pointer

    name_list = "name_list_"+culture

    print("Checking",culture)
    while i < len(ts):
        i += 1
        if i >= len(ts):
            print("...done", culture)
            break
        # check if title
        elif is_title(ts[i]):
            t = title_strip(ts[i])

            # check if title has a cname defined for this culture
            #  remember d = {("title","name"), ...}
            #  dictionairies are (key,value) lists
            if t in d.keys() and d[t]!=None and d[t]!="" and d[t]!="None":
                #print("Found definable title:",t)
                
                # Bookmark this line so we can return later if needed
                title_start = i
                # Remember indentation for to add a line later
                ws = lws(ts[i]) + "\t"

                # continue until we find a cname block or another title
                cn_start = -1
                #print("..looking for cname block..")
                for j in range(i,len(ts)):
                    line = ts[j].strip()

                    # cname block
                    if is_cname_block(line):
                        #print("....found cname block at line",j)
                        cn_start = j
                    # found a cname definition
                    elif is_cname(line,culture):
                        #print("....found existing cname:",line.strip())
                        if not t in ts[j]: # ie NOT one of my generated ts (always of the form cn_b_title_culture)
                            ts[j] = (lws(ts[j]) + name_list + " = " + "cn_"+t+"_"+culture + " # " + ts[j].strip().split("=")[1].strip() +"\n")
                        i = j
                        cn_start = -2 # special flag to show we already added applied the new cname
                        break
                    # cname block was found and we reached the next title
                    elif cn_start > -1 and is_title(line):
                        #print("....cname block was found and we reached the next title",j)
                        i = j
                        break
                    elif "color = {" in line:
                        nice_spot = j+1 # nice clean spot to insert cname block
                        #print("found a nice spot for",t)

                # if it has a cname block but no cname, add to the cname block
                if cn_start > -1:
                    ts.insert(cn_start+1, ws+"\t"+name_list+" = "+"cn_"+t+"_"+culture+"\n")
                    #print("Added cname to existing cname block")
                
                # elif no cname block > make one and add to it
                elif cn_start == -1:
                    ts.insert(nice_spot, ws+r"cultural_names = {\n")
                    ts.insert(nice_spot+1, ws+"\t"+name_list+" = "+"cn_"+t+"_"+culture+"\n")
                    ts.insert(nice_spot+2, ws+"}\n")
                    ts.insert(nice_spot+3, "\n")

                # elif cn_start == -2: we don't need to do anything
    #done
    return ts

def title_strip(line):
    title = ""

    # example line:
    #  b_montereau = {
    title = line.split(r"=")[0].strip()

    return title

# takes a line of text and tells you if contains a title declaration
def is_title(line):
    if any(line.strip()[:2]==p for p in ('b_','c_','d_','k_','e_')) and "{" in line:
        return True
    return False

def is_cname_block(line):
    if "cultural_names" in line and "=" in line and "{" in line:
        return True
    return False

def is_cname(line,culture):
    if "name_list_"+culture in line and "=" in line:
        return True
    return False

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

# titles: list of lines in 00_landed_titles.txt
# csv: list of rows in toponymy csv
# pair: a pair containing (pos, name) of a culture in csv
# returns a dictionary for the culture provided
def csv_scrape(titles, csv, pair):
    list_of_pairs = []
    count = 0
    culture_pos = int(pair[0])
    culture = pair[1]

	# go through CSV and grab anything for this culture
    for row in csv:
        row[culture_pos] = row[culture_pos].replace("\n","").strip()
        if row[0]!= "" and row[culture_pos]!="" and row[culture_pos]!=None:
            if "/" in row[culture_pos]: # avoid collisions
                list_of_pairs.append((row[0], row[culture_pos].split(r"/")[0].strip()))
            else:
                list_of_pairs.append((row[0], row[culture_pos]))

    if len(list_of_pairs) < 3:
        print("..",len(list_of_pairs),"definitions for",culture)
        for pair in list_of_pairs:
            print("....",pair)

    # position and name added to dictionary so we can look them up later
    list_of_pairs.append(("culture_pos",culture_pos))
    list_of_pairs.append(("culture_name",culture))


    return dict(list_of_pairs)


if __name__ == '__main__':
    main()