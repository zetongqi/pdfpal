import os
import wx
from PIL import Image
from wx.lib.pubsub import pub 
import os
from PIL import Image
from variables import current_img

PhotoMaxSize = 240

files = []

class DropTarget(wx.FileDropTarget):
    def __init__(self, widget):
        wx.FileDropTarget.__init__(self)
        self.widget = widget

    def OnDropFiles(self, x, y, filenames):
        files.append(filenames[0])
        print(current_img)

        image = Image.open(filenames[0])
        image.thumbnail((PhotoMaxSize, PhotoMaxSize))
        image.save('thumbnail.png')
        pub.sendMessage('dnd', filepath='thumbnail.png')
        pub.sendMessage('file', current_img=filenames[0])
        return True


class PhotoCtrl(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Photo Control')

        self.panel = wx.Panel(self.frame)
        pub.subscribe(self.update_image_on_dnd, 'dnd')
        pub.subscribe(self.update_current_img, 'file')

        self.PhotoMaxSize = 240

        self.createWidgets()
        self.frame.Show()
        self.current_img = None

    def update_current_img(self, current_img):
        self.current_img = current_img

    def createWidgets(self):
        instructions = 'Browse for an image'
        img = wx.Image(240,240)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         wx.Bitmap(img))
        filedroptarget = DropTarget(self)
        self.imageCtrl.SetDropTarget(filedroptarget)

        instructLbl = wx.StaticText(self.panel, label=instructions)
        self.photoTxt = wx.TextCtrl(self.panel, size=(200,-1))
        browseBtn = wx.Button(self.panel, label='Browse', pos=(200, 50))
        browseBtn.Bind(wx.EVT_BUTTON, self.onBrowse)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.my_btn = wx.Button(self.panel, label='Generate pdf', pos=(200, 0))
        self.my_btn.Bind(wx.EVT_BUTTON, self.on_press)

        self.rotate_btn = wx.Button(self.panel, label='Rotate', pos=(10, 0))
        self.rotate_btn.Bind(wx.EVT_BUTTON, self.rotate_on_press)

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

    def rotate_on_press(self, event):
        cover = Image.open(self.current_img)
        cover = cover.rotate(-90, expand=True)
        cover.save(self.current_img)
        self.update_image_on_dnd(self.current_img)

    def on_press(self, event):
        name = 'mypdf'
        img_dir = os.getcwd()
        filename = os.path.join(img_dir, name+'.pdf')
        for imagePath in files:
            cover = Image.open(imagePath)
            width, height = cover.size
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
        self.current_img = dialog.GetPath()
        dialog.Destroy() 
        self.onView()

    def update_image_on_dnd(self, filepath):
        self.onView(filepath=filepath)

    def onView(self, filepath=None):
        if not filepath:
            filepath = self.photoTxt.GetValue()
        self.current_img = filepath

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