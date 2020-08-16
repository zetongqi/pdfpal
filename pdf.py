import os
import wx

from PIL import Image
from wx.lib.pubsub import pub 
import os
from PIL import Image

PhotoMaxSize = 240

files = []

class DropTarget(wx.FileDropTarget):

    def __init__(self, widget):
        wx.FileDropTarget.__init__(self)
        self.widget = widget

    def OnDropFiles(self, x, y, filenames):
        files.append(filenames[0])

        image = Image.open(filenames[0])
        image.thumbnail((PhotoMaxSize, PhotoMaxSize))
        image.save('thumbnail.png')
        pub.sendMessage('dnd', filepath='thumbnail.png')
        return True


class PhotoCtrl(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Photo Control')

        self.panel = wx.Panel(self.frame)
        pub.subscribe(self.update_image_on_dnd, 'dnd')

        self.PhotoMaxSize = 240

        self.createWidgets()
        self.frame.Show()

    def createWidgets(self):
        instructions = 'Browse for an image'
        img = wx.Image(240,240)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         wx.Bitmap(img))
        filedroptarget = DropTarget(self)
        self.imageCtrl.SetDropTarget(filedroptarget)

        instructLbl = wx.StaticText(self.panel, label=instructions)
        self.photoTxt = wx.TextCtrl(self.panel, size=(200,-1))
        browseBtn = wx.Button(self.panel, label='Browse')
        browseBtn.Bind(wx.EVT_BUTTON, self.onBrowse)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.my_btn = wx.Button(self.panel, label='Generate pdf')
        self.my_btn.Bind(wx.EVT_BUTTON, self.on_press)

        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                           0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(instructLbl, 0, wx.ALL, 5)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        self.sizer.Add(self.photoTxt, 0, wx.ALL, 5)
        self.sizer.Add(browseBtn, 0, wx.ALL, 5)
        self.mainSizer.Add(self.sizer, 0, wx.ALL, 5)

        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)

        self.panel.Layout()

    def on_press(self, event):
        name = 'mypdf'
        img_dir = os.getcwd()
        filename = os.path.join(img_dir, name+'.pdf')
        for imagePath in files:
            cover = Image.open(imagePath)
            width, height = cover.size
            print(width, height)
            #cover = cover.rotate(-90, expand=True)
            if os.path.exists(filename):
                cover.save(filename, append=True)
            else:
                cover.save(filename)

    def onBrowse(self, event):
        """ 
        Browse for file
        """
        dialog = wx.FileDialog(None, "Choose a file",
                               style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        files.append(dialog.GetPath())
        dialog.Destroy() 
        self.onView()

    def update_image_on_dnd(self, filepath):
        self.onView(filepath=filepath)

    def onView(self, filepath=None):
        if not filepath:
            filepath = self.photoTxt.GetValue()

        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW,NewH)

        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.panel.Refresh()

if __name__ == '__main__':
    app = PhotoCtrl()
    app.MainLoop()