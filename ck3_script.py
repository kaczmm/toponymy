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
    #with open("00_landed_titles.txt","r",encoding="utf-8-sig") as f:
    #    titles = f.readlines()
    with open("00_landed_titles.txt.bak","r",encoding="utf-8-sig") as f:
        titles = f.read().splitlines()

    #  2. load the csv and get A) 2d list of cnames B) list of sets (index,culture)
    with open("Toponymy Project - output.csv","r",encoding="utf-8-sig") as f:
        # cultures = [(index,"name"),(index,"name"),..]
        qp = f.readline().split(',')
        reserved = ['ck3','sanitised','desc','iotised','?']
        for i in range(len(qp)):
            qp[i] = deep_clean(qp[i]).lower()
            if not any(r in qp[i] for r in reserved):
                if qp[i]!="":
                    # culture names that are different in CK3
                    if "romanian" in qp[i].lower(): qp[i] = "vlach"
                    elif "slovak" in qp[i].lower(): qp[i] = "slovien"
                    elif "kashub" in qp[i].lower(): qp[i] = "pommeranian"
                    # duplicate cnames - ie cultures that don't have their own map cnames
                    elif "russian" in qp[i].lower():
                        cultures.append((int(i),"ilmenian"))
                        cultures.append((int(i),"great_russian"))
                    elif "ukrain" in qp[i].lower():
                        cultures.append((int(i),"severian"))
                        cultures.append((int(i),"volhynian"))
                        cultures.append((int(i),"volyn"))
                    elif "belarus" in qp[i].lower():
                        cultures.append((int(i),"byelorusian"))

                    print("cultures:",qp[i].lower())

                    cultures.append((int(i),qp[i].lower().strip()))

        for line in f.readlines():
            toponymy.append(line.split(','))

    #  3. go through each culture (in list of sets) and create a list of dictionairies
    for c in cultures:
        dictionairies.append(csv_scrape(titles,toponymy,c))

    #  4. go through each line in landed_titles and check if it has a cname that can be updated
    new_titles = titles
    for d in dictionairies:
        new_titles = culture_filter(new_titles,d)

    #  5. export the result as a new landed_titles file
    with open("00_landed_titles.txt","w",encoding="utf-8-sig") as f:
        for line in new_titles:
            f.write(line+"\n")

    #  6. create localisation files
    for d in dictionairies:
        if len(list(d.items()))>3:
            gen_localisation(d)

    #  7. create a loc replace for the sanitised title names which should be fixed/changed
    fix_titles(toponymy)

    print("Done!\n")

# takes a dictionary and creates a localisation file
def gen_localisation(d):
    culture = d["culture_name"]

    # create a localisation file
    loc = ['l_english:\n', ' # '+culture+' cultural names, from toponymy project\n']
    for (t,c) in list(d.items()):
        if t!="culture_pos" and t!="culture_name":
            loc.append(' cn_'+t+'_'+culture+':0 "'+c+'"\n')
            loc.append(' cn_'+t+'_'+culture+'_adj:0 "'+demonym(c)+'"\n')

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
    debug = False
    debug_pointer = -1

    name_list = "name_list_"+culture

    print("Checking",culture)
    while i < len(ts):
        i += 1

        if i >= len(ts):
            print("...done", culture)
            break
        elif "name_list" in ts[i]:
            continue
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
                        i = j
                        

                    # found a cname definition
                    elif is_cname(line,culture):
                        #print("....found existing cname:",line.strip())
                        if not t in ts[j]: # ie NOT one of my generated ts (always of the form cn_b_title_culture)
                            ts[j] = (lws(ts[j]) + name_list + " = " + "cn_"+t+"_"+culture + " # " + ts[j].strip().split("=")[1].strip())
                        i = j
                        cn_start = -2 # special flag to show we already added applied the new cname
                        #if debug: print("b")
                        break
                    # cname block was found and we reached the next title
                    elif is_title(line) and t not in line:
                        #print("....cname block was found and we reached the next title",j)
                        #if culture=="irish": print("aborted:",j," content:",line)
                        i = j
                        #if debug: print("c")
                        break
                    elif "color = {" in line:
                        nice_spot = j+1 # nice clean spot to insert cname block
                        #print("found a nice spot for",t)
                        #if debug: print("d")

                # if it has a cname block but no cname, add to the cname block
                if cn_start > -1:
                    ts.insert(cn_start+1, ws+"\t"+name_list+" = "+"cn_"+t+"_"+culture)
                    #print("Added cname to existing cname block")
                
                # elif no cname block > make one and add to it
                elif cn_start == -1:
                    #if debug: print("printed a new block")
                    ts.insert(nice_spot, ws+"cultural_names = {")
                    ts.insert(nice_spot+1, ws+"\t"+name_list+" = "+"cn_"+t+"_"+culture)
                    ts.insert(nice_spot+2, ws+"}")
                    i+=2

                # elif cn_start == -2: we don't need to do anything

    return ts
    
def fix_titles(csv):
    # make new empty list which will be for the replacement loc
    # list of pairs: [(title, new_name), ...]
    list_of_pairs = []
    score = 0
    
    # remove the first row, which is just the labels
    csv.pop(0)
    
    # iterate through each line and compare title_name column w sanitised_name column
    print("Searching for name changes...")
    for row in csv:
        if fuzzy_compare(row[0][2:],row[1])>0:
            print(".....Found one:",row[0],"is called",row[1])
            list_of_pairs.append((row[0],row[1]))
    print("Done searching.\n")
    
    # iterate through the pair list and write it all
    print("Writing new localisation replace file...")
    loc = ['l_english:']
    for (t,c) in list_of_pairs:
        loc.append(' '+t+':0 "'+c)
        loc.append(' '+t+'_adj:0 "'+demonym(c))

    # then just write this to a new file
    loc_file_name = "zztp_titles_replace_l_english.yml"
    with open(loc_file_name,"w",encoding="utf-8-sig") as f:
        for line in loc: f.write(line+"\n")
        
# method which compares two strings and returns an int "number of differences"
#  -removes whitespace and accents, changes everything to lowercase
def fuzzy_compare(string_left, string_right):
    # initial check to catch None strings
    if string_left == None or string_right == None:
        return 0
    # check for empty strings - can't put this with None check bc comparing None can crash
    if string_left == '' or string_right == '':
        return 0

    # remove any spaces, hyphens, underscores, change accented letters to non-accented
    cl = deep_clean(string_left).lower()
    cr = deep_clean(string_right).lower()
    cl = cl.replace(' ', '').replace('-', '').replace('_', '')
    cr = cr.replace(' ', '').replace('-', '').replace('_', '')
    
    short_len = 0
    count = 0
    
    # find which string is shorter, to prevent index oob
    if len(cl)<len(cr): short_len = len(cl)
    else: short_len = len(cr)
    if short_len > 7: short_len = 7 # don't waste time on long ones
    
    # count differences
    for i in range(short_len):
        if cl[i] != cr[i]: count += 1
    
    return count

def deep_clean(text):
    return text.strip().replace('\n', '').replace('\t', '').strip()
    
# Method which guesses the demonym for a placename
def demonym(name):
    dem = name # start with name
    
    # final and -> ish (ie England->English)
    if dem[-3:] == "and": return dem[:-3] + "ish"
    
    # final ndy -> n (Normandy->Norman)
    if dem[-3:] == "ndy": return dem[:-3] + "n"
    
    # final ny -> n (Germany->German)
    if dem[-2:] == "ny": return dem[:-2] + "n"
    
    # final nia -> n (Occitania->Occitan)
    if dem[-3:] == "nia": return dem[:-3] + "n"
    
    # final an -> anian (Iran->Iranian) -- doesn't work with most placenames
    
    # final ll -> ller (Whitehall->Whitehaller)
    if dem[-2:] == "ll": return dem[:-2] + "ller"
    
    # final rg -> rgish (Luxembourgish)
    if dem[-2:] == "rg": return dem[:-2] + "rgish"
    
    # final io -> ian (Alencio->Alencian)
    if dem[-2:] == "io": return dem[:-2] + "ian"
    
    # final a -> an (ie Mercia->Mercian)
    if dem[-1:] == "a": return dem[:-1] + "an"
    
    # final e -> ian (ie Hwicce->Hwiccian)
    if dem[-1:] == "e": return dem[:-1] + "ian"
    
    # final y -> ian (Italy->Italian)
    if dem[-1:] == "y": return dem[:-1] + "ian"
    
    # final i -> no change (ie Ashanti->Ashanti)
    if dem[-1:] == "i": return dem
    
    # final o -> an (Gnyozdovo->Gnyozdovian)
    if dem[-1:] == "o": return dem[:-1] + "an"
    
    return dem

def title_strip(line):
    title = ""

    # example line:
    #  b_montereau = {
    title = line.split(r"=")[0].strip()

    return title

# takes a line of text and tells you if contains a title declaration
def is_title(line):
    if any(line.strip()[:2]==p for p in ('b_','c_','d_','k_','e_')) and line!="" and line!="\n":
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
        row[culture_pos] = deep_clean(row[culture_pos])
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