#!/usr/bin/env python

# SPSU AUV Team Ingress-Egress-Logger
# Copyright (C) 2014  SPSU AUV Team
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import print_function
import numpy as np
import ConfigParser
import datetime as datetime
import sys

mydf = np.zeros( (0,), dtype=[('name',np.str_,16),('time',datetime.datetime),('pass',np.int_),('id',np.str_,12)] )

def findUser(name):
  global mydf
  if np.any(mydf['name'] == name):
    return np.where(mydf['name']==name)[0][0]
  else:
   return -1

def importUser(name, id, overwriteID=False):
  global mydf
  if np.any(mydf['name'] == name):
    if not overwriteID:
      print('ERROR: '+name+' exists.', file=sys.stderr)
    else:
      i=findUser(name)
      if not mydf['id'][i]==id:
        print('WARN:  Overwriting '+name+'\'s id.', file=sys.stderr)
      mydf['id'][i]=id
    return
  newUser = np.zeros( (1,), dtype=[('name',np.str_,16),('time',datetime.datetime),('pass',np.int_),('id',np.str_,12)] )
  newUser['name'][0]=name
  newUser['id'][0]=id
  newUser['pass'][0]=-1
  mydf=np.append(mydf, newUser)
  
def reloadUsers():
  cnames=ConfigParser.RawConfigParser()
  cnames.read('names.ini')
  for entry in cnames.sections():
    importUser(entry, cnames.get(entry,'id'), overwriteID=True)
  
def lerror(str):
  print('\a\a\a\033[;31m'+str+'\033[0m')
  
def lprint(str):
  print('\033[;36m'+str+'\033[0m')
  
def login(name):
  i=findUser(name)
  if i == -1:
    lerror("Could not find member: "+name)
    lerror("Please have an admin add you")
    return
  if mydf['time'][i] == 0:
    mydf['time'][i]=datetime.datetime.now()
    lprint(name+' signed-in')
  else:
    lerror("You are already signed in")
  
def logout(data):
  name = data.partition(' ')[0]
  work = data.partition(' ')[2]
  i=findUser(name)
  if i == -1:
    lerror("Could not find member: "+name)
    lerror("Please have an admin add you")
    return
  if mydf['time'][i] == 0:
    lerror("You are already signed out")
  else:
    f = open(name+'.time', 'a')
    start=mydf['time'][i]
    diff=datetime.datetime.now()-start
    f.write(str(start)+'; '+work.translate(None, ';')+'; '+str(diff)+'; \n')
    f.close()
    mydf['time'][i] = 0
    lprint(name+' worked on '+work)

def listin():
  if not np.any(mydf['time'] <> 0):
    lerror("Lab is empty.")
  else:
    for i in list(np.where(mydf['time'] <> 0)[0]):
      lprint(mydf['name'][i])
  if not np.any(mydf['pass'] <> -1):
    lprint('All passes are signed-in')
  else:
    lerror("\n\rPARKING PASSES\n\r--------------")
    for i in list(np.where(mydf['pass'] <> -1)[0]):
      lerror(str(mydf['pass'][i])+' '+mydf['name'][i])
    
def help():
  print("\033[0;33m")
  print("Sign In: i name")
  print("Sign Out: o name work_peformed")
  print("List Users In: l")
  print("Get Parking Pass: p g last_digit name")
  print("Return Parking Pass: p r last_digit name")
  print("\033[0m")
  
def passes(data):
  global mydf
  code = data.partition(' ')[0]
  digit = data.partition(' ')[2].partition(' ')[0]
  name = data.partition(' ')[2].partition(' ')[2]
  i=findUser(name)
  if i == -1:
    lerror("Could not find member: "+name)
    lerror("Please have an admin add you")
    return
  if code[0] == 'g':
    if mydf['pass'][i] <> -1:
      lerror("You have already checked-out pass number "+str(mydf['pass'][i]))
      return
    if np.any(mydf['pass'] == int(digit)):
      lerror("Parking pass number "+digit+" is already out")
      return
    mydf['pass'][i]=int(digit)
    lprint(name+' checked-out pass number '+digit)
  elif code[0] == 'r':
    if not np.any(mydf['pass'] == int(digit)):
      lerror("Pass humber "+digit+" is already checked-in")
      return
    p=np.where(mydf['pass']==int(digit))[0][0]
    mydf['pass'][p]=-1
    if name == mydf['name'][p]:
      lprint(name+' checked-in pass number '+digit)
    else:
      lerror(name+' checked-in pass number '+digit+' for '+mydf['name'][p])
  
def a_function():
  help()
  inp=raw_input("\033[;32mReady: \033[0m")
  code = inp.partition(' ')[0][0]
  if code == 'i':
    login(inp.partition(' ')[2])
  elif code == 'o':
    logout(inp.partition(' ')[2])
  elif code == 'l':
    listin()
  elif code == 'p':
    passes(inp.partition(' ')[2])
  elif inp == 'reload':
    reloadUsers()
    lprint("Reloaded Users")
    
def main():
  reloadUsers()
  print("\033[2J")#Clear Screen
  while True:
    try:
      a_function()
    except:
      lerror("Invalid command")
  