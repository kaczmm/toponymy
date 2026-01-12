#a quick script for combining 2 columns
# combines left to right

def main():
    lines = []
    with open("Untitled spreadsheet - Sheet1.csv","r",encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    splitlines = [line.split(',') for line in lines]

    for pair in splitlines:
        if pair[1]=="":
            pair[1] = pair[0]
        elif pair[0]=="" and pair[1]!="":
            print("Left is missing",pair[1])

    with open("new.csv","w",encoding="utf-8-sig") as f:
        for line in splitlines: f.write(line[0]+','+line[1]+"\n")

main()