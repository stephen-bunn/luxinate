#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com

import os
import subprocess  
    
class ProgressBar:
    
    def __init__(self, title, amount = 100):
        self.script = os.path.dirname(os.path.abspath(__file__)).replace('/Contents/Resources', '')
        self.title = self.formatSpaces(self.formatConsole(title))
        self.amount = amount
        
    def __call__(self):
        return 'SCRIPT: %s TITLE: %s AMOUNT: %s\n' % (self.script, self.title, self.amount)
     
    def formatSpaces(self, string):
        return string.replace(' ', '\ ')  
        
    def formatConsole(self, string):
        bannedChars = ['&', ';', '(', ')', '|', '"', "'", '`']
        for i in string:
            if i in bannedChars:
                string = string.replace(i, '\%s' % i)
        return string
        
    def formatOsascript(self, string):
        return 'osascript %s %s' % (self.formatSpaces(self.script), string)
        
    def runProcess(self, procCmd):
        proc = subprocess.Popen([procCmd], stdout = subprocess.PIPE, shell = True)
        (proc, proc_e) = proc.communicate()
        return proc
        
    def start(self, paramText = 'Loading...'):
        self.runProcess(self.formatOsascript('prepProgressBar %s %s %s' % (self.title, 
        self.formatSpaces(self.formatConsole(paramText)), self.amount)))
        
    def increment(self, headerText, paramText, increment):
        self.runProcess(self.formatOsascript('incrementProgressBar %s %s %s %s' % (increment, 
        self.formatSpaces(self.formatConsole(headerText)), self.formatSpaces(self.formatConsole(paramText)), 
        self.amount)))
        
    def update(self, paramText):
        self.runProcess(self.formatOsascript('updateProgressBar %s' % (self.formatSpaces(self.formatConsole(paramText)))))
        
    def quit(self):
        self.runProcess(self.formatOsascript('quitProgressBar'))
