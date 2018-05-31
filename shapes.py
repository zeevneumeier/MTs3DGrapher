import pygame
from pygame.locals import *

from OpenGL.arrays import * 
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_object import *



import sys
import ctypes
import numpy

from ctypes import *

import PIL
from PIL import Image
#import sdl2
#from sdl2 import video
from numpy import array

import json
import time
import os

'''
shapes = [
          {"name":"box", "color": (1,0,0), "lines": [((0,0,0),(10,0,0)), ((10,0,0),(10,10,0)), ((10,10,0),(0,10,0)), ((0,10,0),(0,0,0))]}


]
'''

shapes = []
shapesLoadTime = None
shapesLastLoadTryTime = None

axisLimits = 100
axisTics = [0, 1, 5, 10]


def drawAxis():

    glBegin(GL_LINES)

    glColor3fv((1,1,1))

    glVertex3fv((-axisLimits,0,0))
    glVertex3fv((axisLimits,0,0))

    glEnd()


    glBegin(GL_LINES)
    
    glColor3fv((1,1,1))
    
    glVertex3fv((0, -axisLimits,0))
    glVertex3fv((0, axisLimits,0))
    
    glEnd()


    glBegin(GL_LINES)
    
    glColor3fv((1,1,1))
    
    glVertex3fv((0, 0, -axisLimits))
    glVertex3fv((0, 0, 0))
    
    glEnd()



def drawAxisTicks(ticks):
    
    if ticks <= 0:
        return

    for i in range(0, axisLimits, ticks):
        drawText((i, 0, 0), "%i" % i, (1,1,1))
        drawText((-i, 0, 0), "-%i" % i, (1,1,1))
        drawText((0, i, 0), "%i" % i, (1,1,1))
        drawText((0, -i, 0), "-%i" % i, (1,1,1))
        drawText((0, 0, -i), "%i" % i, (1,1,1))

def drawShape(shape, showName):
    

    if "color" in shape:
        color = shape["color"]
    else:
        color = (1,1,1)
    

    maxX = 0
    maxY = 0
    maxZ = 0

    for line in shape["lines"]:
        
        glBegin(GL_LINES)
        
        glColor3fv(color)

        glVertex3fv(line[0])
        glVertex3fv(line[1])

            
        glEnd()

        if showName:
            maxX = max(maxX, line[0][0], line[1][0])
            maxY = max(maxY, line[0][1], line[1][1])
            maxZ = max(maxZ, line[0][2], line[1][2])

    if showName:
        drawText((maxX,maxY,maxZ), shape["name"], color)


def drawText(point, text, color, font=GLUT_BITMAP_9_BY_15):
    
    blending = False
    if glIsEnabled(GL_BLEND) :
        blending = True
    
    #glEnable(GL_BLEND)
    glColor3fv(color)
    glRasterPos3fv(point)
    for ch in text :
        glutBitmapCharacter( font , ctypes.c_int( ord(ch) ) )
    
    
    if not blending :
        glDisable(GL_BLEND)




def loadTexture(path):
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
    img_data = numpy.fromstring(img.tostring(), numpy.uint8)
    width, height = img.size

    texture = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    return texture

def loadShapeFile(shapeFile):

    global shapes, shapesLastLoadTryTime, shapesLoadTime

    if not shapesLoadTime or (time.time() - shapesLastLoadTryTime > 5 and os.stat(shapeFile).st_mtime != shapesLoadTime):
        
        print "----- loading json ----"
        
        try:
            with open(shapeFile, 'r') as f:
                tmp_shapes = json.load(f)
    
            for shape in tmp_shapes:
                if "name" not in shape:
                    raise ValueError("error: this shape does not have a name %s" %  shape)

                if "lines" not in shape:
                    raise ValueError("error in shape %s: no lines defined" % shape["name"])
    
                for line in shape["lines"]:
                    
                    if len(line) != 2:
                        raise ValueError("error in shape %s: this line does not have 2 points %s" % (shape["name"], line))
                            
                    if len(line[0]) != 3 or len(line[1]) != 3:
                        raise ValueError("error in shape %s: this line does not have valid points. Make sure each point has x,y, and z %s" % (shape["name"], line))
                            
                    try:
                        line[0][0] = float(line[0][0])
                        line[0][1] = float(line[0][1])
                        line[0][2] = float(line[0][2])
                        line[1][0] = float(line[1][0])
                        line[1][1] = float(line[1][1])
                        line[1][2] = float(line[1][2])
                    except:
                        raise ValueError("error in shape %s: this line does not have valid points. Make sure the x y and z are valid numbers %s" % (shape["name"], line))
    
            shapes = tmp_shapes
    
        except Exception as exp:
            print "bad json. try again"
            print exp

        shapesLastLoadTryTime = time.time()
        shapesLoadTime = os.stat(shapeFile).st_mtime

        print shapesLastLoadTryTime, shapesLoadTime


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print "USSAGE: shapes shapefile.json"
        exit(0)
    
    shapeFile = sys.argv[1]

    loadShapeFile(shapeFile)
    
    print shapes
    
    pygame.init()
    display = (1920,1080)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(50, (float(display[0])/float(display[1])), 0.1, 5000)

    glTranslatef(0.0,0.0, -50)

    glRotatef(10, 1, -1, 0)

    #save the matrix for later resetting
    glPushMatrix()

    mouseRotate = False
    axisTicksIndex = 0
    showShapeName = False

    while True:
        
        loadShapeFile(shapeFile)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

	    #print event


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    glTranslatef(-0.5,0,0)
                if event.key == pygame.K_RIGHT:
                    glTranslatef(0.5,0,0)

                if event.key == pygame.K_UP:
                    glTranslatef(0,1,0)
                if event.key == pygame.K_DOWN:
                    glTranslatef(0,-1,0)

                if event.key == pygame.K_MINUS:
                    glTranslatef(0,0,-1.0)
                        
                if event.key == pygame.K_EQUALS:
                    glTranslatef(0,0,1.0)
                    
                if event.key == pygame.K_r:
                    glPopMatrix()
                    glPushMatrix()

                if event.key == pygame.K_t:
                    axisTicksIndex = (axisTicksIndex +1) % len(axisTics)

                if event.key == pygame.K_n:
                    showShapeName = not showShapeName

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouseRotate = not mouseRotate

            if event.type == pygame.MOUSEMOTION and mouseRotate:
                
                #print event.rel
            
                glRotatef(.5, event.rel[1], event.rel[0], 0)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        drawAxis()
        drawAxisTicks(axisTics[axisTicksIndex])
        
        for shape in shapes:
            drawShape(shape, showShapeName)

        
        
        #Cube2(myTexture)
        pygame.display.flip()
        pygame.time.wait(10)



