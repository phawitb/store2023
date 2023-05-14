import cv2
import numpy as np
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
# import cv2
import pytesseract
import os
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import requests

cred = credentials.Certificate('store2022-2-firebase-adminsdk-ccya1-c78fa5b43b.json')

try:
    firebase_admin.initialize_app(cred)
except:
    pass
db = firestore.client()

def linenotify(message,img_path):
    url = 'https://notify-api.line.me/api/notify'
    token = 'eksfQt5hl807nYbMMOmru9XYHn7LAPA47ql9DP5Zwdz' # Line Notify Token
    data = {'message': message}
    headers = {'Authorization':'Bearer ' + token}
    session = requests.Session()
    
    if img_path:
        img = {'imageFile': open(img_path,'rb')} #Local picture File
        session_post = session.post(url, headers=headers, files=img, data =data)
    else:
        session_post = session.post(url, headers=headers, data =data)
    print(session_post.text)

def topup_current():
    ref = db.collection(u'topup').document(u'current')
    doc = ref.get().to_dict()
    current_id = doc['id']
    current_exist = doc['exist']
    return current_id,current_exist

def update_qr(token,amount,customer_id,current_exist):
    doc_ref = db.collection(u'topup').document(u'qr_token')
    H = {
        'date' : time.time(),
        'amount' : amount,
        'customer_id' : customer_id
    }
    doc_ref.update({f"{token}" : H})
    
    # current_id,current_exist = topup_current()
    doc_ref = db.collection(u'topup').document(u'current')
    H = current_exist + '|' + token
    doc_ref.update({f"exist" : H})

def update_balace(customer_id,money,time_now,date_now):
    ref = db.collection(u'customers').document(f'{customer_id}')
    c = ref.get().to_dict()
    c['balance'] = int(c['balance']) + int(money)

    sign = '+'
    if money < 0:
      sign = '-'
    h = f"{date_now[6:]}/{date_now[4:6]}/{date_now[:4]}-{time_now[:2]}:{time_now[2:4]}:{time_now[4:6]}|{sign}{money}|{c['balance']}||"
    if 'history' in c.keys():
        c['history'] = c['history'] + h
    else:
        c['history'] = h
    
    ref.set(c)

    return c['balance']

def topup_db(total,customer_id,balance,time_now,date_now):
  # time_now = datetime.now().strftime("%H%M%S%f")
  # date_now = datetime.now().strftime("%Y%m%d")

  Historys = {
      'total': total,
      'customer':customer_id,
      'balance':balance,
  }

  doc_ref = db.collection(u'History').document(u'topup')
  print("{f'{str(date_now)}.{str(time_now)}': Historys}",{f'{str(date_now)}.{str(time_now)}': Historys})
  try:
    doc_ref.update({f'{str(date_now)}.{str(time_now)}': Historys})
  except:
    c = {}
    c[str(date_now)] = {
        str(time_now) : Historys
    }
    doc_ref.set(c)

def add_money(addmoney_df):
    #drop 'total' row 
    # addmoney_df = addmoney_df[addmoney_df.name != 'Total']
    # # addmoney_df

    # #add_id_from_db
    # docs = db.collection(u'customers').stream()
    # for doc in docs:
    #     # print(doc.id,doc.to_dict()['name'])
    #     addmoney_df.loc[addmoney_df.name == doc.to_dict()['name'], "id"] = doc.id

    # #check all name exist in db
    # try:
    #     if addmoney_df['id'].isnull().sum() == 0:
    #         ok = True
    #         print('all name exist in db:',ok)
    #     else:
    #         print('NOT! all name exist in db:',ok)
    #         ok = False
    #         return 'NOT! all name exist in db'
    # except:
    #     return 'NOT! all name exist in -->Pleasw Update Customers'
        

    #add money to db
    if True:
        for index, row in addmoney_df.iterrows():
            # print("row['money']",row['money'],type(row['money']))
            # if int(row['money']) != 0:
            if str(row['money']) != 'nan':
                # time_now = datetime.now().strftime("%H%M%S%f")
                # date_now = datetime.now().strftime("%Y%m%d")
                time_now = datetime.now(tz=timezone(timedelta(hours = 7))).strftime("%H%M%S%f")
                date_now = datetime.now(tz=timezone(timedelta(hours = 7))).strftime("%Y%m%d")

                balance = update_balace(row['id'],int(row['money']),time_now,date_now)
                topup_db(row['money'],row['id'],balance,time_now,date_now)
                print(row['name'], row['money'],balance)
            
        print('complete...')
        return 'complete...'


def OCR(path):
    def ocr_thai(img_path):
        img = cv2.imread(img_path)
        custom_config = r'-l tha --oem 3 --psm 6 -c language_model_ngram_space_delimited_language=1'
        text = pytesseract.image_to_string(img, config=custom_config)
        return text

    def ocr_eng(img_path):
        img = cv2.imread(img_path)
    #     custom_config = r'-l tha --oem 3 --psm 6 -c language_model_ngram_space_delimited_language=1'
        text = pytesseract.image_to_string(img)
        return text
    
    def read_qr_code(filename):
        try:
            img = cv2.imread(filename)
            detect = cv2.QRCodeDetector()
            value, points, straight_qrcode = detect.detectAndDecode(img)
            return value
        except:
            return None
        
    date_now = datetime.now(tz=timezone(timedelta(hours = 7))).strftime("%Y%m%d")
    
    ocr_thai_raw = ocr_thai(path)
    ocr_eng_raw = ocr_eng(path)
    
    ocr_thai = ocr_thai_raw.split('\n')
    ocr_eng = ocr_eng_raw.split('\n')
    
    #ref
    ref = None
    for i in ocr_eng:
        if date_now[:-2] in i:
            ref = i
            ref = ref.split()
            ref = [x for x in ref if date_now[:-2] in x][0]
            break
    if not ref:
        N_digit = []
        for i in ocr_eng:
            n_digit = sum(c.isdigit() for c in i)
            N_digit.append(n_digit)
        idx = N_digit.index(max(N_digit))
        ref = ocr_eng[idx]
        
    #amount
    amount = []
    for i in ocr_thai:
        if 'นวน' in i or 'บาท' in i:
            amount += i.split()
            
    if not amount:
        a = ocr_eng_raw.split('Amount')
        a = a[1].split('\n')
        a = [x for x in a if '.' in x]
        print('a',a)
        amount = a
        
    a = []
    for i in amount:
        a += i.split()
    amount = a
    amount = [x for x in a if '.' in x]
    for i in amount:
        try:
            if float(i) != 0:
                amount = float(i)
        except:
            pass
        
    #check target
    target = [x for x in ocr_thai if 'อธิศมา' in x]
    if not target:
        target = [x for x in ocr_eng if 'ATISMA' in x]
    if target:
        target = True
    else:
        target = False
        
        
    #date
    date = None
    if date_now[:-2] in ref:
        date = date_now[:4] + ref.split(date_now[:4])[1][:4]
#     if not date:
#         date = [x for x in ocr_thai if ':' in x]
#         d = []
#         for i in date:
#             d += i.split()
#         date = d
#         date = [x for x in date if ':' in x]

    #qr
    qr = read_qr_code(path)
                        
    print('ocr_thai:',ocr_thai)
    print('\nocr_eng:',ocr_eng)
    print('\nref:',ref)
    print('amount',amount)
    print('date',date)
    print('target',target)
    print('qr',qr)
    
    return qr,ref,date,target,amount
        
    # return qr,rr,date,sent_person,amount

# def ocr(opencv_image):
#     complete = True
#     qr_token = 'token12412423423qr'
#     money = 12

#     return complete,qr_token,money

uploaded_file = st.file_uploader("Choose a image file", type=["jpg",'jpeg','png','HEIC'])

if uploaded_file is not None:
    # Convert the file to an opencv image.
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)

    # cv2.imwrite('img/current_slip.jpg', opencv_image)

    # Now do something with the image! For example, let's display it:
    st.image(opencv_image, channels="BGR")

    id_name = st.text_input('input your ID name')
    if st.button('submit'):

        # complete,qr_token,money = ocr(opencv_image)
        

        # qr,rr,date,sent_person,amount = OCR('img/current_slip.jpg')

        #step1 write current
        #check exist id
        docs = db.collection(u'customers').stream()
        ID_NAME = []
        ID = []
        for doc in docs:
            ID_NAME.append(doc.to_dict()['name'])  #doc.id
            ID.append(doc.id)

        if id_name in ID_NAME:
            st.write(f'id {id_name} exist,ok')
            #write current_id
            

            #check current id is me
            # ref = db.collection(u'topup').document(u'current')
            # doc = ref.get().to_dict()
            # current_id = doc['id']
            current_id,current_exist = topup_current()
            if current_id != -1:
                doc_ref = db.collection(u'topup').document(u'current')
                doc_ref.update({f"id" : id_name})

                current_id = id_name
                if current_id == id_name:
                    # st.write('is me')
                    cv2.imwrite('img/current_slip.jpg', opencv_image)
                    qr,rr,date,sent_person,amount = OCR('img/current_slip.jpg')

                    msg = f'{id_name},{qr},{rr},{date},{sent_person},{amount}/{ID_NAME.index(id_name)}/{ID[ID_NAME.index(id_name)]}'
                    # st.write(msg)

                    customer_id = ID[ID_NAME.index(id_name)]

                    if qr not in current_exist.split('|'):
                        # st.write(f"Not ever seen slip {customer_id} not in {current_exist.split('|')}")

                        print('-'*100)
                        
                        data = [[customer_id, id_name,int(float(amount))]]
                        df = pd.DataFrame(data, columns=['id', 'name','money'])
                        # st.write(df)

                        sta = add_money(df)

                        update_qr(qr,amount,customer_id,current_exist)

                        doc_ref = db.collection(u'topup').document(u'current')
                        doc_ref.update({f"id" : -1})
                        

                        msg = f"Add Money {sta}, {id_name} = +{int(float(amount))} BATH"
                        st.write(msg)
                        linenotify(msg,"img/current_slip.jpg")
                        # os.remove("img/current_slip.jpg")

                    else:
                        msg = f"Ever seen slip!!!{id_name}"
                        st.write(msg)
                        linenotify(msg,"img/current_slip.jpg")
                        # st.write(f"Ever seen slip {customer_id} in {current_exist.split('|')}")

                else:
                    msg = f'Try again later!{id_name}'
                    st.write(msg)
                    linenotify(msg,None)

            else:
                msg = f'Busy!Try again later!{id_name}'
                st.write(msg)
                linenotify(msg,None)



        else:
            msg = f'customer id : {id_name} >> not exist'
            st.write(msg)
            linenotify(msg,None)

        doc_ref = db.collection(u'topup').document(u'current')
        doc_ref.update({f"id" : ""})
        




        # msg = f'{qr},{rr},{date},{sent_person},{amount}'
        # st.write(msg)
# st.write('The current movie title is', title)