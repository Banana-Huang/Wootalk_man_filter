import threading
import tkinter as tk
from tkinter import messagebox
import filter

window = tk.Tk()
window.title('簡單暴力!')
window.geometry('485x310')


fisher = None
first_time = True
past_s = ""

def start():
    global fisher
    global past_s
    global first_time
    global b2
    global e
    b1.height=2
    b1.config( state=tk.DISABLED )
    b2.config( state=tk.NORMAL )
    e.config( state=tk.DISABLED )
    if first_time:
        past_s = e.get(1.0,'end-1c')
        fisher.secret_key = e.get(1.0,'end-1c')
        first_time = False
        fisher.start()
    else:
        fisher.resume()
        past_s = e.get(1.0,'end-1c')
        

def stop():
    global fisher
    global b1
    b1.height=2
    b1.config( state=tk.NORMAL )
    b2.config( state=tk.DISABLED )
    e.config( state=tk.NORMAL )
    fisher.pause( filter.s4 )
    fisher.message_queue.clear()

photo = tk.PhotoImage(file="background.png")
background = tk.Label(window,justify=tk.LEFT,image=photo,compound = tk.CENTER,fg = "white")
background.pack()

l1=tk.Label(window,text='密語：',font=('新細明體',20))    
l1.place(x=20,y=20,anchor='nw')

e=tk.Text(window,width=20,height=2)
e.place(x=120,y=20,anchor='nw')

b1=tk.Button(window,text='啟動',font=('新細明體',10),width=13,height=2,command=start)
b1.place(x=20,y=75,anchor='nw')

b2=tk.Button(window,text='停止',font=('新細明體',10),width=13,height=2,command=stop,state=tk.DISABLED)
b2.place(x=165,y=75,anchor='nw')

l2=tk.Label(window,text='狀態：',font=('新細明體',20))
l2.place(x=20,y=150,anchor='nw')

t=tk.Label(window,width=20,height=2,borderwidth=10,relief="ridge")
t.place(x=120,y=150,anchor='nw')
t['text'] = '一個人哭，真愛無敵'

if __name__ == '__main__':
    fisher = filter.new_thread(start_Button=b1,stop_Button=b2,edit_text=e,state_label = t )
    fisher.setDaemon(True)
    window.iconbitmap(r'love.ico')
    window.mainloop()