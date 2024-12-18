#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This file is part of CanFestival, a library implementing CanOpen Stack. 
#
#Copyright (C): Edouard TISSERANT, Francis DUPIN and Laurent BESSARD
#
#See COPYING file for copyrights details.
#
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.
#
#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import wx

from types import *
import os, re, platform, sys, time, traceback, getopt

__version__ = "$Revision: 1.27 $"

if __name__ == '__main__':
    def usage():
        print(_("\nUsage of networkedit.py :"))
        print("\n   %s [Projectpath]\n"%sys.argv[0])

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()

    if len(args) == 0:
        projectOpen = None 
    elif len(args) == 1:
        projectOpen = args[0]
    else:
        usage()
        sys.exit(2)
    
    app = wx.PySimpleApp()

ScriptDirectory = os.path.split(os.path.realpath(__file__))[0]

# Import module for internationalization
import gettext
import builtins

# Get folder containing translation files
localedir = os.path.join(ScriptDirectory,"locale")
# Get the default language
langid = wx.LANGUAGE_DEFAULT
# Define translation domain (name of translation files)
domain = "objdictgen"

# Define locale for wx
loc = builtins.__dict__.get('loc', None)
if loc is None:
    loc = wx.Locale(langid)
    builtins.__dict__['loc'] = loc
# Define location for searching translation files
loc.AddCatalogLookupPathPrefix(localedir)
# Define locale domain
loc.AddCatalog(domain)

if __name__ == '__main__':
    builtins.__dict__['_'] = wx.GetTranslation

from nodelist import *
from nodemanager import *
from networkeditortemplate import NetworkEditorTemplate
from doc_index.DS301_index import *

try:
    import wx.html

    EVT_HTML_URL_CLICK = wx.NewIdRef()

    class HtmlWindowUrlClick(wx.PyEvent):
        def __init__(self, linkinfo):
            wx.PyEvent.__init__(self)
            self.SetEventType(EVT_HTML_URL_CLICK)
            self.linkinfo = (linkinfo.GetHref(), linkinfo.GetTarget())
            
    class UrlClickHtmlWindow(wx.html.HtmlWindow):
        """ HTML window that generates and OnLinkClicked event.

        Use this to avoid having to override HTMLWindow
        """
        def OnLinkClicked(self, linkinfo):
            wx.PostEvent(self, HtmlWindowUrlClick(linkinfo))
        
        def Bind(self, event, handler, source=None, id=wx.ID_ANY, id2=wx.ID_ANY):
            if event == HtmlWindowUrlClick:
                self.Connect(-1, -1, EVT_HTML_URL_CLICK, handler)
            else:
                wx.html.HtmlWindow.Bind(event, handler, source=source, id=id, id2=id2)
    
#-------------------------------------------------------------------------------
#                                Html Frame
#-------------------------------------------------------------------------------

    [ID_HTMLFRAME, ID_HTMLFRAMEHTMLCONTENT] = [wx.NewIdRef() for _init_ctrls in range(2)]

    class HtmlFrame(wx.Frame):
        def _init_ctrls(self, prnt):
            # generated method, don't edit
            wx.Frame.__init__(self, id=ID_HTMLFRAME, name='HtmlFrame',
                  parent=prnt, pos=wx.Point(320, 231), size=wx.Size(853, 616),
                  style=wx.DEFAULT_FRAME_STYLE, title='')
            self.Bind(wx.EVT_CLOSE, self.OnCloseFrame)
            
            self.HtmlContent = UrlClickHtmlWindow(id=ID_HTMLFRAMEHTMLCONTENT,
                  name='HtmlContent', parent=self, pos=wx.Point(0, 0),
                  size=wx.Size(-1, -1), style=wx.html.HW_SCROLLBAR_AUTO|wx.html.HW_NO_SELECTION)
            self.HtmlContent.Bind(HtmlWindowUrlClick, self.OnLinkClick)

        def __init__(self, parent, opened):
            self._init_ctrls(parent)
            self.HtmlFrameOpened = opened
        
        def SetHtmlCode(self, htmlcode):
            self.HtmlContent.SetPage(htmlcode)
            
        def SetHtmlPage(self, htmlpage):
            self.HtmlContent.LoadPage(htmlpage)
            
        def OnCloseFrame(self, event):
            self.HtmlFrameOpened.remove(self.GetTitle())
            event.Skip()
        
        def OnLinkClick(self, event):
            url = event.linkinfo[0]
            try:
                import webbrowser
            except ImportError:
                wx.MessageBox(('Please point your browser at: %s') % url)
            else:
                webbrowser.open(url)
    
    Html_Window = True
except:
    Html_Window = False

[ID_NETWORKEDIT, ID_NETWORKEDITNETWORKNODES, 
 ID_NETWORKEDITHELPBAR,
] = [wx.NewIdRef() for _init_ctrls in range(3)]

[ID_NETWORKEDITNETWORKMENUBUILDMASTER, 
] = [wx.NewIdRef() for _init_coll_AddMenu_Items in range(1)]

[ID_NETWORKEDITEDITMENUNODEINFOS, ID_NETWORKEDITEDITMENUDS301PROFILE, 
 ID_NETWORKEDITEDITMENUDS302PROFILE, ID_NETWORKEDITEDITMENUOTHERPROFILE, 
] = [wx.NewIdRef() for _init_coll_EditMenu_Items in range(4)]

[ID_NETWORKEDITADDMENUSDOSERVER, ID_NETWORKEDITADDMENUSDOCLIENT, 
 ID_NETWORKEDITADDMENUPDOTRANSMIT, ID_NETWORKEDITADDMENUPDORECEIVE, 
 ID_NETWORKEDITADDMENUMAPVARIABLE, ID_NETWORKEDITADDMENUUSERTYPE, 
] = [wx.NewIdRef() for _init_coll_AddMenu_Items in range(6)]

class networkedit(wx.Frame, NetworkEditorTemplate):
    
    EDITMENU_ID = ID_NETWORKEDITEDITMENUOTHERPROFILE
    
    def _init_coll_MenuBar_Menus(self, parent):
        if self.ModeSolo:
            parent.Append(menu=self.FileMenu, title=('File'))
        parent.Append(menu=self.NetworkMenu, title=('Network'))
        parent.Append(menu=self.EditMenu, title=('Edit'))
        parent.Append(menu=self.AddMenu, title=('Add'))
        parent.Append(menu=self.HelpMenu, title=('Help'))

    def _init_coll_FileMenu_Items(self, parent):
        parent.Append(help='', id=wx.ID_NEW,
              kind=wx.ITEM_NORMAL, text=('New\tCTRL+N'))
        parent.Append(help='', id=wx.ID_OPEN,
              kind=wx.ITEM_NORMAL, text=('Open\tCTRL+O'))
        parent.Append(help='', id=wx.ID_CLOSE,
              kind=wx.ITEM_NORMAL, text=('Close\tCTRL+W'))
        parent.AppendSeparator()
        parent.Append(help='', id=wx.ID_SAVE,
              kind=wx.ITEM_NORMAL, text=('Save\tCTRL+S'))
        parent.AppendSeparator()
        parent.Append(help='', id=wx.ID_EXIT,
              kind=wx.ITEM_NORMAL, text=('Exit'))
        self.Bind(wx.EVT_MENU, self.OnNewProjectMenu, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnOpenProjectMenu, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnCloseProjectMenu, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnSaveProjectMenu, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnQuitMenu, id=wx.ID_EXIT)

    def _init_coll_NetworkMenu_Items(self, parent):
        parent.Append(help='', id=wx.ID_ADD,
              kind=wx.ITEM_NORMAL, text=('Add Slave Node'))
        parent.Append(help='', id=wx.ID_DELETE,
              kind=wx.ITEM_NORMAL, text=('Remove Slave Node'))
        parent.AppendSeparator()
        parent.Append(help='', id=ID_NETWORKEDITNETWORKMENUBUILDMASTER,
              kind=wx.ITEM_NORMAL, text=('Build Master Dictionary'))
        self.Bind(wx.EVT_MENU, self.OnAddSlaveMenu, id=wx.ID_ADD)
        self.Bind(wx.EVT_MENU, self.OnRemoveSlaveMenu, id=wx.ID_DELETE)
##        self.Bind(wx.EVT_MENU, self.OnBuildMasterMenu,
##              id=ID_NETWORKEDITNETWORKMENUBUILDMASTER)

    def _init_coll_EditMenu_Items(self, parent):
        parent.Append(help='', id=wx.ID_REFRESH,
              kind=wx.ITEM_NORMAL, text=('Refresh\tCTRL+R'))
        parent.AppendSeparator()
        parent.Append(help='', id=wx.ID_UNDO,
              kind=wx.ITEM_NORMAL, text=('Undo\tCTRL+Z'))
        parent.Append(help='', id=wx.ID_REDO,
              kind=wx.ITEM_NORMAL, text=('Redo\tCTRL+Y'))
        parent.AppendSeparator()
        parent.Append(help='', id=ID_NETWORKEDITEDITMENUNODEINFOS,
              kind=wx.ITEM_NORMAL, text=('Node infos'))
        parent.Append(help='', id=ID_NETWORKEDITEDITMENUDS301PROFILE,
              kind=wx.ITEM_NORMAL, text=('DS-301 Profile'))
        parent.Append(help='', id=ID_NETWORKEDITEDITMENUDS302PROFILE,
              kind=wx.ITEM_NORMAL, text=('DS-302 Profile'))
        parent.Append(help='', id=ID_NETWORKEDITEDITMENUOTHERPROFILE,
              kind=wx.ITEM_NORMAL, text=('Other Profile'))
        self.Bind(wx.EVT_MENU, self.OnRefreshMenu, id=wx.ID_REFRESH)
        self.Bind(wx.EVT_MENU, self.OnUndoMenu, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.OnRedoMenu, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.OnNodeInfosMenu,
              id=ID_NETWORKEDITEDITMENUNODEINFOS)
        self.Bind(wx.EVT_MENU, self.OnCommunicationMenu,
              id=ID_NETWORKEDITEDITMENUDS301PROFILE)
        self.Bind(wx.EVT_MENU, self.OnOtherCommunicationMenu,
              id=ID_NETWORKEDITEDITMENUDS302PROFILE)
        self.Bind(wx.EVT_MENU, self.OnEditProfileMenu,
              id=ID_NETWORKEDITEDITMENUOTHERPROFILE)

    def _init_coll_AddMenu_Items(self, parent):
        parent.Append(help='', id=ID_NETWORKEDITADDMENUSDOSERVER,
              kind=wx.ITEM_NORMAL, text=('SDO Server'))
        parent.Append(help='', id=ID_NETWORKEDITADDMENUSDOCLIENT,
              kind=wx.ITEM_NORMAL, text=('SDO Client'))
        parent.Append(help='', id=ID_NETWORKEDITADDMENUPDOTRANSMIT,
              kind=wx.ITEM_NORMAL, text=('PDO Transmit'))
        parent.Append(help='', id=ID_NETWORKEDITADDMENUPDORECEIVE,
              kind=wx.ITEM_NORMAL, text=('PDO Receive'))
        parent.Append(help='', id=ID_NETWORKEDITADDMENUMAPVARIABLE,
              kind=wx.ITEM_NORMAL, text=('Map Variable'))
        parent.Append(help='', id=ID_NETWORKEDITADDMENUUSERTYPE,
              kind=wx.ITEM_NORMAL, text=('User Type'))
        self.Bind(wx.EVT_MENU, self.OnAddSDOServerMenu,
              id=ID_NETWORKEDITADDMENUSDOSERVER)
        self.Bind(wx.EVT_MENU, self.OnAddSDOClientMenu,
              id=ID_NETWORKEDITADDMENUSDOCLIENT)
        self.Bind(wx.EVT_MENU, self.OnAddPDOTransmitMenu,
              id=ID_NETWORKEDITADDMENUPDOTRANSMIT)
        self.Bind(wx.EVT_MENU, self.OnAddPDOReceiveMenu,
              id=ID_NETWORKEDITADDMENUPDORECEIVE)
        self.Bind(wx.EVT_MENU, self.OnAddMapVariableMenu,
              id=ID_NETWORKEDITADDMENUMAPVARIABLE)
        self.Bind(wx.EVT_MENU, self.OnAddUserTypeMenu,
              id=ID_NETWORKEDITADDMENUUSERTYPE)

    def _init_coll_HelpMenu_Items(self, parent):
        parent.Append(help='', id=wx.ID_HELP,
              kind=wx.ITEM_NORMAL, text=('DS-301 Standard\tF1'))
        self.Bind(wx.EVT_MENU, self.OnHelpDS301Menu, id=wx.ID_HELP)
        parent.Append(help='', id=wx.ID_HELP_CONTEXT,
              kind=wx.ITEM_NORMAL, text=('CAN Festival Docs\tF2'))
        self.Bind(wx.EVT_MENU, self.OnHelpCANFestivalMenu, id=wx.ID_HELP_CONTEXT)
        if Html_Window and self.ModeSolo:
            parent.Append(help='', id=wx.ID_ABOUT,
                  kind=wx.ITEM_NORMAL, text=('About'))
            self.Bind(wx.EVT_MENU, self.OnAboutMenu, id=wx.ID_ABOUT)

    def _init_coll_HelpBar_Fields(self, parent):
        parent.SetFieldsCount(3)

        parent.SetStatusText(number=0, text='')
        parent.SetStatusText(number=1, text='')
        parent.SetStatusText(number=2, text='')

        parent.SetStatusWidths([100, 110, -1])

    def _init_utils(self):
        self.MenuBar = wx.MenuBar()
        self.MenuBar.SetEvtHandlerEnabled(True)
        
        if self.ModeSolo:
            self.FileMenu = wx.Menu(title='')
        self.NetworkMenu = wx.Menu(title='')
        self.EditMenu = wx.Menu(title='')
        self.AddMenu = wx.Menu(title='')
        self.HelpMenu = wx.Menu(title='')

        self._init_coll_MenuBar_Menus(self.MenuBar)
        if self.ModeSolo:
            self._init_coll_FileMenu_Items(self.FileMenu)
        self._init_coll_NetworkMenu_Items(self.NetworkMenu)
        self._init_coll_EditMenu_Items(self.EditMenu)
        self._init_coll_AddMenu_Items(self.AddMenu)
        self._init_coll_HelpMenu_Items(self.HelpMenu)

    def _init_ctrls(self, prnt):
        wx.Frame.__init__(self, id=ID_NETWORKEDIT, name='networkedit',
              parent=prnt, pos=wx.Point(149, 178), size=wx.Size(1000, 700),
              style=wx.DEFAULT_FRAME_STYLE, title=('Networkedit'))
        self._init_utils()
        self.SetClientSize(wx.Size(1000, 700))
        self.SetMenuBar(self.MenuBar)
        self.Bind(wx.EVT_CLOSE, self.OnCloseFrame)
        if not self.ModeSolo:
            self.Bind(wx.EVT_MENU, self.OnSaveProjectMenu, id=wx.ID_SAVE)
            accel = wx.AcceleratorTable([wx.AcceleratorEntry(wx.ACCEL_CTRL, 83, wx.ID_SAVE)])
            self.SetAcceleratorTable(accel)

        NetworkEditorTemplate._init_ctrls(self, self)

        self.HelpBar = wx.StatusBar(id=ID_NETWORKEDITHELPBAR, name='HelpBar',
              parent=self, style=wx.ST_SIZEGRIP)
        self._init_coll_HelpBar_Fields(self.HelpBar)
        self.SetStatusBar(self.HelpBar)

    def __init__(self, parent, nodelist = None, projectOpen = None):
        if nodelist is None:
            NetworkEditorTemplate.__init__(self, NodeList(NodeManager()), self, True)
        else:
            NetworkEditorTemplate.__init__(self, nodelist, self, False)
        self._init_ctrls(parent)
        self.HtmlFrameOpened = []
        
        icon = wx.Icon(os.path.join(ScriptDirectory,"networkedit.ico"),wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
                 
        if self.ModeSolo:
            if projectOpen:
                result = self.NodeList.LoadProject(projectOpen)
                if not result:
                    self.NodeList.SetCurrentSelected(0)
                    self.RefreshNetworkNodes()
                    self.RefreshProfileMenu()
            else:
                self.NodeList = None
        else:
            self.NodeList.SetCurrentSelected(0)
            self.RefreshNetworkNodes()
            self.RefreshProfileMenu()
        self.NetworkNodes.SetFocus()
        
        self.RefreshBufferState()
        self.RefreshTitle()
        self.RefreshMainMenu()

    def OnCloseFrame(self, event):
        self.Closing = True
        if not self.ModeSolo and getattr(self, "_onclose", None) != None:
            self._onclose()
        event.Skip()

    def OnChar(self, event):
        if event.ControlDown() and event.GetKeyCode() == 83 and getattr(self, "_onsave", None) != None:
            self._onsave()
        #event.Skip()

    def OnQuitMenu(self, event):
        self.Close()

#-------------------------------------------------------------------------------
#                         Load and Save Funtions
#-------------------------------------------------------------------------------

    def OnNewProjectMenu(self, event):
        if self.NodeList:
            defaultpath = os.path.dirname(self.NodeList.GetRoot())
        else:
            defaultpath = os.getcwd()
        dialog = wx.DirDialog(self , _("Choose a project"), defaultpath, wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            projectpath = dialog.GetPath()
            if os.path.isdir(projectpath) and len(os.listdir(projectpath)) == 0:
                manager = NodeManager()
                nodelist = NodeList(manager)
                result = nodelist.LoadProject(projectpath)
                if not result:
                    self.Manager = manager
                    self.NodeList = nodelist
                    self.NodeList.SetCurrentSelected(0)
                                        
                    self.RefreshNetworkNodes()
                    self.RefreshBufferState()
                    self.RefreshTitle()
                    self.RefreshProfileMenu()
                    self.RefreshMainMenu()
                else:
                    message = wx.MessageDialog(self, result, _("ERROR"), wx.OK|wx.ICON_ERROR)
                    message.ShowModal()
                    message.Destroy()
        
    def OnOpenProjectMenu(self, event):
        if self.NodeList:
            defaultpath = os.path.dirname(self.NodeList.GetRoot())
        else:
            defaultpath = os.getcwd()
        dialog = wx.DirDialog(self , _("Choose a project"), defaultpath, 0)
        if dialog.ShowModal() == wx.ID_OK:
            projectpath = dialog.GetPath()
            if os.path.isdir(projectpath):
                manager = NodeManager()
                nodelist = NodeList(manager)
                result = nodelist.LoadProject(projectpath)
                if not result:
                    self.Manager = manager
                    self.NodeList = nodelist
                    self.NodeList.SetCurrentSelected(0)
                    
                    self.RefreshNetworkNodes()
                    self.RefreshBufferState()
                    self.RefreshTitle()
                    self.RefreshProfileMenu()
                    self.RefreshMainMenu()
                else:
                    message = wx.MessageDialog(self, result, _("Error"), wx.OK|wx.ICON_ERROR)
                    message.ShowModal()
                    message.Destroy()
        dialog.Destroy()
        
    def OnSaveProjectMenu(self, event):
        if not self.ModeSolo and getattr(self, "_onsave", None) != None:
            self._onsave()
        else:
            result = self.NodeList.SaveProject()
            if result:
                message = wx.MessageDialog(self, result, _("Error"), wx.OK|wx.ICON_ERROR)
                message.ShowModal()
                message.Destroy()
        
    def OnCloseProjectMenu(self, event):
        if self.NodeList:
            if self.NodeList.HasChanged():
                dialog = wx.MessageDialog(self, _("There are changes, do you want to save?"), _("Close Project"), wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
                answer = dialog.ShowModal()
                dialog.Destroy()
                if answer == wx.ID_YES:
                    result = self.NodeList.SaveProject()
                    if result:
                        message = wx.MessageDialog(self, result, _("Error"), wx.OK|wx.ICON_ERROR)
                        message.ShowModal()
                        message.Destroy()
                elif answer == wx.ID_NO:
                    self.NodeList.ForceChanged(False)
            if not self.NodeList.HasChanged():
                self.Manager = None
                self.NodeList = None
                self.RefreshNetworkNodes()
                self.RefreshTitle()
                self.RefreshMainMenu()
        
        
#-------------------------------------------------------------------------------
#                             Refresh Functions
#-------------------------------------------------------------------------------

    def RefreshTitle(self):
        if self.NodeList != None:
            self.SetTitle(_("Networkedit - %s") % self.NodeList.GetNetworkName())
        else:
            self.SetTitle(_("Networkedit"))
    
    def RefreshStatusBar(self):
        selected = self.NetworkNodes.GetSelection()
        if self.HelpBar and selected >= 0:
            window = self.NetworkNodes.GetPage(selected)
            self.SetStatusBarText(window.GetSelection(), self.NodeList)
    
    def RefreshMainMenu(self):
        self.NetworkMenu.Enable(ID_NETWORKEDITNETWORKMENUBUILDMASTER, False)
        if self.NodeList == None:
            if self.ModeSolo:
                self.MenuBar.EnableTop(1, False)
                self.MenuBar.EnableTop(2, False)
                self.MenuBar.EnableTop(3, False)
                if self.FileMenu:
                    self.FileMenu.Enable(wx.ID_CLOSE, False)
                    self.FileMenu.Enable(wx.ID_SAVE, False)
            else:
                self.MenuBar.EnableTop(0, False)
                self.MenuBar.EnableTop(1, False)
                self.MenuBar.EnableTop(2, False)
        else:
            if self.ModeSolo:
                self.MenuBar.EnableTop(1, True)
                if self.FileMenu:
                    self.FileMenu.Enable(wx.ID_CLOSE, True)
                    self.FileMenu.Enable(wx.ID_SAVE, True)
                if self.NetworkNodes.GetSelection() == 0:
                    self.MenuBar.EnableTop(2, True)
                    self.MenuBar.EnableTop(3, True)
                else:
                    self.MenuBar.EnableTop(2, False)      
                    self.MenuBar.EnableTop(3, False)
            else:
                self.MenuBar.EnableTop(0, True)
                if self.NetworkNodes.GetSelection() == 0:
                    self.MenuBar.EnableTop(1, True)
                    self.MenuBar.EnableTop(2, True)
                else:
                    self.MenuBar.EnableTop(1, False)      
                    self.MenuBar.EnableTop(2, False)

#-------------------------------------------------------------------------------
#                              Buffer Functions
#-------------------------------------------------------------------------------

    def RefreshBufferState(self):
        NetworkEditorTemplate.RefreshBufferState(self)
        if self.NodeList is not None:
            self.RefreshTitle()

#-------------------------------------------------------------------------------
#                                Help Method
#-------------------------------------------------------------------------------

    def OnHelpDS301Menu(self, event):
        find_index = False
        selected = self.NetworkNodes.GetSelection()
        if selected >= 0:
            window = self.NetworkNodes.GetPage(selected)
            result = window.GetSelection()
            if result:
                find_index = True
                index, subIndex = result
                result = OpenPDFDocIndex(index, ScriptDirectory)
                if isinstance(result, str):
                    message = wx.MessageDialog(self, result, "INFO", wx.OK|wx.ICON_INFORMATION)
                    message.ShowModal()
                    message.Destroy()
        if not find_index:
            result = OpenPDFDocIndex(None, ScriptDirectory)
            if isinstance(result, str):
                message = wx.MessageDialog(self, result, "INFO", wx.OK|wx.ICON_INFORMATION)
                message.ShowModal()
                message.Destroy()
        
    def OnHelpCANFestivalMenu(self, event):
        #self.OpenHtmlFrame("CAN Festival Reference", os.path.join(ScriptDirectory, "doc/canfestival.html"), wx.Size(1000, 600))
        if wx.Platform == '__WXMSW__':
            readerpath = get_acroversion()
            readerexepath = os.path.join(readerpath,"AcroRd32.exe")
            if(os.path.isfile(readerexepath)):
                os.spawnl(os.P_DETACH, readerexepath, "AcroRd32.exe", '"%s"'%os.path.join(ScriptDirectory, "doc","manual_en.pdf"))
        else:
            os.system("xpdf -remote CANFESTIVAL %s %d &"%(os.path.join(ScriptDirectory, "doc/manual_en.pdf"),16))

    def OnAboutMenu(self, event):
        self.OpenHtmlFrame(_("About CAN Festival"), os.path.join(ScriptDirectory, "doc/about.html"), wx.Size(500, 450))

    def OpenHtmlFrame(self, title, file, size):
        if title not in self.HtmlFrameOpened:
            self.HtmlFrameOpened.append(title)
            window = HtmlFrame(self, self.HtmlFrameOpened)
            window.SetTitle(title)
            window.SetHtmlPage(file)
            window.SetClientSize(size)
            window.Show()

#-------------------------------------------------------------------------------
#                               Exception Handler
#-------------------------------------------------------------------------------

Max_Traceback_List_Size = 20

def Display_Exception_Dialog(e_type,e_value,e_tb):
    trcbck_lst = []
    for i,line in enumerate(traceback.extract_tb(e_tb)):
        trcbck = " " + str(i+1) + _(". ")
        if line[0].find(os.getcwd()) == -1:
            trcbck += _("file : ") + str(line[0]) + _(",   ")
        else:
            trcbck += _("file : ") + str(line[0][len(os.getcwd()):]) + _(",   ")
        trcbck += _("line : ") + str(line[1]) + _(",   ") + _("function : ") + str(line[2])
        trcbck_lst.append(trcbck)
        
    # Allow clicking....
    cap = wx.Window_GetCapture()
    if cap:
        cap.ReleaseMouse()

    dlg = wx.SingleChoiceDialog(None, 
        _("""
An error happens.

Click on OK for saving an error report.

Please be kind enough to send this file to:
edouard.tisserant@gmail.com


Error:
""") +
        str(e_type) + _(" : ") + str(e_value), 
        _("Error"),
        trcbck_lst)
    try:
        res = (dlg.ShowModal() == wx.ID_OK)
    finally:
        dlg.Destroy()

    return res

def Display_Error_Dialog(e_value):
    message = wx.MessageDialog(None, str(e_value), _("Error"), wx.OK|wx.ICON_ERROR)
    message.ShowModal()
    message.Destroy()

def get_last_traceback(tb):
    while tb.tb_next:
        tb = tb.tb_next
    return tb


def format_namespace(d, indent='    '):
    return '\n'.join(['%s%s: %s' % (indent, k, repr(v)[:10000]) for k, v in d.items()])


ignored_exceptions = [] # a problem with a line in a module is only reported once per session

def AddExceptHook(path, app_version='[No version]'):#, ignored_exceptions=[]):
    
    def handle_exception(e_type, e_value, e_traceback):
        traceback.print_exception(e_type, e_value, e_traceback) # this is very helpful when there's an exception in the rest of this func
        last_tb = get_last_traceback(e_traceback)
        ex = (last_tb.tb_frame.f_code.co_filename, last_tb.tb_frame.f_lineno)
        if str(e_value).startswith("!!!"):
            Display_Error_Dialog(e_value)
        elif ex not in ignored_exceptions:
            ignored_exceptions.append(ex)
            result = Display_Exception_Dialog(e_type,e_value,e_traceback)
            if result:
                info = {
                    'app-title' : wx.GetApp().GetAppName(), # app_title
                    'app-version' : app_version,
                    'wx-version' : wx.VERSION_STRING,
                    'wx-platform' : wx.Platform,
                    'python-version' : platform.python_version(), #sys.version.split()[0],
                    'platform' : platform.platform(),
                    'e-type' : e_type,
                    'e-value' : e_value,
                    'date' : time.ctime(),
                    'cwd' : os.getcwd(),
                    }
                if e_traceback:
                    info['traceback'] = ''.join(traceback.format_tb(e_traceback)) + '%s: %s' % (e_type, e_value)
                    last_tb = get_last_traceback(e_traceback)
                    exception_locals = last_tb.tb_frame.f_locals # the locals at the level of the stack trace where the exception actually occurred
                    info['locals'] = format_namespace(exception_locals)
                    if 'self' in exception_locals:
                        info['self'] = format_namespace(exception_locals['self'].__dict__)
                
                output = open(path+os.sep+"bug_report_"+info['date'].replace(':','-').replace(' ','_')+".txt",'w')
                lst = list(info.keys())
                lst.sort()
                for a in lst:
                    output.write(a+":\n"+str(info[a])+"\n\n")

    #sys.excepthook = lambda *args: wx.CallAfter(handle_exception, *args)
    sys.excepthook = handle_exception

if __name__ == '__main__':
    wx.InitAllImageHandlers()
    
    # Install a exception handle for bug reports
    AddExceptHook(os.getcwd(),__version__)
    
    frame = networkedit(None, projectOpen=projectOpen)

    frame.Show()
    app.MainLoop()
