<h2>Toponymy project by Matt</h2>
A universal cultural names project for dynamic place names across various paradox interactive games. "Dynamic" or "cultural name" means that France calls Alsace by a French name, while Germany would call it Elsass.


<h3>Contents:</h3>


*00_landed_titles.txt*
- landed_titles file from More Bookmarks+ for CK3 (I should really rename this to ck3_titles or something)
- used as input for the various CK3 scripts


*ck3_fix_titles.py*
- Python script that searches for names which have been changed from vanilla CK3


*ck3_script.py*
- Python script that reads toponymy.csv and adds cultural names to the titles file. Also generates a localisation file.


*cn_scrape.py*
- Scrapes the landed_titles file and localization folder for cultural names already in the game, then adds them to a 1:1 csv so it can be added to the master toponymy csv.


*toponymy.csv*
- The master spreadsheet of cultural names and titles. Hosted in Google Cloud and only put in here as a placeholder
- Should be updated before running any of the scripts


<h3>Planned:</h3>

- Create a scrubbed version of landed_titles:-this is so that the only definitions in here are the ones I'm aware of-First, I need a generalise the scrape script so it scrapes ALL cn definitions (read the files then throw the rest into a method - pass everything for each culture to the method)
- Generalise the scripts. Instead of only doing the operation for 1 culture, the process should be:-Read the clean landed_titles-Read the master toponymy spreadsheet-For each culture defined in the Toponymy spreadsheet, add in the cultural names