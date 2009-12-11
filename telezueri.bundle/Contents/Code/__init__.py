# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VIDEO_PREFIX = "/video/telezueri"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art-default.png'
ICON          = 'icon-default.png'

####################################################################################################

def Start():

    ## make this plugin show up in the 'Video' section
    ## in Plex. The L() function pulls the string out of the strings
    ## file in the Contents/Strings/ folder in the bundle
    ## see also:
    ##  http://dev.plexapp.com/docs/mod_Plugin.html
    ##  http://dev.plexapp.com/docs/Bundle.html#the-strings-directory
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ## set some defaults so that you don't have to
    ## pass these parameters to these object types
    ## every single time
    ## see also:
    ##  http://dev.plexapp.com/docs/Objects.html
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

  


#### the rest of these are user created functions and
#### are not reserved by the plugin framework.
#### see: http://dev.plexapp.com/docs/Functions.html for
#### a list of reserved functions above



#
# Example main menu referenced in the Start() method
# for the 'Video' prefix handler
#

def VideoMainMenu():

    # Container acting sort of like a folder on
    # a file system containing other things like
    # "sub-folders", videos, music, etc
    # see:
    #  http://dev.plexapp.com/docs/Objects.html#MediaContainer
    dir = MediaContainer(viewGroup="InfoList")


    # see:
    #  http://dev.plexapp.com/docs/Objects.html#DirectoryItem
    #  http://dev.plexapp.com/docs/Objects.html#function-objects

    videolist = XML.ElementFromURL("http://www.20min.ch/rss/videoplaylist_platform.tmpl?pf=tz", cacheTime=120)

    shows = videolist.xpath('//data/struct/var/array/*')
    for show in shows:
        title = show.xpath('var[@name="title"]/string')[0].text
        ident = show.xpath('var[@name="id"]/number')[0].text
        dir.Append(Function(DirectoryItem(ShowMenu,title), ident=ident))

    return dir

def ShowMenu(sender, ident):
    dir = MediaContainer(viewGroup="InfoList")

    videolist = XML.ElementFromURL("http://www.20min.ch/rss/videoplaylist_platform.tmpl?pf=tz", cacheTime=120)
    show = videolist.xpath('//data/struct/var/array/struct[var/number = ' + ident + ']/var/array/*')
    Log(show)
    for episode in show:
        title = episode.xpath('var[@name="title"]/string')[0].text
        episode_id = episode.xpath('var[@name="id"]/number')[0].text

        details = XML.ElementFromURL("http://www.20min.ch/telezueri/refresh.tmpl", values={"channel_id": ident, "video_id": episode_id, "page": 0}, isHTML=True)

        summary = "\n".join(details.xpath('span[@class="text"]/text()'))

        dir.Append(VideoItem("http://server774.20min-tv.ch/videos/" + episode_id + "m.flv", title=title, summary=summary))

    return dir
