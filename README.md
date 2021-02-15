# nhentai-dl



### Korewa Nandesuka

This tool downloads doujins from nhentai. Unlike the other nhentai downloaders that download based on what you search for (title, tag, author, etc.), this one is based on ID. This makes it a more suitable tool for archivists.  However, you can still filter out doujins based on their tags. 



One other feature I would like to mention is that a tag file is added to each doujin. This allow for easy adding to Lanraragi with the help of the Hdoujin plugin. The setup I use is set the finished directory to your Lanraragi source directory and toggle Hdoujin as an auto-plugin. Then, your Lanraragi server will slowly grow in size with nicely tagged doujins (saving you lots of manual labor). 



### Doesn't being ID based mean it will have a lot of misses?

First of all, when I say misses, I mean fetching a specific page from nhentai, searching the tags, and finding out its not what you want. To prevent this problem for an ID based approach, there is an index file that contains all encountered doujins so far. When exploring a specific doujin ID, the first place searched is your index file. If it is not the doujin you want, the program moves onto the next ID. No request is made to the nhentai servers. However, if you encounter an ID not in your index file, a request will be made to nhentai to fetch the doujin information. This information is then added to the index file so that if you search for that ID again, you will have all information locally and no request will have to be made to nhentai unless it fits your criteria.



### Requirements

OS: Currently built for Windows

Python 3

Some dependencies (if not already installed):

* requests

* re

* urllib

* os

* shutil

* time

* html



### Usage

Just run the Downloader.py file. It will then prompt you for your criteria and then start downloading.



### Customization

By default, all doujins will start off downloading in "temp" dir within the same directory as the downloader. When finished, they are moved to "finished" dir and then zipped within that dir. You can specify absolute or relative paths to where you want the temp/finished directory to be by editing the constants at the top of the Downloader.py file. You can also change the index/archive files if you so choose. Don't mess with NH_BASE or SOURCE.
