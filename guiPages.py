import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
from tkinter import *
from soap import rackMaker

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        Tk.title(self,"Soap Box")
        self.frames = {}

        for F in (StartPage, PageOne):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        ttr = rackMaker()
        xcelFiles = ttr.getNamesOfExcelFiles()
        xcelFiles.insert(0, "Create New Formula")
        tk.Label(self, text = "Formula Select", font = controller.title_font).grid(row = 0, column = 2, columnspan = 2)
        t = 1
        y = 0
        for x in xcelFiles:
            tk.Button(self, text = x, width = (100//6), height = 3, fg="white", bg ="teal", command=lambda: controller.show_frame("PageOne")).grid(row = t, column = y)

            y += 1
            if y == 6:
                y = 0
                t += 1

        # button1 = tk.Button(self, text="Go to Page One", command=lambda: controller.show_frame("PageOne"))

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 1", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()
        


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()