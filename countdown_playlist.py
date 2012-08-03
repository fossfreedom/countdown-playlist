# Countdown Playlist Rhythmbox Plugin

# Copyright fossfreedom <foss.freedom@gmail.com> 2012
# This is a derivative of the same software name originally created by
# Larry Price <larry.price.dev@gmail.com>, 2011-2012
# This program is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from gi.repository import RB, Gtk, GObject, Peas
import random, string, copy, os

ui_string = \
"""<ui> 
  <toolbar name="ToolBar"> 
    <placeholder name="CountdownPlaylistPlaceholder" >
        <toolitem name="Countdown Playlist" action="CountdownPlaylist" />
    </placeholder>
  </toolbar>
</ui>"""

class CountdownPlaylist (GObject.GObject, Peas.Activatable):
    __gtype_name = 'CountdownPlugin'
    object = GObject.property(type=GObject.GObject)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
	self.shell = self.object
	self.sp = self.shell.props.shell_player
        icon_file_name = os.path.dirname(__file__) + "/Countdown-Clock.png"
        iconsource = Gtk.IconSource()
        iconsource.set_filename(icon_file_name)
        iconset = Gtk.IconSet()
        iconset.add_source(iconsource)
        iconfactory = Gtk.IconFactory()
        iconfactory.add("mybutton", iconset)
        iconfactory.add_default()
        
        action = Gtk.Action("CountdownPlaylist", "Countdown",
                            "Create a playlist for a set period of time",
                            "mybutton");
        action.connect("activate", self.countdown_playlist)
        self.action_group = Gtk.ActionGroup('CountdownPlaylistActionGroup')
        self.action_group.add_action(action)
        
        ui_manager = self.shell.props.ui_manager
        ui_manager.insert_action_group(self.action_group, 0)
        self.UI_ID = ui_manager.add_ui_from_string(ui_string)
        ui_manager.ensure_update();
    
    def deactivate(self):
        ui_manager = self.shell.props.ui_manager
        ui_manager.remove_ui(self.UI_ID)
        ui_manager.ensure_update();
    
    def createSuitablePlaylist(self, theList, Duration):
	    print "createSuitablePlaylist with duration:"

            tempList = copy.copy(theList)
            manList = []
            attempts = 0
            while Duration >= 30:
                randomSong = int(random.random() * len(tempList))
                theSongInfo = tempList[randomSong]
                manList.append( theSongInfo )
                Duration = Duration - theSongInfo[1]

                if Duration < -30:
                    ## we're going to try to keep the list close to ##
                     #   +- 30 seconds, but we're not failing more  #
                     #    than 10 times so as not to waste cycles   #
                    attempts = attempts + 1
                    if attempts < 10 and len(manList):
                        manList.pop()
                        Duration = Duration + theSongInfo[1] ## correct for above
                        retries = attempts
                        if attempts > len(manList):
                            retries = len(manList)
                        for i in range(0, retries):
                            tempInfo = manList.pop()
                            Duration = Duration + tempInfo[1]
                            tempList.append(tempInfo)
                else:
                    tempList.pop(randomSong)
                ## Unfortunately RB won't add songs to the ##
                 # queue more than once, so we have to stop here #
                if not len(tempList):
                    #tempList = copy.copy(theList)
                    return manList

            return manList
        
    def addTracksToQueue(self, theList):
	    print "addTracksToQueue"
            for track in theList:
      		self.shell.props.queue_source.add_entry(track[0], -1)
        
    def ClearQueue(self):
	    print "ClearQueue"
            for row in self.shell.props.queue_source.props.query_model:
                entry = row[0]
		self.shell.props.queue_source.remove_entry(entry)
        
    def CreateGuiGetInfo(self):
	    print "CreateGuiGetInfo"
            keyword = ""
            dur = []
            dialog = Gtk.Dialog("CountdownPlaylist Specs", None, 0,
                                (Gtk.STOCK_OK, Gtk.ResponseType.YES,
                                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
                                
            entryKeyword = Gtk.Entry()
            labelKeyword = Gtk.Label("Keywords (Separated by commas, blank for anything): ")
            
            entryHour = Gtk.Entry()
            labelDuration = Gtk.Label("Duration (hour min sec): ")
            
            entryKeyword.set_editable(1)
            entryHour.set_editable(1)
            entryHour.set_size_request(50, 25)
            entryMinute = Gtk.Entry()
            entryMinute.set_editable(1)
            entryMinute.set_max_length(6)
            entryMinute.set_size_request(50, 25)
            entrySecond = Gtk.Entry()
            entrySecond.set_editable(1)
            entrySecond.set_max_length(9)
            entrySecond.set_size_request(50, 25)
            
            dialog.vbox.pack_start(labelKeyword, True, True, 0)
            labelKeyword.show()
            dialog.vbox.pack_start(entryKeyword, True, True, 0)
            entryKeyword.show()
            dialog.vbox.pack_start(labelDuration, True, True, 0)
            labelDuration.show()
            
            box1 = Gtk.HBox(False, 0)
            dialog.vbox.pack_start(box1, True, True, 0)
            box1.show()
            
            labelHour = Gtk.Label("h")
            labelMinute = Gtk.Label("m")
            labelSecond = Gtk.Label("s")
            
            box1.pack_start(entryHour, True, True, 0)
            entryHour.show()
            box1.pack_start(labelHour, True, True, 0)
            labelHour.show()
            box1.pack_start(entryMinute, True, True, 0)
            entryMinute.show()
            box1.pack_start(labelMinute, True, True, 0)
            labelMinute.show()
            box1.pack_start(entrySecond, True, True, 0)
            entrySecond.show()
            box1.pack_start(labelSecond, True, True, 0)
            labelSecond.show()
            response = dialog.run()
            keyword = entryKeyword.get_text()
            for i in range(0, 3):
                dur.append("0")
            if entryHour.get_text():
                dur[0] = entryHour.get_text()
            if entryMinute.get_text():
                dur[1] = entryMinute.get_text()
            if entrySecond.get_text():
                dur[2] = entrySecond.get_text()
            dialog.destroy()
            while Gtk.events_pending():
                Gtk.main_iteration()
            if response is Gtk.ResponseType.CANCEL:
                return (0, 0)
            else:
                return (keyword, dur)
        
    def ConvertInputToDur(self, dur):
            durSecs = 0
            if dur[0].isdigit():
                durSecs = durSecs + int(dur[0])*3600
            if dur[1].isdigit():
                durSecs = durSecs + int(dur[1])*60
            if dur[2].isdigit():
                durSecs = durSecs + int(dur[2])
            return durSecs
        
    ## this is what actually gets called when we click our button ##
    def countdown_playlist(self, event):
        (ReqKeyword, ReqDur) = self.CreateGuiGetInfo()
        RequestedDuration = self.ConvertInputToDur(ReqDur)
        if not RequestedDuration:
            return
        
         ## find all songs that correspond to the request ##
         # on another note, if the request is blank, we  #
         # will just create a playlist using every song  #
        
	ReqKeywords = None
	CountdownList = []

        if ReqKeyword: # use booleanness of string
            ReqKeywords = ReqKeyword.split(',')
            for keyword in ReqKeywords:
                keyword.lstrip(' ')
                for row in self.shell.props.library_source.props.base_query_model:
                    entry = row[0]
                    keyword = string.lower(keyword)
                    artist = string.lower(entry.get_string(RB.RhythmDBPropType.ARTIST))
                    genre  = string.lower(entry.get_string(RB.RhythmDBPropType.GENRE))
                    title  = string.lower(entry.get_string(RB.RhythmDBPropType.TITLE))
                    album  = string.lower(entry.get_string(RB.RhythmDBPropType.ALBUM))
                    album_artist  = string.lower(entry.get_string(RB.RhythmDBPropType.ALBUM_ARTIST))
                    comment  = string.lower(entry.get_string(RB.RhythmDBPropType.COMMENT))
                    year  = entry.get_ulong(RB.RhythmDBPropType.YEAR)
                    if string.find(artist, keyword) is not -1 or string.find(genre, keyword) is not -1 or \
                            string.find(title, keyword) is not -1 or string.find(album, keyword) is not -1 or \
                            string.find(album_artist, keyword) is not -1 or string.find(comment, keyword) is not -1 \
                            or string.find(string.lower(str(year)), keyword) is not -1:
			songLocation = entry
                        songDuration = entry.get_ulong(RB.RhythmDBPropType.DURATION)
                        CountdownList.append([songLocation, songDuration])

        # add all songs if query failure
        if not ReqKeywords or not CountdownList:
            for row in self.shell.props.library_source.props.base_query_model:
                entry = row[0]
		songLocation = entry
                songDuration = entry.get_ulong(RB.RhythmDBPropType.DURATION)
                CountdownList.append([songLocation, songDuration])

        CountdownList = self.createSuitablePlaylist(CountdownList, RequestedDuration)
        self.ClearQueue()
        self.addTracksToQueue(CountdownList)
        self.shell.props.shell_player.stop()
        self.shell.props.shell_player.set_playing_source( self.shell.props.queue_source )
        self.shell.props.shell_player.playpause(True)

