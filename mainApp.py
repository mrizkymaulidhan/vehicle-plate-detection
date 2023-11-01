# Import Libraries
from tkinter import *
from tkinter import filedialog, NW
from PIL import Image, ImageTk
import imutils as im
import cv2
import numpy as np
import pytesseract
import tkinter as tk

# Path of Tesseract
pytesseract.pytesseract.tesseract_cmd=r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Main Class
class mainApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure()
        self.window.option_add('*tearOff', FALSE)

        self.header = Label(self.window, padx=0, pady=5, text="Plate Detection", font="Helvetica 20 bold italic")
        self.header.pack(side="top")
    
        self.footer = Label(self.window, padx=30, pady=10, text="Copyright © 3B-K4 2022 - All Rights Reserved", font="Calibri 12")
        self.footer.pack(side="bottom")

        self.frame1 = Frame(self.window)
        self.frame2 = Frame(self.window)

        self.rightPanel = None
        self.leftPanel = None
        
        self.circles=np.zeros((4,2),np.int32)
        self.counter=0
        self.thewindow=True

        self.menu = Menu(self.window)

        self.fileMenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_cascade(label="Open File", command=self.openImage)
        self.fileMenu.add_separator()
        self.fileMenu.add_cascade(label="Quit", command=self.window.destroy)

        self.menu.add_command(label="Crop", command=self.cropping)
        
        self.editMenu = Menu(self.menu)
        self.menu.add_cascade(label="Edit", menu=self.editMenu)
        self.editMenu.add_cascade(label="Grayscale", command=self.grayscale)
        self.editMenu.add_cascade(label="Bilateral Filter", command=self.bilateralFilter)
        self.editMenu.add_cascade(label="Thresholding", command=self.thresholding)
        self.editMenu.add_cascade(label="Opening", command=self.opening)
        self.editMenu.add_separator()
        self.editMenu.add_cascade(label="Default", command=self.resetImage)

        self.menu.add_command(label="Detection", command=self.textDetection)
    
        self.textLabel = Label(self.frame2, pady=5, text="Detection Result", font="Calibri 14 bold")
        self.text = Text(self.frame2, borderwidth=3, relief="ridge", height=1, width=10, font="Calibri 20")
    
        self.window['menu'] = self.menu
        self.window.mainloop()

    # Open File
    def openFile(self):
        fileDir = filedialog.askopenfilename(title="Open an Image", filetypes=[(
            'Image files', '*.jpg *.jpeg *.jfif *.png *.bmp *.tiff *.svg *.gif')])
        return fileDir

    # OpenImage
    def openImage(self, size=[625,625]):
        fileDir = self.openFile()
        self.currentFileDir = fileDir
        self.img = cv2.cvtColor(cv2.imread(fileDir), cv2.COLOR_BGR2RGB)
        self.imgEdit = self.img
        self.photo = Image.fromarray(self.img)
        self.photo.thumbnail(size,Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(image=self.photo)

        if(self.leftPanel != None and self.rightPanel != None):
            self.leftPanel.configure(image=self.photo)
            self.leftPanel.image = self.photo
            self.rightPanel.configure(image=self.photo)
            self.rightPanel.image = self.photo
        else:
            self.leftPanel = Label(self.frame1, borderwidth=3, relief="ridge", height=self.photo.height()+20, width=self.photo.width()+20, image=self.photo)
            self.leftPanel.image = self.photo
            self.leftPanel.grid(row=0, column=0, sticky=NW)
            
            self.rightPanel = Label(self.frame1, borderwidth=3, relief="ridge", height=self.photo.height()+20, width=self.photo.width()+20, image=self.photo)
            self.rightPanel.image = self.photo
            self.rightPanel.grid(row=0, column=1, sticky=NW)

        self.frame1.pack(side="top", pady=15)
        self.textLabel.pack(side="top")
        self.text.pack(side="bottom")
        self.frame2.pack()

    # Convert to Grayscale
    def grayscale(self):
        if(len(self.imgEdit.shape) == 2):
            self.imgEdit = cv2.cvtColor(self.imgEdit, cv2.COLOR_GRAY2RGB)
        self.imgEdit = cv2.cvtColor(self.imgEdit, cv2.COLOR_BGR2GRAY)
        self.newRightPanel(self.imgEdit)

    # Removing Noise with Bilateral Filter
    def bilateralFilter(self):
        self.imgEdit = cv2.bilateralFilter(self.imgEdit, 9, 75, 75)
        self.newRightPanel(self.imgEdit)
        self.gray = self.imgEdit

    # Edge detection with Canny Operator
    def edgeDetection(self):
        self.imgEdit = cv2.Canny(self.imgEdit, 170, 200)
        self.newRightPanel(self.imgEdit)
    
    # Thresholding
    def thresholding(self):
        self.imgEdit = cv2.threshold(self.imgEdit, 127, 255, cv2.THRESH_BINARY)[1]
        self.newRightPanel(self.imgEdit)

    # Dilation
    def dilation(self):
        kernel = np.ones((5,5),np.uint8)
        self.imgEdit = cv2.dilate(self.imgEdit,kernel,iterations = 1)
        self.newRightPanel(self.imgEdit)

    # Erosion
    def erosion(self):
        kernel = np.ones((5,5),np.uint8)
        self.imgEdit = cv2.erode(self.imgEdit,kernel,iterations = 1)
        self.newRightPanel(self.imgEdit)

    # Opening
    def opening(self):
        kernel = np.ones((5,5),np.uint8)
        self.imgEdit = cv2.erode(self.imgEdit,kernel,iterations = 1)
        self.imgEdit = cv2.dilate(self.imgEdit,kernel,iterations = 1)
        self.newRightPanel(self.imgEdit)
    
    # Closing
    def closing(self):
        kernel = np.ones((5,5),np.uint8)
        self.imgEdit = cv2.dilate(self.imgEdit,kernel,iterations = 1)
        self.imgEdit = cv2.erode(self.imgEdit,kernel,iterations = 1)
        self.newRightPanel(self.imgEdit)
    
    # Detection with Tesseract
    def textDetection(self):
        text = pytesseract.image_to_string(self.imgEdit, config='--psm 11')
        self.text.delete("1.0", "end")
        self.text.insert(tk.END, text)
    
    # Reset Image to Default
    def resetImage(self):
        self.imgEdit = self.img
        self.newRightPanel(self.imgEdit)

    # Update Image in Right Panel
    def newRightPanel(self,image):
        self.photo = Image.fromarray(image)
        self.photo.thumbnail((625,625),Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(image=self.photo)

        self.rightPanel.configure(image=self.photo)
        self.rightPanel.image = self.photo

    # Contour
    def contour(self):
        (cnts, _) = cv2.findContours(self.imgEdit, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:30]

        NumberPlateCnt = None
        
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:  
                NumberPlateCnt = approx 
                break

        mask = np.zeros(self.tes.shape, np.uint8)
        self.imgEdit = cv2.drawContours(mask,[NumberPlateCnt],0,255,-1)
        self.imgEdit = cv2.bitwise_and(self.img, self.img, mask=mask)
        self.newRightPanel(self.imgEdit)

    def cropping(self):
        gray = cv2.cvtColor(self.imgEdit, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        self.gray = gray
        edged = self.imgEdit = cv2.Canny(self.imgEdit, 170, 200)

        kernel = np.ones((5,5), np.uint8)
        dilasi = cv2.dilate(edged, kernel, iterations = 1)
        erosi = cv2.erode(dilasi, kernel, iterations = 1)

        (cnts, _) = cv2.findContours(erosi, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:30]

        NumberPlateCnt = None
        
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:  
                NumberPlateCnt = approx 
                break

        mask = np.zeros(gray.shape, np.uint8)
        new_img = cv2.drawContours(mask,[NumberPlateCnt], 0, 255, -1)
        new_img = cv2.bitwise_and(self.img, self.img, mask=mask)
        self.imgEdit = new_img
        self.newRightPanel(self.imgEdit)
        
mainApp(Tk(), "Plate Detection")
