#!/usr/bin/env python
# encoding: utf-8
import os
import ecore
import elementary as elm
import esudo
import evas
#~ import checks
import logging
logging.basicConfig(level=logging.DEBUG)

"""eUtil

A GUI frontend for cp, mv, rm built on Python-EFL's.
By: AntCer (bodhidocs@gmail.com)

Uses a slightly modified eSudo, initially made
by Anthony Cervantes, now maintained by Jeff Hoogland,
and improved upon further by Kai Huuko.

Started: February 26, 2013
"""

import sys
import argparse
parser = argparse.ArgumentParser(description='A GUI frontend for cp, mv, and rm built on Python-EFLs.')
parser.add_argument("path", metavar="source", type=str, nargs="*",
                    help="File/Directory to perform action on.")
clargs = parser.parse_args(sys.argv[1:])

HOME = os.getenv("HOME")

#----Common
def popup_close(btn, popup, xbt=None):
    if xbt:
        xbt.disabled_set(False)
    else:
        pass
    popup.delete()

#----Popups
def file_noexist_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (1.0, 1.0)
    popup.text = "<b>Path does not exist</><br><br>Please select an appropriate path as the source."
    popup.timeout = 3.0
    popup.show()

def error_ln_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (1.0, 1.0)
    popup.text = "<b>DENIED</><br><br>The given path is a soft link. Please select an appropriate path as the source."
    popup.timeout = 3.0
    popup.show()

def error_mnt_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (1.0, 1.0)
    popup.text = "<b>DENIED</><br><br>The given path is a mount point. Please select an appropriate path as the source."
    popup.timeout = 3.0
    popup.show()

def error_sys_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (1.0, 1.0)
    popup.text = "<b>DENIED</><br><br>The given path is a critical system folder. Please select an appropriate path as the source."
    popup.timeout = 3.0
    popup.show()

def error_crit_popup(win):
    popup = elm.Popup(win)
    popup.size_hint_weight = (1.0, 1.0)
    popup.text = "<b>ERROR</><br><br>The command failed to execute properly. Please run from terminal and use output to file a bug report."
    popup.timeout = 3.0
    popup.show()

def finished_popup(win, ran):
    popup = elm.Popup(win)
    popup.size_hint_weight = (1.0, 1.0)
    popup.text = "<b>Command Finished!</b><br><br>The %s was successful." %ran
    bt = elm.Button(win)
    bt.text = "OK"
    bt.callback_clicked_add(popup_close, popup)
    popup.part_content_set("button1", bt)
    popup.show()


class buttons_main(object):
    def __init__(self, command=False):

#----Main Window
        win = self.win = elm.StandardWindow("eutil", "eUtil")
        win.callback_delete_request_add(lambda o: elm.exit())

        vbox = elm.Box(win)
        vbox.padding_set(5, 10)
        vbox.size_hint_weight_set(1.0, 1.0)
        vbox.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        vbox.pack_end(sep)
        sep.show()

        fs1b = elm.Box(win)
        fs1b.size_hint_align_set(-1.0, 0.0)
        fs1b.size_hint_weight_set(1.0, 1.0)
        vbox.pack_end(fs1b)
        fs1b.show()

        fs1 = self.fssrc = elm.FileselectorEntry(win)
        fs1.text_set("Select file/directory")
        fs1.expandable_set(False)
        fs1.inwin_mode_set(True)
        fs1.is_save_set(False)
        fs1.path_set(HOME)
        fs1.callback_file_chosen_add(self.init_wait)
        fs1.callback_activated_add(self.en_wait)
        fs1.size_hint_align_set(-1.0, -1.0)
        fs1.size_hint_weight_set(1.0, 1.0)
        fs1b.pack_end(fs1)
        fs1.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        vbox.pack_end(sep)
        sep.show()

        outbox = elm.Box(win)
        outbox.size_hint_align_set(-1.0, -1.0)
        outbox.size_hint_weight_set(1.0, 1.0)
        vbox.pack_end(outbox)
        outbox.show()

        lb = elm.Label(win)
        lb.text = "<b><i>Options:</i></b>"
        lb.size_hint_align = 0.5, 0.0
        outbox.pack_end(lb)
        lb.show()

        rdb = elm.Box(win)
        rdb.horizontal_set(True)
        outbox.pack_end(rdb)
        rdb.show()

        rd = self.r1 = elm.Radio(win)
        rd.state_value_set(1)
        rd.text_set("Copy")
        rdb.pack_end(rd)
        rdg = self.rdg = rd
        rd.show()

        rd = self.r2 = elm.Radio(win)
        rd.state_value_set(2)
        rd.group_add(rdg)
        rd.text_set("Move")
        rdb.pack_end(rd)
        rd.show()

        rd = self.r3 = elm.Radio(win)
        rd.state_value_set(3)
        rd.group_add(rdg)
        rd.text_set("Remove")
        rdb.pack_end(rd)
        rd.show()

        btbox = elm.Box(win)
        btbox.size_hint_weight_set(1.0, 1.0)
        outbox.pack_end(btbox)
        btbox.show()

        bt = self.bt = elm.Button(win)
        bt.text_set("Execute")
        bt.callback_clicked_add(self.exec_check)
        bt.size_hint_align_set(-1.0, -1.0)
        bt.size_hint_weight_set(1.0, 1.0)
        btbox.pack_end(bt)
        bt.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        vbox.pack_end(sep)
        sep.show()

        fs2b = elm.Box(win)
        fs2b.size_hint_align_set(-1.0, 0.0)
        fs2b.size_hint_weight_set(1.0, 1.0)
        vbox.pack_end(fs2b)
        fs2b.show()

        fs2 = self.fsdest = elm.FileselectorEntry(win)
        fs2.text_set("Select destination")
        fs2.expandable_set(False)
        fs2.inwin_mode_set(True)
        fs2.is_save_set(False)
        fs2.path_set("/")
        fs2.folder_only_set(True)
        fs2.callback_file_chosen_add(self.init_wait)
        fs2.callback_activated_add(self.en_wait)
        fs2.size_hint_align_set(-1.0, -1.0)
        fs2.size_hint_weight_set(1.0, 1.0)
        fs2b.pack_end(fs2)
        fs2.show()

        sep = elm.Separator(win)
        sep.horizontal_set(True)
        vbox.pack_end(sep)
        sep.show()

        win.resize_object_add(vbox)
        win.resize(510, 275)
        win.show()

#-------Add deb from CLI
        if clargs.path:
            ss = " "
            path = ss.join(clargs.path)
            if os.path.exists(path):
                self.fssrc.path_set("%s" %path)
                self.fssrc.selected_set("%s" %path)
            else:
                file_noexist_popup(self.win)
        else:
            return

#----Common
    def exec_check(self, bt):
        path = self.fssrc.selected_get()
        path = path.rstrip('\\')
        path = path.rstrip('//')
        val = self.rdg.value_get()
        act = "Action: "
        if os.path.exists(path):
            if not val:
                print(act + "No action selected.")
                return
            else:
                if val == 1:
                    bt.disabled_set(True)
                    print(act + "Copy")
                    if os.path.isdir(path):
                        val = 5
                        self.warning_popup(self.win, bt, val)
                        return
                    else:
                        self.warning_popup(self.win, bt, val)
                        return
                else:
                    if path == HOME or path == "" or path == "/etc" or path == "/usr" or path == "/bin" or path == "/boot" or path == "/lib" or path == "/home" or path == "/lib32" or path == "/lib64" or path == "/opt" or path == "/proc" or path == "/root" or path == "/sbin" or path == "/var" or path == "/media" or path == "/mnt" or path == "/dev" or path == "/cdrom" or path == "/lost+found" or path == "/run" or path == "/selinux" or path == "/srv"or path == "/sys"or path == "/tmp" or path == "/vmlinuz" or path == "/initrd.img":
                        error_sys_popup(self.win)
                        return
                    elif os.path.ismount(path):
                        error_mnt_popup(self.win)
                        return
                    elif val == 2:
                        bt.disabled_set(True)
                        print(act + "Move")
                        self.warning_popup(self.win, bt, val)
                        return
                    else:
                        bt.disabled_set(True)
                        print(act + "Remove")
                        if os.path.isdir(path):
                            val = 4
                            self.warning_popup(self.win, bt, val)
                            return
                        else:
                            self.warning_popup(self.win, bt, val)
                            return
        else:
            self.fssrc.path_set(HOME)
            self.fssrc.selected_set(HOME)
            file_noexist_popup(self.win)

    def en_wait(self, fs):
        path = fs.selected_get()
        testpath = self.fssrc.selected_get()
        if os.path.exists(path):
            return
        else:
            file_noexist_popup(self.win)
            if path == testpath:
                fs.selected_set(HOME)
                fs.path_set(HOME)
            else:
                fs.selected_set("/")
                fs.path_set("/")

    def init_wait(self, fs, string):
        path = fs.selected_get()
        if string:
            return
        else:
            fs.selected_set(path)
            fs.path_set(path)

    def execute(self, bt, val):
        src  = self.fssrc.selected_get()
        dest = self.fsdest.selected_get()
        n = elm.Notify(self.win)
        if   val == 1:
            ran = "copy"
            copy = "cp '%s' '%s'" %(src, dest)
            esudo.eSudo(copy, self.win, self.bt, ran, start_callback=self.start_cb, end_callback=self.end_cb, data=n)
        elif val == 2:
            ran = "move"
            move = "mv '%s' '%s'" %(src,dest)
            esudo.eSudo(move, self.win, self.bt, ran, start_callback=self.start_cb, end_callback=self.end_cb, data=n)
        elif val == 3:
            ran = "removal"
            remove = "rm '%s'" %src
            esudo.eSudo(remove, self.win, self.bt, ran, start_callback=self.start_cb, end_callback=self.end_cb, data=n)
        elif val == 4:
            ran = "directory removal"
            dir_remove = "rm -R '%s'" %src
            esudo.eSudo(dir_remove, self.win, self.bt, ran, start_callback=self.start_cb, end_callback=self.end_cb, data=n)
        else:
            ran = "directory copy"
            dir_copy = "cp -R '%s' '%s'" %(src, dest)
            esudo.eSudo(dir_copy, self.win, self.bt, ran, start_callback=self.start_cb, end_callback=self.end_cb, data=n)


#-------Popups
    def warning_popup(self, win, xbt, val):
        popup = elm.Popup(win)
        popup.size_hint_weight = (1.0, 1.0)
        popup.text = "<b>WARNING!</><br><br>Modifying files/directories that require Super User privileges can potentially ruin your operating system.<ps><ps>Click <i>Continue</i> if you wish to proceed. Otherwise, click <i>Close</i>."
        bt = elm.Button(win)
        bt.text = "Close"
        bt.callback_clicked_add(popup_close, popup, xbt)
        popup.part_content_set("button1", bt)
        bt = elm.Button(win)
        bt.text = "Continue"
        if val == 1 or val == 2 or val == 5:
            bt.callback_clicked_add(self.execute, val)
            bt.callback_clicked_add(popup_close, popup)
        else:
            bt.callback_clicked_add(self.rm_warning_popup, win, xbt, val)
            bt.callback_clicked_add(popup_close, popup)
        popup.part_content_set("button2", bt)
        popup.show()

    def rm_warning_popup(self, wl, win, xbt, val):
        popup = elm.Popup(win)
        popup.size_hint_weight = (1.0, 1.0)
        popup.text = "<b>CONFIRMATION</><br><br>Removing files/directories that require Super User privileges can potentially ruin your operating system.<ps><ps>Click <i>Continue</i> if you <i>really</i> wish to proceed. Otherwise, click <i>Close</i>."
        bt = elm.Button(win)
        bt.text = "Continue"
        bt.callback_clicked_add(self.execute, val)
        bt.callback_clicked_add(popup_close, popup)
        popup.part_content_set("button1", bt)
        bt = elm.Button(win)
        bt.text = "Close"
        bt.callback_clicked_add(popup_close, popup, xbt)
        popup.part_content_set("button2", bt)
        popup.show()

#---------Callbacks
    def end_cb(self, exit_code, win, xbt, ran, *args, **kwargs):
        n = kwargs["data"]
        n.delete()
        xbt.disabled_set(False)
        if exit_code == 0:
            logging.info("No errors.")
            self.fssrc.path_set(HOME)
            self.fssrc.selected_set(HOME)
            self.fsdest.path_set("/")
            self.fsdest.selected_set("/")
            finished_popup(win, ran)
        else:
            logging.critical("Something went wrong. Please file bug report!")
            error_crit_popup(self.win)

    def start_cb(self, win, *args, **kwargs):
        n = kwargs["data"]

        box = elm.Box(win)
        box.size_hint_weight = 1.0, 1.0
        box.size_hint_align = -1.0, -1.0

        lb = elm.Label(win)
        lb.text = "<b>Please wait...</b>"
        lb.size_hint_align = 0.0, 0.5
        box.pack_end(lb)
        lb.show()

        sep = elm.Separator(win)
        sep.horizontal = True
        box.pack_end(sep)
        sep.show()

        pb = elm.Progressbar(win)
        pb.style = "wheel"
        pb.pulse(True)
        pb.size_hint_weight = 1.0, 1.0
        pb.size_hint_align_set(-1.0, -1.0)
        box.pack_end(pb)
        pb.show()

        box.show()

        n.orient = 1
        n.allow_events_set(False)
        n.content = box
        n.show()


#----- Main -{{{-
if __name__ == "__main__":
    elm.init()

    buttons_main(None)

    elm.run()
    elm.shutdown()
# }}}
# vim:foldmethod=marker
