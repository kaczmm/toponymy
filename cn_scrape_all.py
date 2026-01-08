# Python script which scrapes the landed_titles file and extracts all the cultural title names for ALL cultures

# needed to search files
import os
import re

def main():
    cultures = []
	# 1. get a list of cultures
    with open("00_landed_titles.txt","r",encoding="utf-8-sig") as f:
        for line in f:
            if "name_list_" in line:
                # example:
                # name_list_portuguese = cn_balboa #comment
                cultures.append(re.search("name_list_[a-z]*", line).group(0)[10:])
                
    # remove duplicates
    cultures = set(cultures)
    
    # scrape the toponymy master csv
    tlines = []
    with open("toponymy.csv","r",encoding="utf-8-sig") as f:
        tlines = f.readlines()
    master_csv = []
    for line in tlines:
        master_csv.append(line.strip().split(','))
    master_csv[0] = [l.lower() for l in master_csv[0]] # first row - culture names
    print("csv scraped successfully")


    # a list of dictionaries? one for each culture?
    dictionaries = []
    temp_list = []

    # do the same for every culture
    for c in cultures:
        temp_list = csv_scrape(master_csv,c)
        if len(temp_list)>2:
            dictionaries.append(csv_scrape(master_csv,c))

    for i in range(len(master_csv)):
        for d in dictionaries:
            culture_pos = int(d["culture_pos"])
            if culture_pos < 1: # need to append new column
                if i==0: master_csv[i].append(d["culture_name"]) # column heading
                else:
                    if master_csv[i][0] in d: master_csv[i].append(d[master_csv[i][0]])
                    else: master_csv[i].append("") # to keep the right number of commas
            else:
                if master_csv[i][0] in d:
                    if master_csv[i][culture_pos] == d[master_csv[i][0]]: # if it's the same, skip
                        continue
                    elif master_csv[i][culture_pos] == "" or master_csv[i][culture_pos] == None: # if it's blank, replace
                        master_csv[i][culture_pos] = d[master_csv[i][0]]
                    else:
                        master_csv[i][culture_pos] += "/"+d[master_csv[i][0]] # if it's not blank and it's different, write a slash and add


	# 5. output the table as a csv file
    csv_name = "new_toponymy.csv"
    with open(csv_name,"w",encoding="utf-8-sig") as f:
        for i in range(len(master_csv)):
            for j in range(len(master_csv[i])):
                f.write(master_csv[i][j]+",")
            f.write("\n")
        
    print("Done!")


# returns a dictionary which pairs titles with cnames
# ALSO includes 1 entry that pairs "position" with the column number of that culture
def csv_scrape(csv, culture):
    list_of_pairs = []
    count = 0

    # find the column for our target culture
    if culture in csv[0]:
        culture_pos = csv[0].index(culture)
        #print("Culture <",culture,"> found in csv at column number", culture_pos)
    else:    
        culture_pos = -1
        #print("New culture <",culture,">") 

    # position and name added to dictionary so we can look them up later
    list_of_pairs.append(("culture_pos",culture_pos))
    list_of_pairs.append(("culture_name",culture))

	# read landed_titles and take all the lines that are either titles OR cultural name definitions for the specific culture
    prefixes = ('b_','c_','d_','k_','e_')
    titles = []
    name_list = "name_list_"+culture

    # create list of titles and cultural names
    with open("00_landed_titles.txt","r",encoding="utf-8-sig") as f:
        for line in f:
            if any(line.strip()[:2]==p for p in prefixes) or name_list in line:
                titles.append(line.strip())

	# 3. new list of pairs with only titles which have cnames
    cn = ''
    for i in range(len(titles)-1):
        if any(titles[i].strip()[:2] == p for p in prefixes):
            if i<len(titles)-1 and name_list in titles[i+1]: # and the next element is a cn...
                list_of_pairs.append((titles[i].split("=")[0].strip(),
                    titles[i+1].split("=")[1].strip())) # append the pair
    
	# 4. for every cn, search the localisation folder for the actual text
    localised_pairs = []
    for root, _, files in os.walk(r"C:\Users\matth\Documents\Paradox Interactive\Crusader Kings III\mod\more bookmarks 1.17.1 pre-AUH\localization"):
        for filename in files:
            with open(os.path.join(root,filename),"r",encoding="utf-8-sig") as f:
                if not filename.endswith((".yml", ".yaml")):
                    continue
                if not "cn" in filename: # cn loc should have cn in the filename
                    continue
                for line in f:
                    for pair in list_of_pairs:
                        if line != None and line.strip() != "":
                            if line.strip()[0] != "l" and line.strip()[0] != "#":
                                # split line into [cn_tag,cn,empty string]
                                good_line = line.split(r'"')

                                if str(pair[1])+":" in good_line[0] and "_adj:" not in good_line[0]:
                                    localised_pairs.append((str(pair[0]),good_line[1]))
                                    count+=1

    for root, _, files in os.walk(r"C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game\localization\english"):
        for filename in files:
            with open(os.path.join(root,filename),"r",encoding="utf-8-sig") as f:
                if not filename.endswith((".yml", ".yaml")):
                    continue
                if not "cultural_name" in filename: # cn loc should have cn in the filename
                    continue
                for line in f:
                    for pair in list_of_pairs:
                        if line != None and line.strip() != "":
                            if line.strip()[0] != "l" and line.strip()[0] != "#":
                                # split line into [cn_tag,cn,empty string]
                                good_line = line.split(r'"')

                                if str(pair[1])+":" in good_line[0] and "_adj:" not in good_line[0]:
                                    localised_pairs.append((str(pair[0]),good_line[1]))
                                    count+=1

    if count==0:
        print(culture,"has NO titles!")
        localised_pairs = []
    elif count <3:
        print(culture,"has <3 titles!")
        print("...",localised_pairs)

    localised_pairs.append(list_of_pairs[0])
    localised_pairs.append(list_of_pairs[1])

    return dict(localised_pairs)


if __name__ == '__main__':
    main()