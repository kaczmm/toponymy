# script which looks through the toponymy master csv and makes a loc override file
# specifically for CK3

# used to normalise accented letters for comparison
from unidecode import unidecode
# used for removing underscores
from re import sub


def main():
    # import csv file as a list of lines
    print("Reading toponymy.csv...")
    with open("toponymy.csv","r",encoding="utf-8-sig") as f:
        lines = f.readlines()
        T = len(lines)
    csv = []
    for line in lines:
        csv.append(line.strip().split(','))
    print("...done")
    
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
    print("Writing new localisation file...")
    loc = ['l_english:\n']
    for (t,c) in list_of_pairs:
        loc.append(' '+t+':0 "'+c+'"\n')
        loc.append(' '+t+'_adj:0 "'+demonym(c)+'"\n')

    # then just write this to a new file
    loc_file_name = "zzz_titles_replace_l_english.yml"
    with open(loc_file_name,"w",encoding="utf-8-sig") as f:
        f.writelines(loc)
        
    print("...done.")
    
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
    cl = string_left.strip().lower()
    cr = string_right.strip().lower()
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


if __name__ == '__main__':
    main()