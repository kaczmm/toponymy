# Python script which scrapes the landed_titles file and extracts all the cultural title names for a culture

# needed to search files
import os

def main():
	# 1. culture selection (because I don't really care about every single culture)
    culture = "polish" # default for testing
    
    # prompt for culture name
    print("Enter culture name:")
    try:
        culture = input().lower()
    except:
        print("Error! Please enter a valid culture name")
        input()
        exit()
    name_list = "name_list_"+culture
    
    # scrape the toponymy master csv
    tlines = []
    with open("toponymy.csv","r",encoding="utf-8-sig") as f:
        tlines = f.readlines()
    csv = []
    for line in tlines:
        csv.append(line.strip().split(','))
    csv[0] = [l.lower() for l in csv[0]]
    print("csv scraped successfully")

    # find the column for our target culture
    culture_pos = -1
    culture_pos = csv[0].index(culture)
    if culture_pos == -1:
        print("Fatal error: no such culture in toponymy csv")
        input()
        exit()
    print("Culture <",culture,"> found in csv at column number", culture_pos)

	# 2. read landed_titles and take all the lines that are either titles OR cultural name definitions for the specific culture
    prefixes = ('b_','c_','d_','k_','e_')
    titles = []

    # create list of titles and cultural names
    with open("00_landed_titles.txt","r",encoding="utf-8-sig") as f:
        for line in f:
            if any(line.strip()[:2]==p for p in prefixes) or name_list in line:
                titles.append(line.strip())

	# 3. new list of pairs with only titles which have cnames
    list_of_pairs = []
    cn = ''
    for i in range(len(titles)-1):
        if any(titles[i].strip()[:2] == p for p in prefixes):
            if i<len(titles)-1 and name_list in titles[i+1]: # and the next element is a cn...
                list_of_pairs.append((titles[i].split("=")[0].strip(),
                    titles[i+1].split("=")[1].strip())) # append the pair
    
	# 4. for every cn, search the localisation folder for the actual text
    localised_pairs = []
    print("Reading files...")
    for root, _, files in os.walk(r"C:\Users\matth\Documents\Paradox Interactive\Crusader Kings III\mod\more bookmarks 1.17.1 pre-AUH\localization"):
        for filename in files:
            with open(os.path.join(root,filename),"r",encoding="utf-8-sig") as f:
                if not filename.endswith((".yml", ".yaml")):
                    continue
                if not "cn" in filename: # cn loc should have cn in the filename
                    continue
                #print("reading",filename,"...")
                for line in f:
                    for pair in list_of_pairs:
                        if line != None and line.strip() != "":
                            if line.strip()[0] != "l" and line.strip()[0] != "#":
                                # split line into [cn_tag,cn,empty string]
                                good_line = line.split(r'"')
                                if pair[1]+":" in good_line[0] and "_adj:" not in good_line[0]:
                                    localised_pairs.append((pair[0],good_line[1]))

    loc = dict(localised_pairs)
    for row in csv:
        if row[0] in loc: row[culture_pos] = loc[row[0]]

	# 5. output the table as a csv file
    csv_name = "toponymy_"+culture+".csv"
    with open(csv_name,"w",encoding="utf-8-sig") as f:
        for i in range(len(csv)):
            f.write(csv[i][0]+","+csv[i][culture_pos]+"\n")
        
    print("Done!")


if __name__ == '__main__':
    main()