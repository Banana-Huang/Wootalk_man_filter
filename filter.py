import threading
import webspider
import time
import random
import tkinter as tk
import re
from tkinter import messagebox
pattern = [re.compile(r'.*男.*'), re.compile(r'.*找.*妹.*'), re.compile(r'.*找.*女.*'),
    re.compile(r'.*妳好.*'),re.compile(r'.*女.*\?|？'),re.compile(r'.*女.*嗎\?|？'),re.compile(r'.*女.*嗎')]
w_pattern = [re.compile(r'.*女.*'), re.compile(r'.*women.*')]
answer = ['高雄 21 男']
def s2( object ,robot ): 
    global pattern
    object.state_label['text'] = '檢查陌生人回復'
    leave_flag = False
    message = None
    for message in object.message_queue:
        for p in pattern:
            match = p.search(message)
            if match:
                leave_flag = True
                break
        if leave_flag:
            break
    return leave_flag
    

def s3( object, robot ):
    global answer
    object.state_label['text'] = '問候對方'
    message = random.choice(answer)
    if not robot.check_stranger():
        robot.send_message(message)
    else:
        return False
    message = robot.get_message() # progress
    while message != None:
        object.message_queue.append(message)
        message = robot.get_message()
    message = robot.get_message()
    while message != None:
        object.message_queue.append(message)
        message = robot.get_message()
    if object.message_queue:
        return True
    else:
        return False

def s4( object, robot ):
    object.state_label['text'] = '離開聊天室'
    try:
        robot.leave()
    except:
        pass
    object.message_queue.clear()
    return True

def s1( object ,robot ):
    global s4
    object.state_label['text'] = '進入聊天室'
    robot.change_secret( object.edit_text.get(1.0,'end-1c') )
    result = robot.start()
    if result == None:
        message = robot.get_message(1)
        while message != None:
            object.message_queue.append(message)
            message = robot.get_message()
        if object.message_queue:
            return True
        else:
            return False
    elif result == 'wait':
        messagebox.showinfo("被抓包了", "被抓到使用機器人,請按連結玩一下小遊戲")
        object.spider.maximize()
        object.start_button.config( state=tk.NORMAL )
        object.stop_button.config( state=tk.DISABLED )
        object.edit_text.config( state=tk.DISABLED )
        object.pause( s4 )
        return True
    elif result == 'long':
        messagebox.showinfo("等太久了", "請重新啟動,或是換一下密語")
        object.spider.maximize()
        object.start_button.config( state=tk.NORMAL )
        object.stop_button.config( state=tk.DISABLED )
        object.edit_text.config( state=tk.NORMAL )
        object.pause( s4 )
        return True

def s5( object, robot ):
    object.state_label['text'] = '檢查陌生人性別'
    global w_pattern
    catch_flag = False
    while object.message_queue:
        message = object.message_queue.pop(0)
        for p in w_pattern:
            match = p.search(message)
            if match:
                catch_flag = True
                break
        if catch_flag:
            break
    object.message_queue.clear()
    return catch_flag

def s6( object, robot ):
    object.state_label['text'] = '檢查對方回覆'
    global pattern
    leave_flag = False
    message = None
    for message in  object.message_queue:
        for p in pattern:
            match = p.search(message)
            if match:
                leave_flag = True
                break
        if leave_flag:
            break
    return leave_flag

def s7( object, robot ):
    object.state_label['text'] = '等待30秒'
    stranger_leave = robot.check_stranger()
    if stranger_leave:
        return False
    message = robot.get_message(30)
    while message != None:
        object.message_queue.append(message)
        message = robot.get_message()
    if object.message_queue:
        return True
    else:
        return False

def s8( object, robot ):
    object.state_label['text'] = '性別檢查'
    global w_pattern
    catch_flag = False
    message = None
    while object.message_queue:
        message = object.message_queue.pop(0)
        for p in pattern:
            match = p.search(message)
            if match:
                catch_flag = True
                break
        if catch_flag:
            break
    object.message_queue.clear()
    return catch_flag

def s9( object, robot ):
    global s4
    object.state_label['text'] = '上鉤啦!'
    object.start_button.config( state=tk.NORMAL )
    object.stop_button.config( state=tk.DISABLED )
    object.edit_text.config( state=tk.DISABLED )
    object.pause()
    answer = messagebox.askokcancel('上鉤囉!~','要不要釣起來?')
    if answer == True:
        try:
            robot.maximize()
        except:
            pass
        return True
    else:
        object.resume()
        return False

def s10( object, robot ): 
    object.state_label['text'] = '直球對決'
    message = '男'
    robot.send_message(message)
    time.sleep(3)
    stranger_leave = robot.check_stranger()
    if stranger_leave:
        return True
    else:
        message = robot.get_message() # progress
        while message != None:
            object.message_queue.append(message)
            message = robot.get_message()
        message = robot.get_message()
        while message != None:
            object.message_queue.append(message)
            message = robot.get_message()
        if object.message_queue:
            return False
        else:
            return True

transition_table = {s1:[s3,s2],s2:[s5,s4],s3:[s7,s6],s4:[s1,s1],\
s5:[s3,s9],s6:[s8,s4],s7:[s4,s2], s8:[s10,s9],s9:[s4,s4],s10:[s5,s4]}

class new_thread( threading.Thread ):
    def __init__( self, *args, **kwargs ):
        global transition_table
        self.start_button = kwargs['start_Button']
        self.stop_button = kwargs['stop_Button']
        self.edit_text = kwargs['edit_text']
        self.state_label = kwargs['state_label']
        del kwargs['start_Button']
        del kwargs['stop_Button']
        del kwargs['edit_text']
        del kwargs['state_label']
        super( new_thread, self ).__init__(*args,**kwargs)
        self.__running = threading.Event()
        self.__running.set()
        self.__flag = threading.Event()
        self.__flag.set()
        self.__action = None
        self.state = None
        self.message_queue = []
        self.spider = webspider.woospider()
        self.spider.connect()
        self.transition_table = transition_table
        self.secret_key = None
    
    def run( self ):
        if self.secret_key != "":
            self.spider.set_secret(self.secret_key)
        self.state = s1
        while self.__running.isSet():
            self.__flag.wait()
            self.__action = self.state( self ,self.spider )
            if self.__action:
                self.state = self.transition_table[self.state][1]
            else:
                self.state = self.transition_table[self.state][0]
            s_leave = self.spider.check_stranger()
            if s_leave:
                self.state = s4
                self.message_queue.clear()
    
    def pause( self, s = None ):
        self.__flag.clear()
        if s != None:
            self.state = s
    
    def resume( self ):
        self.__flag.set()
        self.catch = False
        
    def stop( self ):
        self.__running.clear()
        self.__flag.clear()