from tkinter import *
from tkinter.font import Font
import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
# from datetime import datetime
from datetime import datetime, timezone, timedelta
import urllib.request
from time import sleep,time
from tkinter.font import Font
import cv2
from playsound import playsound
import os
import random

def capture(date,id,total):
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    cv2.imwrite(f'captures/{date}_{id}_{total}.png', frame)
    vid.release()
    
def capture2(date,id,total):
    vid = cv2.VideoCapture(2)
    ret, frame = vid.read()
    cv2.imwrite(f'captures/products_{date}_{id}_{total}.png', frame)
    vid.release()

def create_history(Barcodes):
  B = []
  for b in Barcodes:
    if b not in B:
      B.append(b)
  History = {}
  Total = 0
  for i,b in enumerate(B):
    print('bbbbbb',b)
    p = df_products.loc[df_products['barcode'] == b]
    print('ppppp',p)
    # print(list(p['barcode'])[0],list(p['name'])[0],list(p['price'])[0],Barcodes.count(b))
    History[str(i)] = {
        'barcode': list(p['barcode'])[0],
        'name':list(p['name'])[0],
        'price':list(p['price'])[0],
        'amount':Barcodes.count(b),
        'total': list(p['price'])[0]*Barcodes.count(b)
    }
    Total += list(p['price'])[0]*Barcodes.count(b)
  History['total'] = Total*-1
  return History

def internet_connection():
    try:
        urllib.request.urlopen("http://www.google.com")
        return True
    except:
        return False

def Shortcut():
  shortcut = db.collection(u'setup').document(f'shortcut').get().to_dict()
  Shortcut = {}
  for s in shortcut:
    barcode = shortcut[s]
    products = db.collection(u'products').document(barcode).get().to_dict()
    # products['key'] = s
    products['barcode'] = barcode
    Shortcut[s] = products
  return Shortcut

def update_df_customers():
  data = []
  docs = db.collection(u'customers').stream()
  for doc in docs:
      # print(f"{doc.id} => {doc.to_dict()['name']}")
      data.append([doc.id,doc.to_dict()['name']])
  df_customers = pd.DataFrame((data),columns=['id', 'name'])
  return df_customers

def update_df_products():
  data = []
  docs = db.collection(u'products').stream()
  for doc in docs:
      # print(f"{doc.id} => {doc.to_dict()['name']}")
      data.append([doc.id,doc.to_dict()['name'],doc.to_dict()['price']])
  df_customers = pd.DataFrame((data),columns=['barcode','name','price'])
  return df_customers

def create_table2(customer_id):
    ref = db.collection(u'customers').document(f'{customer_id}')
    c = ref.get().to_dict()
    items = [x.split('|') for x in c['history'].split('||')][:-1]
    if len(items)>10:
        items = items[-10:]
    N = 'Date'+' '*30
    A = ' '*5+'Money'+' '*5
    P = ' '*5+'Balance'+' '*5
    for t in items:
        N += f"\n{t[0]}"
        A += f"\n{t[1]}"
        P += f"\n{t[2]}"
        b = t[2]
    total.set(f"Balance {b} ฿")
    table_name.set(N)
    table_amount.set(A)
    table_price.set(P)


def create_table(table):
    if table:
        N = 'Name'+' '*30
        A = ' '*5+'Amount'+' '*5
        P = ' '*5+'Price'+' '*5
        for t in [x for x in table.keys() if str(x).isdigit()]:
            N += f"\n{table[t]['name']}"
            A += f"\n{table[t]['amount']}"
            P += f"\n{table[t]['total']}"
            
        total.set(f"Total {abs(table['total'])}")
        table_name.set(N)
        table_amount.set(A)
        table_price.set(P)
    else:
        total.set("")
        table_name.set("")
        table_amount.set("")
        table_price.set("")

#     table_name.set('Name'+' '*30+'\naaaaa\nss\nvrrrr')
#     table_amount.set(' '*5+'Amount'+' '*5+'\n1\n20\n100')
#     table_price.set(' '*5+'Price'+' '*5+'\n30\n5\n500')

def update_balace(customer_id,money,time_now,date_now):
    ref = db.collection(u'customers').document(f'{customer_id}')
    c = ref.get().to_dict()
    c['balance'] = int(c['balance']) + money

    h = f"{date_now[6:]}/{date_now[4:6]}/{date_now[:4]}-{time_now[:2]}:{time_now[2:4]}:{time_now[4:6]}|{money}|{c['balance']}||"
    if 'history' in c.keys():
        c['history'] = c['history'] + h
    else:
        c['history'] = h
    
    ref.set(c)

    return c['balance']

def customer_detail(customer_id):
    ref = db.collection(u'customers').document(f'{customer_id}')
    return ref.get().to_dict()

def save_history2(Historys,time_now,date_now):
    # time_now = datetime.now().strftime("%H%M%S%f")
    # date_now = datetime.now().strftime("%Y%m%d")

    print('Historys',Historys)

    if internet_connection():
    
    	#update current stock
        for i in [x for x in Historys.keys() if x.isnumeric()]:
            ref = db.collection(u'stocks').document('current')
            try:
                n = ref.get().to_dict()[Historys[i]['barcode']]
            except:
                n = 0
            ref.update({Historys[i]['barcode']:n+Historys[i]['amount']*-1})
        #----------------------------
        
        try:
            doc_ref = db.collection(u'History').document(u'sell')
            try:
                doc_ref.update({f'{str(date_now)}.{str(time_now)}': Historys})
            except:
                H = {}
                H[str(date_now)] = {
                    str(time_now) : Historys
                }
                    
                doc_ref.set(H)
            capture(f'{str(date_now)}.{str(time_now)}',Historys['customer'],Historys['total'])
            try:
                capture2(f'{str(date_now)}.{str(time_now)}',Historys['customer'],Historys['total'])
                
            except:
                pass           
            return 'complete'
        except Exception as e:
            print(e)
            return 'notconnectfb'
            
    else:
        return 'nointernet'

def update_img(sta):
    # if input_text:
    #     sta = 'scanforpay'
    # else:
    #     sta = 'scanproduct'
    image = Image.open(f"imgs/{sta}.png")
    image = image.resize((450, 500))  #.resize((int(image.width * .5), int(image.height * .5)))
    imgTk = ImageTk.PhotoImage(image)
    img.configure(image=imgTk)
    img.image = imgTk

def on_click2(e):
    # global Barcodes
    print('22222222222222222222222',e,str(e))
    # Barcodes.append(e)
    
    on_click(e)
    
    
def on_click(e):
    global Barcodes,df_products
    print('eeeeeeeeeeeeeeeeeeeeeeeeeeee',e)
    if type(e) == str:
        input_text = e
    else:
        input_text = txt.get() # "0.0" get text from the beginning (from first line, first character

    if e == 'RESET':
        Barcodes = []
    elif e == 'DELETE':
        Barcodes = Barcodes[:-1]
    
    print('xxxxxxxxxxx',input_text,type(input_text))
    print("str(df_products['barcode'])",list(df_products['barcode']))

    if not Barcodes:
        update_img('scanproduct')
        create_table(None)
        status.set('scan your products')
        total.set('Ready')

    if str(input_text) in list(df_products['barcode']) or e == 'DELETE' and Barcodes:
        print('zzzzzzzz',input_text)
        if e != 'DELETE':
            Barcodes.append(input_text)
        table = create_history(Barcodes)
        create_table(table)
        update_img('scanforpay')
        status.set('scan for payment')
    
    elif str(input_text) in list(df_customers['id']) and not Barcodes:
        status.set('show history data')
        create_table2(str(input_text))
        

    elif str(input_text) in list(df_customers['id']) and Barcodes:
        if internet_connection():
            customer_barcode = str(input_text)
            print('customer_barcode',customer_barcode)
            custom = customer_detail(customer_barcode)
            customer = custom['name'] + ' : ' + str(custom['balance'])
            table = create_history(Barcodes)
            print('customer',customer)
            print("table['Total']",table['total'])
            if int(custom['balance']) >= abs(table['total']):
                time_now = datetime.now().strftime("%H%M%S%f")
                date_now = datetime.now().strftime("%Y%m%d")
                balance = update_balace(customer_barcode,table['total'],time_now,date_now)
                table['balance'] = balance
                table['customer'] = customer_barcode
                
                sta = save_history2(table,time_now,date_now)
                print('sta',sta)
                if sta == 'complete':
                    Barcodes = []
                    update_img('finish')
                    status.set(f"{custom['name']} Balance : {custom['balance']+table['total']} ฿")
                    total.set(f"Finish! {table['total']} ฿")
                    arr = os.listdir('imgs')
                    finish_sound = [x for x in arr if '.mp3' in x and 'finish' in x]
                    finish_sound = random.sample(finish_sound, 1)[0]
                    playsound(f'imgs/{finish_sound}')

                    

            else:
                status.set(f"Not Enought money!   {custom['name']}  :  {custom['balance']}  ฿")
                update_img('nomoney')
                arr = os.listdir('imgs')
                nomoney_sound = [x for x in arr if '.mp3' in x and 'nomoney' in x]
                nomoney_sound = random.sample(nomoney_sound, 1)[0]
                playsound(f'imgs/{nomoney_sound}')

        else:
            status.set("No internet!")
        # sleep(5)
        # create_table(None)
        


    
    

    
    # table = {0: {'amount': 1,
    #   'barcode': '8851123341011',
    #   'name': 'babymind powder',
    #   'price': 10,
    #   'total': 10},
    #  1: {'amount': 2,
    #   'barcode': '8858891302701',
    #   'name': 'เย็นเย็น เหลือง',
    #   'price': 10,
    #   'total': 20},
    #  'Total': 30}
    # Barcodes = ['8851123341011','8858891302701','8858891302701']
    # table = create_history(Barcodes)
    # create_table(table)

#     total.set('25')
    
#     table_name.set('Name'+' '*30+'\naaaaa\nss\nvrrrr')
#     table_amount.set(' '*5+'Amount'+' '*5+'\n1\n20\n100')
#     table_price.set(' '*5+'Price'+' '*5+'\n30\n5\n500')
    
    # status.set('scan for payment')
    
    txt.delete(0, END)

cred = credentials.Certificate('store2022-2-firebase-adminsdk-ccya1-c78fa5b43b.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Barcodes = []
Barcodes = []
df_customers = update_df_customers()
df_products = update_df_products()



    
root = Tk()

bigFont = Font(root=root.master,family="Helvetica",size="20",weight="bold",slant="roman",underline=0,overstrike=0)

root.option_add("*Font", "Helvetica 20")
f1 = Frame(root, bg="red")
f1.grid(row=0, column=0, columnspan=3)
f2 = Frame(root,bg='red')
f2.grid(row=1, column=0)
f3 = Frame(root)
f3.grid(row=1, column=1, sticky="news",padx=30, pady=30)
f4 = Frame(root,bg="white")
f4.grid(row=1, column=2,sticky="news")
f5 = Frame(root)
f5.grid(row=3, column=0,columnspan=3)

total = StringVar()
table = StringVar()
status = StringVar()

status.set('scan your products')
total.set('Ready')



# Label(f1, text="Barcode", width=25).pack(side=LEFT,padx=10, pady=10)

# txt = Entry(f1, width=30, fg="green")
# txt.insert(END, "")
# txt.focus_set()  #click...................
# txt.pack(side=LEFT,padx=10, pady=10)

Label(f1, fg="white",bg="red",font= ('Helvetica 50 bold'),text="Deep Store", width=23).pack(side=LEFT,padx=5, pady=5)

txt = Entry(f1, width=30, fg="red",bg='red')
txt.insert(END, "")
txt.focus_set()  #click...................
txt.pack(side=LEFT,padx=10, pady=10)

btn = Button(f1, text="ADD", bg="gold")
btn.pack()
btn.bind("<Button-1>", on_click)

Menu = []
Shortcuts = Shortcut()
print('Shortcuts',Shortcuts)
for i in range(18):
    if str(i+1) in Shortcuts.keys():
        Menu.append(Shortcuts[str(i+1)]['name'])
    else:
        Menu.append("")
Menu.append('RESET')
Menu.append('DELETE')

mbtn = []
for i,menu in enumerate(Menu):
    # mbtn = Button(f2, text=menu,width=8)
    # mbtn.grid(row=i//2, column=i%2, padx=5, pady=5)
    # mbtn.bind("<Button-1>", on_click2)
    fg = 'black'
    bg='white'
    if str(i+1) in Shortcuts.keys():
        btn_detail = Shortcuts[str(i+1)]['barcode']
    elif menu == 'RESET':
        btn_detail = 'RESET'
        fg = 'white'
        bg='red'
    elif menu == 'DELETE':
        btn_detail = 'DELETE'
        fg = 'white'
        bg='red'
    else:
        btn_detail = 'notset'
 
    mbtn = Button(f2, width=11,height=2,fg=fg,bg=bg,text=menu,font=bigFont,command=lambda m=btn_detail: on_click2(m))
    mbtn.grid(row=i//2, column=i%2, padx=5, pady=5)

# Label(f3, text='Products',justify="left").pack(anchor=W)
Label(f3, text='',width=40,justify="left").pack(anchor=W)

table_name = StringVar()
table_amount = StringVar()
table_price = StringVar()
Label(f3, textvariable=table_name,justify=LEFT).pack(side=LEFT,anchor=N)
Label(f3, textvariable=table_amount).pack(side=LEFT,anchor=N)
Label(f3, textvariable=table_price).pack(side=LEFT,anchor=N)

    
img = Label(f4)
img.pack()
update_img('scanproduct')

Label(f4, textvariable=total,fg='red',bg='white',font= ('Helvetica 40 bold')).pack(fill=X,padx=10, pady=10)
Label(f5, textvariable=status,fg='blue',font= ('Helvetica 30 bold')).pack(fill=X,padx=10, pady=5)


root.bind('<Return>',on_click)
# root.bind("<->", on_click('DELETE'))

root.attributes("-fullscreen", True)
root.bind("<F11>", lambda event: root.attributes("-fullscreen",
                                    not root.attributes("-fullscreen")))
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

root.mainloop()
