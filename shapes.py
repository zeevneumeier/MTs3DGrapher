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
from ctypes import *

import json
import time
import os



shapes = []
shapesLoadTime = None
shapesLastLoadTryTime = None
errorMessage = ""

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

def drawErrorMessage():


    if errorMessage:
        
        currentDisplay = glGetIntegerv( GL_VIEWPORT )
        font = GLUT_BITMAP_TIMES_ROMAN_24
        
        blending = False
        if glIsEnabled(GL_BLEND) :
            blending = True

        #glEnable(GL_BLEND)
        glColor3fv((1,0,0))
        
        glViewport(20,currentDisplay[3]-30,1,1)
        
        glRasterPos2fv((0,0))
        
        for ch in errorMessage :
            glutBitmapCharacter( font , ctypes.c_int( ord(ch) ) )
        
        
        if not blending :
            glDisable(GL_BLEND)

        glViewport(currentDisplay[0], currentDisplay[1], currentDisplay[2], currentDisplay[3])

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


def loadShapeFile(shapeFile):

    global shapes, shapesLastLoadTryTime, shapesLoadTime, errorMessage

    if not shapesLoadTime or (time.time() - shapesLastLoadTryTime > 5 and os.stat(shapeFile).st_mtime != shapesLoadTime):
        
        errorMessage = ""
        
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
            errorMessage = str(exp)
            errorMessage = ((errorMessage[:150] + '..') if len(errorMessage) > 150 else errorMessage)

        shapesLastLoadTryTime = time.time()
        shapesLoadTime = os.stat(shapeFile).st_mtime

        print shapesLastLoadTryTime, shapesLoadTime


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        
        #try default
        try:
            f = open("shapes.json")
            f.close()
            shapeFile = "shapes.json"
        except:
            print "Error: can't find shapes.json file. Make sure it is in the running directory or pass the file path as a parameter."
            exit(0)
    
    else:
        shapeFile = sys.argv[1]

    loadShapeFile(shapeFile)
    
    print shapes
    
    pygame.init()
    pygame.font.init()

    infoObject = pygame.display.Info()

    display = (int(infoObject.current_w*0.80),int(infoObject.current_h*0.80))
    screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)


    gluPerspective(50, (float(display[0])/float(display[1])), 0.1, 5000)

    glTranslatef(0.0,0.0, -50)

    glRotatef(10, 1, -1, 0)

    #save the matrix for later resetting
    glPushMatrix()

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


            if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                
                #print event.rel
            
                glRotatef(.5, event.rel[1], event.rel[0], 0)

            if event.type == pygame.VIDEORESIZE:
                #print event
                #glViewport(0,0, event.w, event.h)
                pass


        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        drawAxis()
        drawAxisTicks(axisTics[axisTicksIndex])
        
        for shape in shapes:
            drawShape(shape, showShapeName)

        drawErrorMessage()
        
        #Cube2(myTexture)
        pygame.display.flip()
        pygame.time.wait(10)



