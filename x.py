from tkinter import *
import cv2
from PIL import Image, ImageTk
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from ffpyplayer.player import MediaPlayer


cred = credentials.Certificate('store2022-2-firebase-adminsdk-ccya1-c78fa5b43b.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

player = None

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
    print(N,A,P)
    total.set(f"Balance {b} ฿")
    table_name.set(N)
    table_amount.set(A)
    table_price.set(P)

#-------------------------------------------

def on_click(event):
    global cap,player

    input_barcode=txt.get()
    print("input txt : " + input_barcode)
    input_txt.set("")
    if input_barcode in list(df_customers['id']):
        create_table2(input_barcode)
    elif input_barcode in [x.split('.')[0] for x in os.listdir('vdo')]:
        print('-'*1000)
        vdo_file = [x for x in os.listdir('vdo') if input_barcode in x][0]
        cap = cv2.VideoCapture(f'vdo/{vdo_file}')
        
        player = MediaPlayer(f'vdo/{vdo_file}')


def update_frame():
    global cap,player
    
    ret, frame = cap.read()

    # if player:
    #     audio_frame,val = player.get_frame()
    # print('ret',ret)
    if not ret:
        print('not ret.........')
        cap = cv2.VideoCapture(0)

    if ret:
        if player:
            audio_frame,val = player.get_frame()

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # print('frame_rgb.shape',frame_rgb.shape)
        frame_rgb = cv2.resize(frame_rgb, (1280, 960))
 
        # cv2.waitKey(60)

        image = Image.fromarray(frame_rgb)
        image_tk = ImageTk.PhotoImage(image)

        camera_label.configure(image=image_tk)
        camera_label.image = image_tk

        # #update table
        # N = 'Name                     \nปากกายี่ห้อabcd\nbbb'
        # A = 'Amount\n5\n3'
        # P = 'Bath\n25\n39'

        # table_name.set(N)
        # table_amount.set(A)
        # table_price.set(P)
        # #update total
        # total.set('12312')
        # status.set('axasxas')
        # #update stus buttom
        # status_buttom.set('bbbbb')

    camera_label.after(5, update_frame)

#-------------------------------------------------------

df_customers = update_df_customers()
df_products = update_df_products()

root = Tk()
root.geometry("200x100")

f0 = Frame(root, background="yellow", width=10, height=10,padx=650, pady=5)
f1 = Frame(root, background="bisque", width=10, height=10)
f2 = Frame(root, background="pink", width=10, height=10,padx=25, pady=5)
f3 = Frame(root, background="blue", width=10, height=10)
f4 = Frame(root, background="green", width=10, height=10)
f5 = Frame(root, background="black", width=10, height=10)

f0.grid(row=0, column=0,columnspan=2, sticky="nsew")
f1.grid(row=1, column=0,rowspan=3, sticky="nsew")
f2.grid(row=1, column=1, sticky="nsew")
f3.grid(row=2, column=1, sticky="nsew")
f4.grid(row=3, column=1, sticky="nsew")
f5.grid(row=4, column=0,columnspan=2, sticky="nsew")

#-------------------------------------------------------
#head
Label(f0, fg="yellow",bg="red",font= ('Helvetica 60 bold'),text="Deep Store").pack(side=LEFT,padx=5, pady=5)

input_txt =  StringVar()
txt = Entry(f0, width=1, fg="red",bg='red',textvariable=input_txt)
txt.insert(END, "")
txt.focus_set()  #click...................
txt.pack(side=LEFT,padx=1, pady=1)

btn = Button(f0, text="A", bg="red",fg="red",highlightthickness=0)
btn.pack(side=LEFT,padx=1, pady=1)  #.pack()
btn.bind("<Button-1>", on_click)


#camera
camera_label = Label(f1)
camera_label.pack(fill=X,padx=10, pady=50)   #.pack()

#table
# Label(f2, text='',width=40,justify="left").pack(anchor=W)
table_name = StringVar()
table_amount = StringVar()
table_price = StringVar()

Label(f2, textvariable=table_name,font='Helvetica 25',justify=LEFT).pack(side=LEFT,anchor=N)
Label(f2, textvariable=table_amount,font='Helvetica 25').pack(side=LEFT,anchor=N)
Label(f2, textvariable=table_price,font='Helvetica 25').pack(side=LEFT,anchor=N)

#total
total = StringVar()
Label(f3, textvariable=total,fg='red',bg='white',font= ('Helvetica 50 bold')).pack(fill=X,padx=10, pady=40)

#status
status = StringVar()
Label(f4, textvariable=status,fg='blue',font= ('Helvetica 40 bold')).pack(fill=X,padx=10, pady=40)

#buttom
status_buttom = StringVar()
Label(f5, textvariable=status_buttom,fg='blue',font= ('Helvetica 50 bold')).pack(fill=X,padx=10, pady=5)

#-------------------------------------------------------
root.grid_columnconfigure(0, weight=3,uniform=True)
root.grid_columnconfigure(1, weight=1,uniform=True)
root.grid_rowconfigure(0, weight=1,uniform=True)
root.grid_rowconfigure(1, weight=4,uniform=True)
root.grid_rowconfigure(2, weight=1,uniform=True)
root.grid_rowconfigure(3, weight=1,uniform=True)
root.grid_rowconfigure(4, weight=1,uniform=True)



root.bind('<Return>',on_click)
root.attributes("-fullscreen", True)


cap = cv2.VideoCapture(0)
update_frame()

root.mainloop()

cap.release()
cv2.destroyAllWindows()


