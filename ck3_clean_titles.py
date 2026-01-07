# Python script which creates a clean landed_titles (ie no cultural_names blocks and no "name_list" lines)

def main():
    titles = []
    # read the whole file into a list
    with open("00_landed_titles.txt","r",encoding="utf-8-sig") as f:
        for line in f:
            if any(line.strip()[:2]==p for p in prefixes) or name_list in line:
                titles.append(line.strip())

	# line contains "cultural_names" we will traverse
    cname_start = -1
    
    # write a new file that excludes 
    with open("CLEAN_landed_titles.txt","w",encoding="utf-8-sig") as f:
        for i in range(len(titles)):
            if "cultural_names" in titles[i] and "{" in titles[i]: # cultural names block!
                print("Found cultural names block")
                cname_start = i
                for j in range(cname_start,len(titles)):
                    if "}" in titles[j]:
                        i = j
                        print("...found block close")
                        break
            else:
                f.write(titles[i]+"\n")


if __name__ == '__main__':
    main()