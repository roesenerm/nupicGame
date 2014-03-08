#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""A simple client to read Game Event usage and predict it in real time."""

from collections import deque
import time

import pygame
import sys
from pygame.locals import *

import matplotlib.pyplot as plt

from nupic.data.inference_shifter import InferenceShifter
from nupic.frameworks.opf.modelfactory import ModelFactory

import model_params

pygame.init()

SECONDS_PER_STEP = 2
WINDOW = 60

# turn matplotlib interactive mode on (ion)
plt.ion()
fig = plt.figure()
# plot title, legend, etc
plt.title('Game Event prediction')
plt.xlabel('time [s]')
plt.ylabel('Event')

def runEvent():
  """Poll Event, make predictions, and plot the results. Runs forever."""
  # Create the model for predicting Game usage.
  model = ModelFactory.create(model_params.MODEL_PARAMS)
  model.enableInference({'predictedField': 'event'})
  # The shifter will align prediction and actual values.
  shifter = InferenceShifter()
  # Keep the last WINDOW predicted and actual values for plotting.
  actHistory = deque([0.0] * WINDOW, maxlen=60)
  predHistory = deque([0.0] * WINDOW, maxlen=60)

  # Initialize the plot lines that we will update with each new record.
  actline, = plt.plot(range(WINDOW), actHistory)
  predline, = plt.plot(range(WINDOW), predHistory)
  # Set the y-axis range.
  actline.axes.set_ylim(0, 10)
  predline.axes.set_ylim(0, 10)

  while True:
    s = time.time()
    
    white = (255,255,255)
    black = (0,0,0)
    bg = black

    fps = 30
    displayWidth = 800
    displayHeight = 600
    cellSize = 10

    UP = 'up'
    DOWN = 'down'
    RIGHT = 'right'
    LEFT = 'left'

    # Get the Game Event usage.
    def runGame():
        startx = 3
        starty = 3
        coords = [{'x':startx, 'y':starty}]
        direction = RIGHT

        isAlive = 'yes'

        while True:
            
            while isAlive == 'yes':
                
                nValue = 0
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    elif event.type == KEYDOWN:
                        if event.key == K_LEFT:
                            direction = LEFT
                        elif event.key == K_RIGHT:
                            direction = RIGHT
                        elif event.key == K_DOWN:
                            direction = DOWN
                        elif event.key == K_UP:
                            direction = UP
                if direction == UP:
                    newCell = {'x':coords[0]['x'],'y':coords[0]['y']-1}
                    nValue = 1
                
                elif direction == DOWN:
                    newCell = {'x':coords[0]['x'],'y':coords[0]['y']+1}
                    nValue = 2
                
                elif direction == RIGHT:
                    newCell = {'x':coords[0]['x']+1,'y':coords[0]['y']}
                    nValue = 3
                
                elif direction == LEFT:
                    newCell = {'x':coords[0]['x']-1,'y':coords[0]['y']}
                    nValue = 4
                
                del coords[-1]
                
                coords.insert(0,newCell)
                setDisplay.fill(bg)
                drawCell(coords)
                pygame.display.update()
                fpsTime.tick(fps)
                event = nValue
                print "event: ", event
                
                # Run the input through the model and shift the resulting prediction.
                modelInput = {'event': event}
                result = shifter.shift(model.run(modelInput))
                
                # Update the trailing predicted and actual value deques.
                inference = result.inferences['multiStepBestPredictions'][5]
                print 'inference: ', inference
                if inference is not None:
                    actHistory.append(result.rawInput['event'])
                    predHistory.append(inference)
                
                # Redraw the chart with the new data.
                actline.set_ydata(actHistory)  # update the data
                predline.set_ydata(predHistory)  # update the data
                plt.draw()
                plt.legend( ('actual','predicted') )
                
                
                #adding boundaries
                if (newCell['x'] < 0 or newCell['y'] < 0 or newCell['x'] > displayWidth/cellSize or newCell['y'] > displayHeight/cellSize):
                    isAlive = 'no'
            
            print 'you died'
            pygame.quit()
            sys.exit()

    def drawCell(coords):
        for coord in coords:
            x = coord['x']*cellSize
            y = coord['y']*cellSize
            makeCell = pygame.Rect(x,y,cellSize,cellSize)
            pygame.draw.rect(setDisplay,white,makeCell)

    global fpsTime
    global setDisplay

    fpsTime = pygame.time.Clock()
    setDisplay = pygame.display.set_mode((displayWidth,displayHeight))
    pygame.display.set_caption('controlling')
    runGame()
  

    # Make sure we wait a total of 2 seconds per iteration.
    #try:
        #plt.pause(SECONDS_PER_STEP)
    #except:
        #pass

if __name__ == "__main__":
  runEvent()
