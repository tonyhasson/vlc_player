import mysql.connector
from mysql.connector import Error




def create_server_connection(host_name, user_name, user_password,database_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=database_name
        )
        #print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


##creating database
def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        #print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")


##for feeding data to the table
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        #print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")



##for reading data from table
def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")



# import external libraries
import vlc
from vlc import Instance
import sys
from moviepy.editor import VideoFileClip



if sys.version_info[0] < 3:
    import Tkinter as Tk
    from Tkinter import ttk
    from Tkinter.filedialog import askopenfilename
else:
    import tkinter as Tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename

# import standard libraries
import os
#import pathlib
from threading import Thread, Event
import time
#import platform
#import shelve

class ttkTimer(Thread):
    """a class serving same function as wxTimer... but there may be better ways to do this
    """

    def __init__(self, callback, tick):
        Thread.__init__(self)
        self.callback = callback
        # print("callback= ", callback())
        self.stopFlag = Event()
        self.tick = tick
        self.iters = 0

    def run(self):
        while not self.stopFlag.wait(self.tick):
            self.iters += 1
            self.callback()
            #print("ttkTimer start")

    def stop(self):
        self.stopFlag.set()

    def get(self):
        return self.iters


# def doit():
#    print("hey dude")

# code to demo ttkTimer
# t = ttkTimer(doit, 1.0)
# t.start()
# time.sleep(5)
# print("t.get= ", t.get())
# t.stop()
# print("timer should be stopped now")


class Player(Tk.Frame):
    """The main window has to deal with events.
    """

    def __init__(self, parent, title=None):
        Tk.Frame.__init__(self, parent)
        self.Player = Instance('--loop')
        self.parent = parent

        q1="""SELECT `episode_table`.`episode_num`,
    `episode_table`.`episode_time`,
    `episode_table`.`episode_season`
FROM `personal_use`.`episode_table`;"""
        results = read_query(connection, q1)

        self.episode_num=results[0][0]-1  ##subracting 1 to match array position of real episode
        self.episode_season=results[0][2]
        self.episode_time=results[0][1]

        self.first_entrence=0
        self.label_arr=[]
        self.running=0
        self.dirname=""
        self.videos=[]
        self.video_len=0


        if title == None:
            title = "tk_vlc"
        self.parent.title(title)

        # Menu Bar
        #   File Menu
        menubar = Tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Tk.Menu(menubar)
        fileMenu.add_command(label="Open", underline=0, command=self.OnOpen)
        fileMenu.add_command(label="Exit", underline=1, command=self._quit)
        menubar.add_cascade(label="File", menu=fileMenu)

        # The second panel holds controls
        self.player = None
        self.videopanel = ttk.Frame(self.parent)
        self.canvas = Tk.Canvas(self.videopanel).pack(fill=Tk.BOTH, expand=1)
        self.videopanel.pack(fill=Tk.BOTH, expand=1)

        ctrlpanel = ttk.Frame(self.parent)
        pause = ttk.Button(ctrlpanel, text="Pause", command=self.OnPause)
        play = ttk.Button(ctrlpanel, text="Play", command=self.OnPlay)
        stop = ttk.Button(ctrlpanel, text="Stop", command=self.OnStop)
        next = ttk.Button(ctrlpanel, text="next", command=self.OnNext)
        previous = ttk.Button(ctrlpanel, text="previous", command=self.OnPrevious)
        volume = ttk.Button(ctrlpanel, text="Volume", command=self.OnSetVolume)
        pause.pack(side=Tk.LEFT)
        play.pack(side=Tk.LEFT)
        stop.pack(side=Tk.LEFT)
        next.pack(side=Tk.LEFT)
        previous.pack(side=Tk.LEFT)
        volume.pack(side=Tk.LEFT)
        self.volume_var = Tk.IntVar()
        self.volslider = Tk.Scale(ctrlpanel, variable=self.volume_var, command=self.volume_sel,
                                  from_=0, to=100, orient=Tk.HORIZONTAL, length=100)
        self.volslider.pack(side=Tk.LEFT)
        ctrlpanel.pack(side=Tk.BOTTOM)

        ctrlpanel2 = ttk.Frame(self.parent)
        self.scale_var = Tk.DoubleVar()
        self.timeslider_last_val = ""
        self.timeslider = Tk.Scale(ctrlpanel2, variable=self.scale_var, command=self.scale_sel,
                                   from_=0, to=1000, orient=Tk.HORIZONTAL, length=500)
        self.timeslider.pack(side=Tk.BOTTOM, fill=Tk.X, expand=1)
        self.timeslider_last_update = time.time()
        ctrlpanel2.pack(side=Tk.BOTTOM, fill=Tk.X)

        # VLC player controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()


        # below is a test, now use the File->Open file menu
        # media = self.Instance.media_new('output.mp4')
        # self.player.set_media(media)
        # self.player.play() # hit the player button
        # self.player.video_set_deinterlace(str_to_bytes('yadif'))

        self.timer = ttkTimer(self.OnTimer, 1.0)
        self.timer.start()




        self.parent.update()

        # self.player.set_hwnd(self.GetHandle()) # for windows, OnOpen does does this


    ##tony


    def printSomething(self,txt):
        # if you want the button to disappear:
        # button.destroy() or button.pack_forget()
        # 0 is unnecessary
            #global label_arr
            if len(self.label_arr)>0:
                self.label_arr[-1].destroy()
            label = Tk.Label(root, text=txt)
            # this creates x as a new label to the GUI
            label.pack()
            self.label_arr.append(label)





    def OnNext(self):

        if self.episode_num<len(self.videos)-1:
            self.episode_num += 1
            q1="""TRUNCATE `personal_use`.`episode_table`;"""
            execute_query(connection, q1)
            q1="""INSERT INTO `personal_use`.`episode_table`
                    (`episode_num`,
                    `episode_time`,
                    `episode_season`)
                        VALUES
                        ("""+str(self.episode_num+1)+""","""+str(self.episode_time)+""","""+str(self.episode_season)+""");"""
            execute_query(connection,q1)

            self.Create(self.dirname,self.videos[self.episode_num])
            self.OnPlay()
        else:
            self.episode_season+=1
            self.episode_num=1
            q1 = """TRUNCATE `personal_use`.`episode_table`;"""
            execute_query(connection, q1)
            q1 = """INSERT INTO `personal_use`.`episode_table`
                                (`episode_num`,
                                `episode_time`,
                                `episode_season`)
                                    VALUES
                                    (""" + str(self.episode_num) + """,""" + str(self.episode_time) + """,""" + str(
                self.episode_season) + """);"""
            execute_query(connection, q1)
            self.episode_num-=1
            self.OnOpen()



    ##tony
    def OnPrevious(self):

        if self.episode_num>0:
            self.episode_num -= 1
            q1 = """TRUNCATE `personal_use`.`episode_table`;"""
            execute_query(connection, q1)
            q1 = """INSERT INTO `personal_use`.`episode_table`
                                (`episode_num`,
                                `episode_time`,
                                `episode_season`)
                                    VALUES
                                    (""" + str(self.episode_num+1) + """,""" + str(self.episode_time) + """,""" + str(
                self.episode_season) + """);"""
            execute_query(connection, q1)
            self.Create(self.dirname, self.videos[self.episode_num])
            self.OnPlay()
        else:
            self.episode_season -= 1

            self.dirname = r"C:\Users\tonyh\OneDrive\Desktop\shows and movies\shows\that 70s show\season"
            self.dirname += str(self.episode_season)

            self.mediaList = self.Player.media_list_new()
            self.videos = os.listdir(self.dirname)

            self.episode_num = len(self.videos)
            q1 = """TRUNCATE `personal_use`.`episode_table`;"""
            execute_query(connection, q1)
            q1 = """INSERT INTO `personal_use`.`episode_table`
                                            (`episode_num`,
                                            `episode_time`,
                                            `episode_season`)
                                                VALUES
                                                (""" + str(self.episode_num) + """,""" + str(
                self.episode_time) + """,""" + str(
                self.episode_season) + """);"""
            execute_query(connection, q1)
            self.episode_num -= 1
            self.OnOpen()

    def OnExit(self, evt):
        """Closes the window.
        """
        self.Close()

    def OnOpen(self):
        """Pop up a new dialow window to choose a file, then play the selected file.
        """
        # if a file is already running, then stop it.
        self.OnStop()

        # Create a file dialog opened in the current home directory, where
        # you can display all kind of files, having as title "Choose a file".
        #p = pathlib.Path(os.path.expanduser("~"))
        #fullname = askopenfilename(initialdir=p, title="choose your file",
                                   #filetypes=(("all files", "*.*"), ("mp4 files", "*.mp4")))
        #if os.path.isfile(fullname):
            #print(fullname)
            #splt = os.path.split(fullname)
        #global dirname,videos
        #dirname = os.path.dirname(fullname)
        #self.dirname=r"C:\Users\tonyh\OneDrive\Desktop\shows and movies\shows\that 70s show\season1"

        self.dirname=r"C:\Users\tonyh\OneDrive\Desktop\shows and movies\shows\that 70s show\season"
        self.dirname+=str(self.episode_season)
            #filename = os.path.basename(fullname)


            ##tony
        self.mediaList = self.Player.media_list_new()
        self.videos = os.listdir(self.dirname)

        for v in self.videos:
            self.mediaList.add_media(self.Player.media_new(os.path.join(self.dirname, v)))
            self.listPlayer = self.Player.media_list_player_new()
            self.listPlayer.set_media_list(self.mediaList)



        self.Create(self.dirname,self.videos[self.episode_num])
            # Creation
            #self.Media = self.Instance.media_new(str(os.path.join(dirname, filename)))
            #self.player.set_media(self.Media)
            # Report the title of the file chosen
            # title = self.player.get_title()
            #  if an error was encountred while retriving the title, then use
            #  filename
            # if title == -1:
            #    title = filename
            # self.SetTitle("%s - tkVLCplayer" % title)

            # set the window id where to render VLC's video output

            ##tony: you turned of this so it opens a seperate window

            #if platform.system() == 'Windows':
            #    self.player.set_hwnd(self.GetHandle())
            #else:
            #    self.player.set_xwindow(self.GetHandle())  # this line messes up windows
            # FIXME: this should be made cross-platform


        self.OnPlay()


            # set the volume slider to the current volume
            # self.volslider.SetValue(self.player.audio_get_volume() / 2)
        self.volslider.set(self.player.audio_get_volume())

    ##tony
    def Create(self,dirname,filename):


        if self.first_entrence==0:##if first time then start from the time you stopped
            self.Media = self.Instance.media_new(str(os.path.join(dirname, filename)))
            print(str(self.episode_time))
            self.Media.add_option('start-time='+str(self.episode_time)+'')
            self.player.set_media(self.Media)
            self.first_entrence+=1



        else:
            self.Media = self.Instance.media_new(str(os.path.join(dirname, filename)))
            self.player.set_media(self.Media)


        self.video_len = VideoFileClip(str(os.path.join(dirname, filename)))
        self.video_len = self.video_len.duration
        self.running=1
        #self.player.set_time(15)
        #print(filename)
        self.printSomething(filename)

    def OnPlay(self):
        """Toggle the status to Play/Pause.
        If no file is loaded, open the dialog window.
        """
        # check if there is a file to play, otherwise open a
        # Tk.FileDialog to select a file
        if not self.player.get_media():
            self.OnOpen()
        else:
            # Try to launch the media, if this fails display an error message
            if self.player.play() == -1:
                self.errorDialog("Unable to play.")

    def GetHandle(self):
        return self.videopanel.winfo_id()

    # def OnPause(self, evt):
    def OnPause(self):
        """Pause the player.
        """
        self.player.pause()

    def OnStop(self):
        """Stop the player.
        """
        self.player.stop()
        # reset the time slider
        if self.first_entrence!=0:
            self.timeslider.set(0)

    def OnTimer(self):
        """Update the time slider according to the current movie time.
        """
        #global running,episode_time
        if self.player == None:
            return
        # since the self.player.get_length can change while playing,
        # re-set the timeslider to the correct range.
        length = self.player.get_length()
        dbl = length * 0.001
        self.timeslider.config(to=dbl)

        # update the time on the slider
        tyme = self.player.get_time()
        if tyme == -1:
            tyme = 0
        dbl = tyme * 0.001


        if self.first_entrence!=0:##important for starting from saved time
            self.episode_time=dbl
        self.timeslider_last_val = ("%.0f" % dbl) + ".0"
        # don't want to programatically change slider while user is messing with it.
        # wait 2 seconds after user lets go of slider
        if time.time() > (self.timeslider_last_update + 2.0):
            self.timeslider.set(dbl)

        if self.running==1:
            if dbl>self.video_len-1:
                time.sleep(5)
                if dbl>self.video_len-1:
                    self.running=0
                    self.player.set_time(0)
                    self.OnNext()

    def scale_sel(self, evt):
        if self.player == None:
            return
        nval = self.scale_var.get()
        sval = str(nval)
        if self.timeslider_last_val != sval:
            # this is a hack. The timer updates the time slider.
            # This change causes this rtn (the 'slider has changed' rtn) to be invoked.
            # I can't tell the difference between when the user has manually moved the slider and when
            # the timer changed the slider. But when the user moves the slider tkinter only notifies
            # this rtn about once per second and when the slider has quit moving.
            # Also, the tkinter notification value has no fractional seconds.
            # The timer update rtn saves off the last update value (rounded to integer seconds) in timeslider_last_val
            # if the notification time (sval) is the same as the last saved time timeslider_last_val then
            # we know that this notification is due to the timer changing the slider.
            # otherwise the notification is due to the user changing the slider.
            # if the user is changing the slider then I have the timer routine wait for at least
            # 2 seconds before it starts updating the slider again (so the timer doesn't start fighting with the
            # user)
            # selection = "Value, last = " + sval + " " + str(self.timeslider_last_val)
            # print("selection= ", selection)
            self.timeslider_last_update = time.time()
            mval = "%.0f" % (nval * 1000)
            self.player.set_time(int(mval))  # expects milliseconds

    def volume_sel(self, evt):
        if self.player == None:
            return
        volume = self.volume_var.get()
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def OnToggleVolume(self, evt):
        """Mute/Unmute according to the audio button.
        """
        is_mute = self.player.audio_get_mute()

        self.player.audio_set_mute(not is_mute)
        # update the volume slider;
        # since vlc volume range is in [0, 200],
        # and our volume slider has range [0, 100], just divide by 2.
        self.volume_var.set(self.player.audio_get_volume())

    def OnSetVolume(self):
        """Set the volume according to the volume sider.
        """
        volume = self.volume_var.get()
        print("volume= ", volume)
        # volume = self.volslider.get() * 2
        # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
        if volume > 100:
            volume = 100
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def errorDialog(self, errormessage):
        """Display a simple error dialog.
        """
        edialog = Tk.tkMessageBox.showerror(self, 'Error', errormessage)



    def _quit(self):
        q1 = """UPDATE `personal_use`.`episode_table` SET `episode_time` = '"""+str(self.episode_time)+"""';"""
        execute_query(connection,q1);
        print("_quit: bye")
        root = Tk_get_root()
        root.quit()  # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        os._exit(1)



def Tk_get_root():
    if not hasattr(Tk_get_root, "root"):  # (1)
        Tk_get_root.root = Tk.Tk()  # initialization call is inside the function
    return Tk_get_root.root


if __name__ == "__main__":
    # Create a Tk.App(), which handles the windowing system event loop

    connection = create_server_connection("127.0.0.1", "tony", "tonton12", "personal_use")

    root = Tk_get_root()

    player = Player(root, title="tkinter vlc")

    root.protocol("WM_DELETE_WINDOW", player._quit)


    # show the player window centred and run the application
    root.mainloop()

