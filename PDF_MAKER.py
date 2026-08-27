# main Python code to convert database file in to pdf

#import libraries
import pyodbc
from datetime import date
import timeit
import os
import pdf_maker as pm
import login
from tkinter import *
from tkinter import ttk,messagebox
from functools import partial
from PIL import ImageTk, Image
import sys
def resource_path(relative_path):
   #Get absolute path to resource, works for dev and for PyInstaller
    try:

        base_path = sys._MEIPASS
    except:
         base_path = os.path.abspath(".")    
    
    return os.path.join(base_path, relative_path)

   
    
#this function check login if ok go to generate pd

def check_login(user,code,ip_add,level):   
    global level_add
    try:
        print("Button clicked")                 
        #print(user.get(),code.get())
        c =login.login(user.get(),code.get(),ip_add.get())                   
        print("Login success")                            
        name=user.get()          
        level_add =level.get()           
        generate_pdf(c,name)          
        
   
    except pyodbc.Error as ex:
         err =ex.args[0]
         if err == '08S01':
            print('Not on FGI network, Check VPN connection')
            messagebox.showerror('Python Error', 'Not on FGI network, Check VPN connection')
         if err == '28000':
            print('Check user id/password')        
            messagebox.showerror('Python Error', 'Check user id/password')

#this function get schedule number and go to make pdf    
def generate_pdf(c,user_name):    
    global logged_in
    root.destroy()
    
    logged_in = Tk()
    logged_in.title("Tax invoice & Credit note PDF generator") 
    logged_in.geometry("925x450+230+110")
    logged_in.configure(bg='#fff')
    logged_in.resizable(False,False)
    #image adjusted here
    #img2=Image.open("profile.png")
    img2=Image.open(resource_path("profile.png"))
    img = img2.resize((200,200))
    img = ImageTk.PhotoImage(img)
    Label(logged_in,image=img,bg='white').place(x=100,y=110)
    #heading
    heading=Label(logged_in,text=user_name,fg='#57a1f8',bg='white',font=('Microsoft Yahei UI Regular',15))
    heading.place(x=150,y=320)    
    heading=Label(logged_in,text="Welcome",fg='#57a1f8',bg='white',font=('Microsoft Yahei UI Regular',18))
    heading.place(x=148,y=65)
    #frame 
    frame1= Frame(logged_in,width=350,height=350,bg="white")
    frame1.place(x=500,y=120)
    heading=Label(frame1,text="Schedule Number Detail",fg='#57a1f8',bg='white',font=('Microsoft Yahei UI Light',18,'bold'))
    heading.place(x=55,y=2)
    heading1=Label(frame1,text="pls. close all word files before pdf generation",fg='#3f3f3f',bg='white',font=('Microsoft Yahei UI Light',11))
    heading1.place(x=55,y=195)
    
    SN= IntVar()      
    snEntry=Entry(frame1,width=40,textvariable=SN,fg='black',border=0,bg="white",font=('Microsoft Yahei UI Light',11))
    snEntry.place(x=55,y=100)
    snEntry.insert(0,'Enter Last 4 Digit of Schedule Number')
    snEntry.bind('<FocusIn>',on_enter)
    snEntry.bind('<FocusOut>',S_on_leave)
    Frame(frame1,width=295,height=2,bg='black').place(x=52,y=127)
      
    #pb=ttk.Progressbar(frame1,orient='horizontal',mode='indeterminate',length=240)
    #pb.grid(column=0, row=0,  padx=10, pady=20)
    #pb.grid_forget()
    #pb.place(x=80,y=220)
    
    get_pdf = partial(make_pdf,c,snEntry)
    Button(frame1,width=39,pady=7,text="Generate",bg='#57a1f8',fg='white',command=get_pdf,border=0).place(x=60,y=160)
    logged_in.mainloop()
        
#this function actually get data in dataframe and than write word file and genrate pdf
def make_pdf(c,snEntry):     
    try:
        #print(snEntry.get())
        schedule_number = str(snEntry.get())
        if len(str(schedule_number)) == 4 :
            df,df1 = login.get_data(c,schedule_number,level_add)
            #print('There are total {} Tax_invoice for schedule number {}'.format(len(df),schedule_number))
            if len(df) > 0 or len(df1)>0:
                messagebox.showinfo('information', 'There are total {} Tax_invoices and {} Credit_notes \n' 'Downloading will begin; press OK.'.format(len(df),len(df1)))
                parent_dir =os.getcwd()
                template_dir=os.path.join(parent_dir,'Template')
                directory1='Tax_invoice_'+str(date.today())+'_'+str(schedule_number)
                path1=os.path.join(parent_dir,directory1)
                directory2='Credit_notes_'+str(date.today())+'_'+str(schedule_number)
                path2=os.path.join(parent_dir,directory2)
                
                try:
                    os.mkdir(path1)
                    os.mkdir(path2)
                except OSError as error:
                    print(error)
                # print(path)
        
                pm.write_word(df,path1,parent_dir,template_dir,type='tax')
                pm.write_word(df1,path2,parent_dir,template_dir,type='credit')
                
                print('All extraction completed in {} mins'.format((timeit.default_timer()-t1)/60))
                res = messagebox.askquestion('Exit Application', 'Extraction completed\n''Want to extract more')
                if res =='no':
                   logged_in.destroy()
                else:
                    pass     
            else:
                 messagebox.showinfo('information', 'There are zero Tax_invoices/credit notes \n')        
        else:    
            messagebox.showerror('error', 'Schedule number should be only 4digit')
        
    except pyodbc.Error as ex:
            err =ex.args[0]
            print(err)
            if err == '08S01':
             messagebox.showerror('Python Error', 'Not on FGI network, Check VPN connection')        

#this function clear placeholder value
def on_enter(e):
         input = e.widget
         if input.get()=='Password':
            input.delete(0,'end')
            input.config(show='*')
         else:
              input.delete(0,'end')
                 
#these function add placeholder back
def on_leave(e):
    input =e.widget
    if input.get() == '':
            input.insert(0,'Username')
def S_on_leave(e):
    input =e.widget
    if input.get() == '':
            input.insert(0,'Enter Last 4 digit of Schedule Number')

def P_on_leave(e):
    input =e.widget
    if input.get() == '':
            input.insert(0,'Password')
            input.config(show='')

def I_on_leave(e):
    input =e.widget
    if input.get() == '':
            input.insert(0,'IP address(10.1.41.62)')

def L_on_leave(e):
    input =e.widget
    if input.get() == '':
            input.insert(0,'Level(FGGACT)')
        

t1 = timeit.default_timer()
#schedule_number =1517
parent_dir=path=directory=''

#main function

if __name__ == "__main__":
    #root =Tk()
     root = Tk()
     root.geometry("925x450+230+110")
     root.configure(bg='#fff')
     root.resizable(False,False)
     #img1=Image.open("login.png")
     img1=Image.open(resource_path("login.png"))
     img = img1.resize((450,450))
     img = ImageTk.PhotoImage(img)
     Label(root,image=img,bg='white').place(x=1,y=1)
     root.title("Tax invoice & Credit note PDF generator")
     frame= Frame(root,width=350,height=350,bg="white")
     frame.place(x=500,y=60)
     heading=Label(frame,text="Sign in",fg='#57a1f8',bg='white',font=('Microsoft Yahei UI Light',23,'bold'))
     heading.place(x=100,y=5)
     ######## user id, password, ip ,level input code
         
     ip_add= Entry(frame,width=25,fg='black',border=0,bg="white",font=('Microsoft Yahei UI Light',11))
     ip_add.place(x=30,y=80)
     ip_add.insert(0,'IP address(10.1.41.62)')
     ip_add.bind('<FocusIn>',on_enter)
     ip_add.bind('<FocusOut>',I_on_leave)
     Frame(frame,width=150,height=2,bg='black').place(x=25,y=102)
     
     level= Entry(frame,width=25,fg='black',border=0,bg="white",font=('Microsoft Yahei UI Light',11))
     level.place(x=200,y=80)
     level.insert(0,'Level(FGGACTDTA)')
     level.bind('<FocusIn>',on_enter)
     level.bind('<FocusOut>',L_on_leave)
     Frame(frame,width=120,height=2,bg='black').place(x=200,y=102)
     
     user= Entry(frame,width=25,fg='black',border=0,bg="white",font=('Microsoft Yahei UI Light',11))
     user.place(x=30,y=130)
     user.insert(0,'Username')
     user.bind('<FocusIn>',on_enter)
     user.bind('<FocusOut>',on_leave)
     Frame(frame,width=295,height=2,bg='black').place(x=25,y=152)
     
     code= Entry(frame,width=25,fg='black',border=0,bg="white",font=('Microsoft Yahei UI Light',11))
     code.place(x=30,y=160)
     code.insert(0,'Password')
     code.bind('<FocusIn>',on_enter)
     code.bind('<FocusOut>',P_on_leave)
     Frame(frame,width=295,height=2,bg='black').place(x=25,y=182)

     validateLogin = partial(check_login,user,code,ip_add,level)
     Sign_up=Button(frame,width=39,pady=7,text='Sign in',bg='#57a1f8',fg='white',border=0,command=validateLogin)
     Sign_up.place(x=35,y=214)
     
     root.mainloop()


     
