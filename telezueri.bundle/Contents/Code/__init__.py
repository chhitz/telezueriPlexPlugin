from random import randint

####################################################################################################

VIDEO_PREFIX = "/video/telezueri"
TELE_ZUERI_VIDEOLIST_URL = "http://www.20min.ch/rss/videoplaylist_platform.tmpl?pf=tz"
TELE_ZUERI_DETAILS_URL = "http://www.20min.ch/telezueri/refresh.tmpl"
TELE_ZUERI_SERVERLIST_URL = "http://server072.20min-tv.ch/lb_20min/servers.xml?899"

NAME = L('Title')

ART           = 'art-default.png'
ICON          = 'icon-default.png'

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    #MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

def VideoMainMenu():
    dir = MediaContainer(viewGroup="InfoList")

    serverlist = HTML.ElementFromURL(TELE_ZUERI_SERVERLIST_URL, cacheTime=300)
    Log(XML.StringFromElement(serverlist))
    servers = serverlist.xpath('//var[@name="url"]/string')
    for server in servers:
        Log(server.text)
        try:
            result = HTTP.Request(server.text)
        except:
            servers.remove(server)

    videolist = XML.ElementFromURL(TELE_ZUERI_VIDEOLIST_URL, cacheTime=120)

    shows = videolist.xpath('//data/struct/var/array/*')
    for show in shows:
        title = show.xpath('var[@name="title"]/string')[0].text
        ident = show.xpath('var[@name="id"]/number')[0].text
        dir.Append(Function(DirectoryItem(ShowMenu, title), server=servers[(randint(0, len(servers) - 1))].text, ident=ident))

    return dir

def ShowMenu(sender, ident, server, start=0):
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)
    show_count = 0

    videolist = XML.ElementFromURL(TELE_ZUERI_VIDEOLIST_URL, cacheTime=120)
    show = videolist.xpath('//data/struct/var/array/struct[var/number = ' + ident + ']/var/array/*')
    for episode in show[start:]:
        if show_count == 8:
            dir.Append(Function(DirectoryItem(ShowMenu, L("More Results")), server=server, ident=ident, start=(start + show_count)))
            break
        show_count += 1

        title = episode.xpath('var[@name="title"]/string')[0].text
        episode_id = episode.xpath('var[@name="id"]/number')[0].text

        details = HTML.ElementFromURL(TELE_ZUERI_DETAILS_URL, values={"channel_id": ident, "video_id": episode_id, "page": 0})

        summary = "\n".join(details.xpath('span[@class="text"]/text()'))

        dir.Append(VideoItem(server + episode_id + "m.flv", title=title, summary=summary))

    return dir
