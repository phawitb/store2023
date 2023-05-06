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
# from time import sleep,time
from tkinter.font import Font
import cv2
from playsound import playsound
import os
import random
from promptpay import qrcode

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time 

SHOW_WINDOWSELINIUM = False
TIME_RESET = 60*5
INFINITY_LOOP = 5000
REFRESH_RECIEVEMONEY = False
AUTO_LOGIN = True

# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium import webdriver
# import pandas as pd

xBarcodes = []
st_barcode = time.time()
TOTAL = 0
scan_qr = False
balance_ttb = None
START = True


def infinite_loop():
    global Barcodes,xBarcodes,st_barcode,START
    # print('loop.................................................................................',current_state())
    if Barcodes != xBarcodes:
        print('barcode change!!!!'*100)
        st_barcode = time.time()
        xBarcodes = Barcodes.copy()

        if not Barcodes:
            qr_text.set('Wellcome !')
            mbtn_qr.configure(fg='white', bg='red',activebackground="red", activeforeground="white")
        else:
            if scan_qr == True:
                qr_text.set('Check Recieve money')
                mbtn_qr.configure(fg='white', bg='green',activebackground="green", activeforeground="white")
            else:
                qr_text.set('QR Scan')
                mbtn_qr.configure(fg='white', bg='blue',activebackground="blue", activeforeground="white")
                
        # if scan_qr == True and Barcodes:
        #     qr_text.set('Check Money Recieved')
        #     mbtn_qr.configure(fg='white', bg='green')
        # else:
        #     qr_text.set('QR Scan')
        #     mbtn_qr.configure(fg='white', bg='red')


    if time.time() - st_barcode > TIME_RESET:
        # Barcodes = []
        on_click('RESET')

    if True:
        print('infinite_loop....Barcodes',Barcodes)
        print('infinite_loop....xBarcodes',xBarcodes)
        print('infinite_loop....st_barcode',st_barcode)
    
    if START:
        on_click('START')
        START = False

    if scan_qr == True and Barcodes:
        if REFRESH_RECIEVEMONEY:
            on_click('QR')
    #     qr_text.set('Check Recieve money')
    #     mbtn_qr.configure(fg='black', bg='blue')
    # else:
    #     qr_text.set('Check Recieve money')
    #     mbtn_qr.configure(fg='black', bg='blue')

    
    if AUTO_LOGIN:
        if current_state() == 'relogin' or current_state() == 'error':
            on_click('GETBALANCE')

    # #relogin--------------------------------------------------------------------------------------------
    # if not Barcodes and (current_state() == 'error' or current_state() == 'relogin'):
    #     on_click('QR')
    # #----------------------------------------------------------------------------------------------------

    root.after(INFINITY_LOOP, infinite_loop)

def current_state():
    global driver
    driver.implicitly_wait(0)
    try:
        driver.find_element(By.ID, "frmIBPreLogin_txtUserId")
        return 'login'
    except:
        try:
            driver.find_element(By.ID, "vbox201224764780_lblBalanceVal")  #balance
            return 'main'
        except:
            try:
                driver.find_element(By.ID, "frmIBAccntSummary_lnkFullStatement") #รายการเดินบัญชี btn
                return 'account'
            except:
                try:
                    driver.find_element(By.ID, "frmIBAccntSummary_lnkFullStatement")  #last transaction
                    return 'transaction'
                except:
                    try:
                        driver.find_element(By.ID, "frmIBLogoutLanding_btnReLogin")  #btnReLogin
                        return 'relogin'
                    except:
                        try:
                            driver.find_element(By.ID, "hbox58865467582335_lbltransid")  #last trans
                            return 'lasttrans'
                        except:
                            return 'error'
            
def login():
    global driver
    username = "joleenfirst"
    password = "Botan.2711"

    driver.implicitly_wait(15)
    inputElement = driver.find_element(By.ID, "frmIBPreLogin_txtUserId")
    inputElement.send_keys(username)

    inputElement = driver.find_element(By.ID, "frmIBPreLogin_txtPassword")
    inputElement.send_keys(password)
    time.sleep(1)
    inputElement.send_keys(Keys.ENTER)
    time.sleep(3)
    
def get_balance():
    global driver
    current_st = current_state()
    if current_st == 'error':
        driver.close()
    
        if SHOW_WINDOWSELINIUM:
            driver = webdriver.Chrome()
        else:
            options = webdriver.ChromeOptions() 
            options.add_argument("headless")   
            driver = webdriver.Chrome(chrome_options=options)

        driver.get("https://www.ttbdirect.com/ttb/kdw1.39.2#_frmIBPreLogin")
        # driver.get("https://www.sdvsdvsdv.com")
        time.sleep(5)
        login()
    elif current_st == 'relogin':
        driver.find_element(By.ID, "frmIBLogoutLanding_btnReLogin").click()  #btnReLogin
        time.sleep(3)
        login()
    else:
        driver.find_element(By.ID, "hbxIBPostLogin_image2503629151205733").click()
        
    Bbalance = driver.find_element(By.ID, "vbox201224764780_lblBalanceVal").text  #balance
    Bbalance = float(Bbalance[:-2].replace(',',''))
    return Bbalance
    

# def start():
#     global driver
#     username = "joleenfirst"
#     password = "Botan.2711"

#     driver.implicitly_wait(15)
#     inputElement = driver.find_element(By.ID, "frmIBPreLogin_txtUserId")
#     inputElement.send_keys(username)

#     inputElement = driver.find_element(By.ID, "frmIBPreLogin_txtPassword")
#     inputElement.send_keys(password)
#     time.sleep(1)
#     inputElement.send_keys(Keys.ENTER)
#     driver.find_element(By.ID, "frmIBPostLoginDashboard_btnMenuMyActivities").click()

# def read_table():
#     global driver
#     driver.find_element(By.XPATH, "/html/body/app-root/menu-main/div[1]/main/div/div[2]/app-account-business/div/app-account-summary-main/app-recent-transaction/div/div[1]/div/form/fieldset/div/div/div/a[1]").click()
#     time.sleep(2)
#     #table
#     new_table = driver.find_element(By.XPATH, "/html/body/app-root/menu-main/div[1]/main/div/div[2]/app-account-business/div/app-account-summary-main/app-recent-transaction/div/div[3]").text
#     return new_table

# def last_transaction(new_table):
#     table = new_table.split('\n')[:-3]
#     Table = []
#     for i in range(len(table)//6):
#         Table.append(table[i*6:i*6+6])
    
#     df = pd.DataFrame(Table[1:],columns =['date','time','status','amount']+Table[0][4:])
#     return df.iloc[0]['date'],df.iloc[0]['time'],df.iloc[0]['status'],df.iloc[0]['amount']

def gen_qr(id_or_phone_number,money):
    payload = qrcode.generate_payload(id_or_phone_number)
    payload_with_amount = qrcode.generate_payload(id_or_phone_number, money)
    # export to PIL image
    # img = qrcode.to_image(payload)
    qrcode.to_file(payload_with_amount, "/home/phawit/Documents/store2022-2/imgs/qr.png")

def capture(date,id,total):
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    cv2.imwrite(f'/home/phawit/Documents/store2022-2/captures/{date}_{id}_{total}.png', frame)
    vid.release()
    
def capture2(date,id,total):
    vid = cv2.VideoCapture(2)
    ret, frame = vid.read()
    cv2.imwrite(f'/home/phawit/Documents/store2022-2/captures/products_{date}_{id}_{total}.png', frame)
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
    global TOTAL
    if table:
        N = 'Name'+' '*30
        A = ' '*5+'Amount'+' '*5
        P = ' '*5+'Price'+' '*5
        for t in [x for x in table.keys() if str(x).isdigit()]:
            N += f"\n{table[t]['name']}"
            A += f"\n{table[t]['amount']}"
            P += f"\n{table[t]['total']}"
            
        TOTAL = abs(table['total'])
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

        print(str(date_now),str(time_now))
        print('Historys',Historys)
        
        #try:
        doc_ref = db.collection(u'History').document(u'sell')
        doc_ref.update({f'{str(date_now)}.{str(time_now)}': Historys})
            # try:
            # 	capture(f'{str(date_now)}.{str(time_now)}',Historys['customer'],Historys['total'])
            # 	capture2(f'{str(date_now)}.{str(time_now)}',Historys['customer'],Historys['total'])
            # except:
            # 	print('not connect camera')           
        return 'complete'
        # except:
        #     return 'notconnectfb'
            
    else:
        return 'nointernet'

def update_img(sta):
    global TOTAL,scan_qr
    if sta == 'scanforpay' and scan_qr == True:
        gen_qr('0911971661',TOTAL)
        image = Image.open(f"/home/phawit/Documents/store2022-2/imgs/qr.png")
    else:
        image = Image.open(f"/home/phawit/Documents/store2022-2/imgs/{sta}.png")

    # image = Image.open(f"/home/phawit/Documents/store2022-2/imgs/{sta}.png")
    image = image.resize((360, 500))  #.resize((int(image.width * .5), int(image.height * .5)))
    imgTk = ImageTk.PhotoImage(image)
    img.configure(image=imgTk)
    img.image = imgTk

def on_click2(e):
    # global Barcodes
    print('22222222222222222222222',e,str(e))
    # Barcodes.append(e)
    
    on_click(e)
    
    
def on_click(e):
    global Barcodes,df_products,TOTAL,scan_qr,driver,balance_ttb,START
    print('eeeeeeeeeeeeeeeeeeeeeeeeeeee',e)

    

    if type(e) == str:
        input_text = e
    else:
        input_text = txt.get() # "0.0" get text from the beginning (from first line, first character

    if e == 'RESET':
        Barcodes = []
        scan_qr = False
    elif e == 'DELETE':
        Barcodes = Barcodes[:-1]
        if not Barcodes:
            scan_qr = False

    elif e == 'START':
        balance_ttb = get_balance()
    elif e == 'QR' and Barcodes:
        # driver = webdriver.Chrome()
        # start()
        # new_table = read_table()
        # noti = last_transaction(new_table)
        
        if balance_ttb == None:
            balance_ttb = get_balance()
        
        print('new transection',get_balance()-balance_ttb)
        print('get_balance()',get_balance(),'balance_ttb',balance_ttb)
        print('TOTAL',TOTAL,'get balance',balance_ttb,'scan_qr',scan_qr)
        if get_balance()-balance_ttb == TOTAL:
            input_text = '2874668560376'
            print('recieve money')
            status.set('recieve money')
        else:
            if status.get() == 'scan for payment':
                status.set('scan QR for payment')
            else:
                status.set('not recieve money')
                print('not recieve money')
                print('TOTAL',TOTAL,'get balance',balance_ttb,'scan_qr',scan_qr)
        
        if balance_ttb:
            QR_READY = True
            gen_qr('0911971661',TOTAL)
            scan_qr = True
            update_img('scanforpay')

        balance_ttb = get_balance()
    elif e == 'CARDPAY':
        scan_qr = False
        update_img('scanforpay')
    elif e == 'GETBALANCE':
        get_balance()

    
    print('xxxxxxxxxxx',input_text,type(input_text))
    print("str(df_products['barcode'])",list(df_products['barcode']))

    

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
            #if int(custom['balance']) >= abs(table['total']):
            if True:
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
                    arr = os.listdir('/home/phawit/Documents/store2022-2/imgs')
                    finish_sound = [x for x in arr if '.mp3' in x and 'finish' in x]
                    finish_sound = random.sample(finish_sound, 1)[0]
                    playsound(f'/home/phawit/Documents/store2022-2/imgs/{finish_sound}')
                    scan_qr = False

                    

            else:
                status.set(f"Not Enought money!   {custom['name']}  :  {custom['balance']}  ฿")
                update_img('nomoney')
                arr = os.listdir('/home/phawit/Documents/store2022-2/imgs')
                nomoney_sound = [x for x in arr if '.mp3' in x and 'nomoney' in x]
                nomoney_sound = random.sample(nomoney_sound, 1)[0]
                playsound(f'/home/phawit/Documents/store2022-2/imgs/{nomoney_sound}')

        else:
            status.set("No internet!")

    if not Barcodes:
        update_img('scanproduct')
        create_table(None)
        status.set('scan your products')
        total.set('Ready')

        qr_text.set('Wellcome !')
        mbtn_qr.configure(fg='white', bg='red')

    else:
        if scan_qr == True:
            qr_text.set('Check Recieve money')
            mbtn_qr.configure(fg='white', bg='green')
        else:
            qr_text.set('QR Scan')
            mbtn_qr.configure(fg='white', bg='blue')
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
    # txt.focus_set()  #click...................

cred = credentials.Certificate('/home/phawit/Documents/store2022-2/store2022-2-firebase-adminsdk-ccya1-c78fa5b43b.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Barcodes = []
Barcodes = []
df_customers = update_df_customers()
df_products = update_df_products()




if SHOW_WINDOWSELINIUM:
    driver = webdriver.Chrome()
else:
    options = webdriver.ChromeOptions() 
    options.add_argument("headless")   
    driver = webdriver.Chrome(chrome_options=options)




    
root = Tk()

bigFont = Font(root=root.master,family="Helvetica",size="20",weight="bold",slant="roman",underline=0,overstrike=0)
bigFont2 = Font(root=root.master,family="Helvetica",size="28",weight="bold",slant="roman",underline=0,overstrike=0)

root.option_add("*Font", "Helvetica 20")
f1 = Frame(root, bg="red")
f1.grid(row=0, column=0, columnspan=3)
f2 = Frame(root,bg='red')
f2.grid(row=1, column=0,rowspan=3)
f3 = Frame(root)
f3.grid(row=1, column=1, sticky="news",padx=30, pady=30)
f4 = Frame(root,bg="white")
f4.grid(row=1, column=2,sticky="news")
f5 = Frame(root)
f5.grid(row=3, column=0,columnspan=3)
f6 = Frame(root,bg="white")
f6.grid(row=2, column=2,sticky="news")

total = StringVar()
table = StringVar()
status = StringVar()
qr_text = StringVar()

status.set('scan your products')
total.set('Waiting...')
qr_text.set('QR Scan')


Label(f1, fg="white",bg="red",font= ('Helvetica 50 bold'),text="                         Deep Store", width=28).pack(side=LEFT,padx=5, pady=5)

txt = Entry(f1, width=30, fg="red",bg='red',highlightthickness=0)
txt.insert(END, "")
txt.focus_set()  #click...................
txt.pack(side=LEFT,padx=10, pady=10)

btn = Button(f1, text="ADD", bg="red",fg="red",highlightthickness=0)
btn.pack()
btn.bind("<Button-1>", on_click)

mbtn_qr = Button(f6, width=23,height=2,fg='white',bg='red',textvariable=qr_text,font=bigFont2,command=lambda m='QR': on_click2(m))
mbtn_qr.grid(row=1, column=1, padx=5, pady=5)
# mbtn = Button(f6, width=11,height=2,fg='white',bg='red',text='Card Pay',font=bigFont,command=lambda m='CARDPAY': on_click2(m))
# mbtn.grid(row=1, column=2, padx=5, pady=5)



Menu = []
Shortcuts = Shortcut()
print('Shortcuts',Shortcuts)
for i in range(16):
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
    
img = Label(f4,borderwidth=0)
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

root.after(INFINITY_LOOP, infinite_loop)

root.mainloop()



