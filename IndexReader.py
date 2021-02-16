'''
'
' class Doujin()
'
' Description :
'
'    A doujin object that can store all relevant information
'    about a doujin. 
'
'''
class Doujin():
  def __init__(self, source=None, URL=None, ID=None, pages=None, title=None, tags=None):
    self.source = source
    self.URL = URL
    self.ID = str(ID)
    self.pages = str(pages)
    self.title = title
    self.tags = tags

  #Converts information into standardized text format
  def format(self):

#   doujinText = "{\n"
#   doujinText += "  \"source\": \"" + self.source + "\",\n"
#   doujinText += "  \"id\": \"" + self.ID + "\",\n"
#   doujinText += "  \"url\": \"" + self.URL + "\",\n"
#   doujinText += "  \"title\": \"" + self.title + "\",\n"
#   doujinText += "  \"pages\": \"" + self.pages + "\",\n"
#   doujinText += "  \"tags\": \"" + listToCommaString(self.tags) + "\"\n"
#   doujinText += "}"
    doujinText =  "BEGIN\n"
    doujinText += "SOURCE:" + self.source                  + "\n"
    doujinText += "ID:"     + self.ID                      + "\n"
    doujinText += "URL:"    + self.URL                     + "\n"
    doujinText += "TITLE:"  + self.title                   + "\n"
    doujinText += "PAGES:"  + self.pages                   + "\n"
    doujinText += "TAGS:"   + listToCommaString(self.tags) + "\n"
    doujinText += "END"
    return doujinText

  def setSource(self, source):
    self.source = source

  def setURL(self, URL):
    self.URL = URL

  def setID(self, ID):
    self.ID = str(ID)

  def setPages(self, pages):
    self.pages = str(pages)

  def setTitle(self, title):
    self.title = title

  def setTags(self, tags):
    self.tags = tags

'''
'
' def listToCommaString(l)
'
' Paramaters   : l      : List
'
' Return Value : string : List in string format
'
' Description  :
'
'   Takes a generic list and converts each element into a string.
'   These strings are concatenated together to create a comma separated
'   list.
'
'''
def listToCommaString(l):
  s = ""
  for i in range(0, len(l)):
    if (len(l[i].strip()) == 0):
      continue
    else:
      if (len(s) == 0):
        s += str(l[i])
      else:
        s += "," + str(l[i])

  return s

'''
'
' def commaStringToList
'
' Paramaters   : s    : string
'
' Return Value : list : string converted to list
'
' Description  :
'
'    Takes a comma separated string and converts it into
'    a list with the comma as a delimiter. Removed any unnecessary
'    whitespace.
'
'''
def commaStringToList(s):
  s = s.strip()
  l = s.split(",")
  for i in range(0, len(l)):
    l[i] = l[i].strip()

  return l

'''
'
' def readIndex()
'
' Parameters   : none
'
' Return Value : Doujin list
'
' Description  :
'
'    Reads the "index.txt" file in current directory and
'    converts each doujin entry into a doujin object with
'    a source, URL, ID, tags, title, and page amount.
'    Relies on index.txt not being messed with by the unwise.
'
'''
def readIndex(indexName):
  try:
    open(indexName, "r+").close()
  except IOError:
    print("No " + indexName + " file found. Creating new one.")
    open(indexName, "w+").close()

  f = open(indexName, "r+")
  
  doujinDict = {}
  newDoujin = Doujin()

  lineFeed = f.readline()
  while (lineFeed != ""):
      if (lineFeed[:5] == "BEGIN"):
        newDoujin = Doujin()
      if (lineFeed[:6] == "SOURCE"):
        newSource = lineFeed[7:]
        newSource = newSource.strip()
        newDoujin.setSource(newSource)
      if (lineFeed[:2] == "ID"):
        newID = lineFeed[3:]
        newID = newID.strip()
        newDoujin.setID(newID)
      if (lineFeed[:5] == "TITLE"):
        newTitle = lineFeed[6:]
        newTitle = newTitle.strip()
        newDoujin.setTitle(newTitle)
      if (lineFeed[:5] == "PAGES"):
        newPages = lineFeed[6:]
        newPages = newPages.strip()
        newDoujin.setPages(newPages)
      if (lineFeed[:4] == "TAGS"):
        newDoujin.setTags(commaStringToList(lineFeed[5:]))
      if (lineFeed[:3] == "URL"):
        newURL = lineFeed[4:]
        newURL = newURL.strip()
        newDoujin.setURL(newURL)
      if (lineFeed[:3] == "END"):
        doujinDict[int(newDoujin.ID)] = newDoujin
        
      lineFeed = f.readline()

  f.close()

  return doujinDict

'''
'
'
'
'
'''
def backupIndex(indexName):
  try:
    indexFile = open(indexName, "r+")
    indexContents = indexFile.read()
    indexBackup = open(indexName + ".backup", "w+")
    indexBackup.write(indexContents)
    indexBackup.close()
    indexFile.close()
    success = 0
  except IOError:
    #Create archive for first time
    open(indexName, "w+").close()
    success = 1

  return success

'''
'
' addToIndex(newDj)
'
' Parameters   : indexName : name of index file
                 newDj     : doujin item to be added to index
'
' Return Value : 0 if success, 1 if failure
'
' Description  :
'
'    Takes a single doujin item and adds it to the index.
'
'''
def addToIndex(indexName, newDj):

  try:
    indexFile = open(indexName, "a")
    indexFile.write(newDj.format())
    indexFile.write("\n")
    indexFile.close()
    success = 0
  except IOError:
    #Create archive for first time
    open(indexName, "w+").close()
    success = 1

  return success
