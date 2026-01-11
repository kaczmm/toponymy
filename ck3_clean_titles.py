# Python script which creates a clean landed_titles (ie no cultural_names blocks and no "name_list" lines)

def main():
    titles = []
    # read the whole file into a list
    with open("00_landed_titles.txt","r",encoding="utf-8-sig") as f:
        titles = f.readlines()

	# line contains "cultural_names" we will traverse
    cname_start = -1
    i = 0
    
    # write a new file that excludes 
    with open("CLEAN_landed_titles.txt","w",encoding="utf-8-sig") as f:
        while i<len(titles):
            if "cultural_names" in titles[i] and "{" in titles[i]: # cultural names block!
                print("Found cultural names block")
                cname_start = i
                for j in range(cname_start,len(titles)):
                    print('...Line...',titles[j].strip())
                    if "}" in titles[j]:
                        i = j
                        print("......found block close")
                        break
            else:
                f.write(titles[i])
            i+=1
    print("Done!")


if __name__ == '__main__':
    main()