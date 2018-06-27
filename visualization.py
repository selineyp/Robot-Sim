#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
#
# Author: Peter Schüller (2014)
# Adapted from a script posted by Adam Marshall Smith on the potassco mailing list (2014)
#

import sys
import re
import json
import subprocess
import collections
import traceback
import time
from PIL import Image, ImageTk


def extractExtensions(answerset):
  #print(repr(answer_set))
  field_pattern = re.compile(r'(\w+)\((\d+)\)')
  tuple_pattern = re.compile(r'(\w+)\((.*,.*)\)')
  extensions = collections.defaultdict(lambda: set())
  for l in answerset:
    try:
      args = field_pattern.match(l).groups()
      #print "for {} got field pattern match {}".format(l, repr(args))
      # first arg = predicate
      # second/third arg = coordinates
      # rest is taken as string if not None but " are stripped
      head = args[0]
      rest = int(args[1])
      extensions[head].add(rest)
      if args[3]:
        rest.append(str(args[3]).strip('"'))
      #sys.stderr.write(
      #  "got head {} and rest {}\n".format(repr(head), repr(rest))
    except:
      #sys.stderr.write("exception ignored: "+traceback.format_exc())
      pass
  for l in answerset:
      try:
        args = tuple_pattern.match(l).groups()
        #print "for {} got field pattern match {}".format(l, repr(args))
        # first arg = predicate
        # second/third arg = coordinates
        # rest is taken as string if not None but " are stripped
        head = args[0]
        rest = args[1]
        extensions[head].add(rest)
        if args[3]:
          rest.append(str(args[3]).strip('"'))
        #sys.stderr.write(
        #  "got head {} and rest {}\n".format(repr(head), repr(rest))
      except:
        #sys.stderr.write("exception ignored: "+traceback.format_exc())
        pass
  print(extensions)
  return extensions

def render_svg(literals,size=20):
    import xmlbuilder

    answer_set = extractExtensions(literals)
    maxx = max([x[0] for x in answer_set['row']])
    maxy = max([x[1] for x in answer_set['column']])

    svg = xmlbuilder.XMLBuilder(
        'svg',
        viewBox="0 0 %d %d"%(10*(maxx+1),10*(maxy+1)),
        xmlns="http://www.w3.org/2000/svg",
        **{'xmlns:xlink':"http://www.w3.org/1999/xlink"})

    #with svg.linearGradient(id="grad"):
    #    svg.stop(offset="0", **{'stop-color': "#f00"})
    #    svg.stop(offset="1", **{'stop-color': "#ff0"})

    #with svg.g():
    #    for (x,y) in room.values():
    #        svg.circle(cx=str(5+10*x),cy=str(5+10*y),r="2")

    with svg.g():
        for x in answer_set['row']:
            for y in answer_set['column']:
                x = int(x)
                y = int(y)
                svg.rect(x=str(10*x -5),
                        y=str(10*y-5),
                        width=str(10),
                        height=str(10),
                        style="stroke: black; stroke-width: 1px; fill:white;")

    #return IPython.display.SVG(data=str(svg))
    with file("out.svg","w+") as f:
      f.write(str(svg))

import tkinter as tk
class Window:
  def __init__(self,answersets):
    self.answersets = answersets
    self.selections = list(range(0,len(self.answersets)))
    self.selected = 0
    self.root = tk.Tk()
    self.main = tk.Frame(self.root)
    self.main.pack(fill=tk.BOTH, expand=1)
    self.canvas = tk.Canvas(self.main, bg="white")
    self.canvas.pack(fill=tk.BOTH, expand=1, side=tk.BOTTOM)
    self.selector = tk.Scale(self.main, orient=tk.HORIZONTAL, showvalue=0, command=self.select)
    self.selector.pack(side=tk.RIGHT,fill=tk.X)
    self.root.bind("<Right>", lambda x:self.go(+1))
    self.root.bind("<Left>", lambda x:self.go(-1))
    self.root.bind("q", exit) # TODO more graceful quitting
    self.items = []
    #self.root.after(0, self.animation)
    self.updateView()


  def select(self,which):
    self.selected = int(which)
    self.updateView()

  def go(self,direction):
    self.selected = (self.selected + direction) % len(self.answersets)
    self.updateView()

  def updateView(self):
    self.selector.config(from_=0, to=len(self.answersets)-1)

    SIZE=40
    FIELD_FILL='#FFF'
    WALL_FILL='#444'
    MARK_FILL='#A77'
    TEXT_FILL='#000'
    ROBOT_FILL='#ffc0cb'
    TARGET_FILL='#ccccff'

    def fieldRect(x,y,offset=SIZE):
      x, y = int(x)+1, int(y)+1
      return (x*SIZE-offset/2, y*SIZE-offset/2, x*SIZE+offset/2, y*SIZE+offset/2)

    # delete old items
    for i in self.items:
      self.canvas.delete(i)
    # create new items
    self.items = []

    ext = extractExtensions(self.answersets[self.selected])
    #print repr(ext)
    maxx = max([x for x in ext['row']])
    maxy = max([x for x in ext['column']])
    self.root.geometry("{}x{}+1+1".format((maxx+2)*SIZE, (maxy+2)*SIZE))
    for x in ext['row']:
        for y in ext['column']:
            self.items.append( self.canvas.create_rectangle( * fieldRect(y,x), fill=FIELD_FILL) )

    self.img = Image.open("smallrobo.gif")
    self.robo = ImageTk.PhotoImage(self.img)
    for a in ext['obstacleAt']:#static
      x=a.split(',')
      self.items.append( self.canvas.create_rectangle( * fieldRect(x[1],x[0]), fill=WALL_FILL) )
    counter=0
    tmp=sorted(list(ext['robotAt']), key=lambda x: int(x[-1]))
    tmp1=sorted(list(ext['target']), key=lambda x: int(x[-1]))
    timelim=int(tmp[-1].split(',')[-1])
    for i in range(0,timelim+1):
        x=tmp[i].split(',')
        c,d = int(x[1])+1, int(x[0])+1

        if(i!=timelim):
            x1=tmp1[i].split(',')
            c1,d1 = int(x1[1])+1, int(x1[0])+1
            di=x1[-2]
        else:
            x1=tmp1[i-1].split(',')
            c1,d1 = int(x1[3])+1, int(x1[2])+1
        counter+=1
        if counter==1:
            self.rob=self.canvas.create_image(c*SIZE, d*SIZE,image=self.robo)
            self.items.append(self.rob)
            self.tar=self.canvas.create_oval(*fieldRect(x1[1],x1[0],10), fill=TARGET_FILL)
            a=(int(x1[1])+1)*SIZE
            b=(int(x1[0])+1)*SIZE+2
            a1=(int(x1[1])+1)*SIZE+4
            b1=(int(x1[0])+1)*SIZE
            a2=(int(x1[1])+1)*SIZE-4
            b2=(int(x1[0])+1)*SIZE

            self.arrow=self.canvas.create_polygon(a,b,a1,b1,a2,b2,fill='black')
            if di=='west':
                self.canvas.coords(self.arrow,a,b,a1-4,b1-2,a2,b2)
            elif di=='east':
                self.canvas.coords(self.arrow,a,b,a1,b1,a2+4,b2-2)
            elif di=='north':
                self.canvas.coords(self.arrow,a,b-4,a1,b1,a2,b2)

            self.items.append(self.tar)
            self.canvas.update()
        else:
            time.sleep(1)
            self.canvas.move(self.rob, (c-lastx)*SIZE, (d-lasty)*SIZE)
            self.canvas.move(self.tar, (c1-lastx1)*SIZE, (d1-lasty1)*SIZE)
            self.canvas.move(self.arrow,(c1-lastx1)*SIZE, (d1-lasty1)*SIZE)
            time.sleep(1)
            a=c1*SIZE
            b=d1*SIZE+2
            a1=c1*SIZE+4
            b1=d1*SIZE
            a2=c1*SIZE-4
            b2=d1*SIZE
            if di=='west':
                self.canvas.coords(self.arrow,a,b,a1-4,b1-2,a2,b2)
            elif di=='east':
                self.canvas.coords(self.arrow,a,b,a1,b1,a2+4,b2-2)
            elif di=='north':
                self.canvas.coords(self.arrow,a,b-4,a1,b1,a2,b2)
            elif di=='south':
                self.canvas.coords(self.arrow,a,b,a1,b1,a2,b2)
            self.canvas.update()
        lastx=c
        lasty=d
        lastx1=c1
        lasty1=d1


def display_tk(answersets):
  w = Window(answersets)

MAXANS=100
clingo = subprocess.Popen(
  "clingo --outf=2 {}".format(' '.join(sys.argv[1:])),
  shell=True, stdout=subprocess.PIPE, stderr=sys.stderr)
clingoout, clingoerr = clingo.communicate()
del clingo
clingoout = json.loads(clingoout.decode('utf-8'))
#print(repr(clingoout))
#print(repr(clingoout['Call'][0]['Witnesses']))
#print(repr(clingoout['Call'][0]['Witnesses'][0]['Value']))
witnesses = clingoout['Call'][0]['Witnesses']

#import random
#render_svg(random.choice(witn)['Value'])
display_tk([witness['Value'] for witness in witnesses])

tk.mainloop()
