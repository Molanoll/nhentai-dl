import requests
import re
import urllib
import os
import shutil
import IndexReader as ir
import time
import html

NH_BASE = "https://nhentai.net/g/"
SOURCE = "nhentai"
INDEX_NAME = "index.txt"
ARCHIVE_NAME = "archive.txt"
TEMP_DIR = "temp"
FINISHED_DIR = "E:\Other\Books\Doujinshi"

def main():

  #First read index into memory
  indexDict = ir.readIndex() 

  #Get search space from user
  startID = int(input("ID to start at: "))
  endID = int(input("ID to end at: "))

  whitelistTags = askUserForTags()

  #Read and backup archived doujin ids
  backupArchive(ARCHIVE_NAME)
  archiveList = readArchive(ARCHIVE_NAME)

  #Loop through id numbers
  for i in range(startID, endID+1):

    #Check if already downloaded
    if (i in archiveList):
      continue

    #Check index for entry and compare allowed tags
    if (i in indexDict):
      if ((not checkValidSubset(indexDict[i].tags, whitelistTags)) and (whitelistTags != [])):
        print("Skipping (invalid tags) " + str(i) + ": " + indexDict[i].title + "\n")
        continue

    #Builds top gallery URL
    djURL = NH_BASE + str(i)
    r = requests.get(djURL)

    #Check if gallery is valid
    if (r.status_code != 200):
      #Prevents checking same page again in future runs
      archiveList.append(i)
      singleUpdateArchive(i, ARCHIVE_NAME)
      continue

    #Extract page source
    pageSource = r.text
    pageSource = pageSource.replace("\n", "")

    #Get all tags from doujin
    tags = getTags(pageSource)

    #Get title from doujin
    djTitle = getTitle(pageSource)

    #Folder title may be different from djTitle
    #Illegal filename characters removed and length shortened if too long
    folderTitle = fixTitleName(djTitle)

    #Extract page num
    pageNum = int(re.search("Pages.*?name.*?(\d{1,4})", pageSource).groups()[0])

    #All info gathered about doujin, add to index for future searches
    newDoujin = ir.Doujin(source=SOURCE, URL=djURL, pages=pageNum, title=djTitle, tags=tags, ID=i)
#   indexDict[int(newDoujin.ID)] = newDoujin
    ir.addToIndex(newDoujin)

    if ((not checkValidSubset(tags, whitelistTags)) and (whitelistTags != [])):
      print("Skipping (invalid tags) " + str(i) + ": " + djTitle + "\n")
      continue

    print("Downloading " + str(pageNum) + " pages from " + str(i) + ": " + djTitle + "\n")
    #Fetch first page image url and extension type
    (galleryUrl, imgExt) = getGalleryInfo(djURL)

    #Initialize directory for downloading
    try:
      os.mkdir(TEMP_DIR + "\\" + folderTitle)
    except FileExistsError:
      fileList = os.listdir(TEMP_DIR + "\\" + folderTitle)
      #If folder has correct page num, add to archive 
      if (len(fileList) == pageNum+1):
        archiveList.append(i)
        singleUpdateArchive(i, ARCHIVE_NAME)
        moveTempToComplete(folderTitle)
        continue
      else:
        shutil.rmtree(TEMP_DIR + "\\" + folderTitle)
        os.mkdir(TEMP_DIR + "\\" + folderTitle)

    #Place tags in new folder
    tagFileName = TEMP_DIR + "\\" + folderTitle + "\\" + "info.txt"
    tagFileOpen = open(tagFileName, "w")
    tagFileOpen.write("TAGS: ")
    for j in range(0, len(tags)):
      if (j == 0):
        tagFileOpen.write(tags[j])
      else:
        tagFileOpen.write(", " + tags[j])

    tagFileOpen.close()

    #Loop through all pages to download
    for j in range(1, pageNum+1):
      #Build image url
      imgUrl = galleryUrl + "/" + str(j) + imgExt
      imgR = requests.get(imgUrl)

      #imgR unsuccessful likely means mixture of png and jpg files
      if (imgR.status_code != 200):
        if (imgExt == ".png"):
          imgExt = ".jpg"
          imgUrl = galleryUrl + "/" + str(j) + imgExt
          imgR = requests.get(imgUrl)
        else:
          imgExt = ".png"
          imgUrl = galleryUrl + "/" + str(j) + imgExt
          imgR = requests.get(imgUrl)

      #Save web image to local image file
      fname = TEMP_DIR + "\\" + folderTitle + "\\" + str(j) + imgExt
      fin = open(fname, 'wb')
      fin.write(imgR.content)
      fin.close()

    #Now that doujin downloaded, mark it so not redownloaded
    archiveList.append(i)
    singleUpdateArchive(i, ARCHIVE_NAME)
#   updateArchive(archiveList, ARCHIVE_NAME)
    moveTempToComplete(folderTitle)

  #Finalize downloaded doujins into archive.txt
  updateArchive(archiveList, ARCHIVE_NAME, sortBool=True)

  #Prevents temp bans
  time.sleep(0.5)

  return

'''
'
'
'
'''
def getGalleryInfo(dUrl):
  testUrl = dUrl + "/" + "1"
  r = requests.get(testUrl)
  pageSource = r.text
  pageSource.replace("\n", "")

  tempGallery = re.search(r"image-container.*?img src=\"(.*?)\"", pageSource).groups()[0]

  imgExt = "." + re.search(r"/\d{1,3}\..*", tempGallery)[0].split(".")[1]
  gallery = re.search(r".*?\d{1,9}", tempGallery)[0]

  return (gallery, imgExt)

'''
'
'
'
'''
def moveTempToComplete(folderName):
  try:
    shutil.move(TEMP_DIR + "\\" + folderName, FINISHED_DIR + "\\")
    shutil.make_archive(FINISHED_DIR + "\\" + folderName, format="zip", root_dir=FINISHED_DIR + "\\", base_dir=folderName)
    shutil.rmtree(FINISHED_DIR + "\\" + folderName)
  except shutil.Error:
    i = 2

    while (os.path.exists(FINISHED_DIR + "\\"  + folderName + " " + str(i))):
      i += 1
    
    newFolderName = folderName + " " + str(i)
    shutil.move(TEMP_DIR + "\\" + folderName, TEMP_DIR + "\\" + newFolderName)
    shutil.move(TEMP_DIR + "\\" + folderName + " " + str(i), FINISHED_DIR + "\\")
    shutil.make_archive(FINISHED_DIR + "\\" + newFolderName, format-"zip", root_dir=FINISHED_DIR + "\\", base_dir=newFolderName)
    shutil.rmtree(FINISHED_DIR + "\\" + newFolderName)
  return

'''
'
'
'
'''
def backupArchive(fname):
  try:
    f = open(fname, "r")
    text = f.read()
    fbackup = open(ARCHIVE_NAME + ".backup", "w+")
    fbackup.write(text)
    f.close()
    fbackup.close()

    return 0

  except IOError:

    return 1    

'''
'
' def fixTitleName(fname)
'
' Parameters : fname : name to be fixed
'
' Return Value : string : fixed name
'
' Description :
'
'    Takes a title/folder name and removed and illegal
'    characters (those not allowed in the Windows OS).
'    Also replaces some common errors in names such as
'    "&#x27;" being used instead of the apostrophe.
'
'''
def fixTitleName(fname):
  fname = html.unescape(fname)
  fname = fname.replace(":", ",")
  fname = fname.replace("<", " ")
  fname = fname.replace(">", " ")
  fname = fname.replace("\"", "'")
  fname = fname.replace("/", " ")
  fname = fname.replace("|", " ")
  fname = fname.replace("?", " ")
  fname = fname.replace("*", " ")

  if (len(fname) > 251):
    fname = fname[:250]

  fname = fname.strip()

  return fname

'''
'
' def getTags(source)
'
' Parameters : source : string of toplevel doujin page contents
'
' Return Value : string list : list of all tags found
'
' Description :
'
'    Takes a web page's contents and extracts all tags from it. Adds a
'    prefix to some special tags like the artist, language, etc., but leaves
'    the traditional tags pertaining to the contents of the doujin alone.
'
'''
def getTags(source):
  #First get traditional tags
  tags = re.findall(r"twitter:description\" content=\"(.*?)\"", source)[0]
  tags = tags.split(", ")

  #Artist tags
  addTags(r"/artist/(.*?)/", "artist:", tags, source)

  #Language tags
  addTags(r"href=\"/language/(.*?)/\"", "language:", tags, source)

  #Parody tags
  addTags(r"/parody/(.*?)/", "parody:", tags, source)

  #Character tags
  addTags(r"/character/(.*?)/", "character:", tags, source)

  #Group tags
  addTags(r"href=\"/group/(.*?)/", "group:", tags, source)

  return tags

'''
'
' def addTags(rePattern, label, tagList, s)
'
' Parameters : rePattern : re pattern to be used
'              label     : string prefixed on to each tag found
'              tagList   : list that new tags will be added to
'              s         : page source to be searched
'
' Return Value : none
'
' Description :
'
'    A helper function to the getTags function. Uses the
'    provided arguments and searches for any matches. If found,
'    they get added to the tag list with the given label as a
'    prefix to each entry.
'
'''
def addTags(rePattern, label, tagList, s):
  newTags = re.findall(rePattern, s)
  for i in range(0, len(newTags)):
    tempTag = label + newTags[i]
    tagList.append(tempTag)

  return

'''
'
'
'
'''
def getTitle(source):
  titleParts = re.search(r"<h1 class=\"title\"><span class=\"before\">(.*?)<.*?pretty\">(.*?)<.*?after\">(.*?)<", source)
  title = titleParts.groups()[0]
  for i in range(1, 3):
    if (titleParts.groups()[i] == ""):
      continue
    else:
      title += " "
      title += titleParts.groups()[i]

  return title

'''
'
'
'
'''
def askUserForTags():
  confirmed = False

  while (not confirmed):
    whiteTags = input("Enter tags you would like to download (separated by commas): ")

    if (whiteTags.strip() == ""):
      whiteTags = []
    else:
      whiteTags = whiteTags.strip().split(",")

    for i in range(0, len(whiteTags)):
      whiteTags[i] = whiteTags[i].strip()

    print("Confirm these are the tags you want [y/n]:\n")
    for i in range(0, len(whiteTags)):
      print("  " + whiteTags[i] + "\n")

    confirmed = input("").lower() == 'y'

  return whiteTags

'''
'
'
'
'''
def checkValidSubset(parentSet, subset):
    return set(subset).issubset(set(parentSet))

'''
'
'
'
'''
def readArchive(fname):
  try:
    f = open(fname, "r")
    idList = []
    
    x = f.readline()
    while (x != ""):
      x = x.replace("\n", "")
      if (x != ""):
        idList.append(int(x))

      x = f.readline()

    return idList

  except:

    return []

'''
'
' def updateArchive(idList, fname sortBool=False)
'
' Parameters : idList : list containg all downloaded doujin ids
'              fname  : file to be written to
'              sortBool : sorts idList before being written to file
'
' Return Value : none
'
' Description :
'
'   Takes a list of id numbers and writes them to a text file.
'   This allows for future checks against the text file to see
'   if a particular doujin has already been downloaded.
'
'''
def updateArchive(idList, fname, sortBool=False):
  if (sortBool):
    idList.sort()

  f = open(fname, "w+")
  
  for i in range(0, len(idList)):
    f.write(str(idList[i]))
    f.write("\n")

  f.close()

  return

'''
'
' def singleUpdateArchive(idNum, fname)
'
' Parameters : idNum : id of doujin being added to archive
'
' Return Value : none
'
' Description :
'
'   Adds a single id to the doujin archive. File is appended to
'   so as to save disk read/write speed for when archive gets large.
'
'''
def singleUpdateArchive(idNum, fname):
  with open(fname, "a") as f:
    f.write(str(idNum))
    f.write("\n")

  return

main()
