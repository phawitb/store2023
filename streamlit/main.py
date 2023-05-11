import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
# from datetime import datetime
from datetime import datetime, timezone, timedelta
import time

def update_shortcut(C):
  print(C)
  ref = db.collection(u'setup').document('shortcut')
  ref.set(C)

def update_customers(barcode,name):
  ref = db.collection(u'customers').document(f'{barcode}')
  c = ref.get().to_dict()
  if not c:
    c = {}
    c['name'] = name
    c['balance'] = 0
    c['history'] = ''
    ref.set(c)

def all_addstock_exist(addstock_df):
  docs = db.collection(u'products').stream()
  products_id = []
  for doc in docs:
    products_id.append(doc.id)
  for i in addstock_df['barcode']:
    if i not in products_id:
      return False
  return True
  
def update_current_stock(barcode,amount):
  ref = db.collection(u'stocks').document('current')
  if str(amount) == 'nan':
    amount = 0
  print('amount',amount,type(amount))
  try:
    ref.update({barcode:ref.get().to_dict()[barcode]+int(amount)})
  except:
    try:
        ref.update({barcode:int(amount)})
    except:
        c = ref.get().to_dict()
        if not c:
            c = {}
        try:
            c[barcode] = int(amount)
        except:
            c[barcode] = 0
        ref.set(c)

def update_history_stock(H):
  time_now = datetime.now(tz=timezone(timedelta(hours = 7))).strftime("%H%M%S%f")
  date_now = datetime.now(tz=timezone(timedelta(hours = 7))).strftime("%Y%m%d")

  doc_ref = db.collection(u'History').document(u'addstock')
  # doc_ref.update({date_now:{time_now:H}})
  try:
    doc_ref.update({f'{str(date_now)}.{str(time_now)}': H})
  except:
    hh = {}
    hh[str(date_now)] = {
        str(time_now) : H
    }
    doc_ref.set(hh)

def update_products(barcode,name,price):
  ref = db.collection(u'products').document(f'{barcode}')
  c = ref.get().to_dict()
  if not c:
    c = {}
  c['name'] = name
  c['price'] = price
  ref.set(c)

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

# topup_db(10,'7986925784557',balance)

def check_balance(customer_id):
    ref = db.collection(u'customers').document(f'{customer_id}')
    return ref.get().to_dict()
# check_balance('1737180942647')

def get_stock():
    ref = db.collection(u'stocks').document('current')
    S = ref.get().to_dict()
    
    col_1 = []
    col_2 =[]
    for s in S.keys():
        col_1.append(s)
        col_2.append(S[s])
    data = {'barcode': col_1, 'amount': col_2}
    df = pd.DataFrame.from_dict(data)
    df = df.sort_values(["amount"],ascending=False)
    return df


def get_all_balance():
    docs = db.collection(u'customers').stream()
    S = []
    for doc in docs:
        s = doc.to_dict()
        s['id'] = doc.id
        S.append(s)
        # print(f'{doc.id} => {doc.to_dict()}')
        # print(type(doc.to_dict()))
    # print(S)
    df = pd.DataFrame.from_dict(S)
    cols = ['id','name','balance']
    df = df[cols] 
    return df

def add_money(addmoney_df):
    #drop 'total' row 
    addmoney_df = addmoney_df[addmoney_df.name != 'Total']
    # addmoney_df

    #add_id_from_db
    docs = db.collection(u'customers').stream()
    for doc in docs:
        # print(doc.id,doc.to_dict()['name'])
        addmoney_df.loc[addmoney_df.name == doc.to_dict()['name'], "id"] = doc.id

    #check all name exist in db
    try:
        if addmoney_df['id'].isnull().sum() == 0:
            ok = True
            print('all name exist in db:',ok)
        else:
            print('NOT! all name exist in db:',ok)
            ok = False
            return 'NOT! all name exist in db'
    except:
        return 'NOT! all name exist in -->Pleasw Update Customers'
        

    #add money to db
    if ok:
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

def findProductName(barcode):
    ref = db.collection(u'products').document(barcode)
    name = ref.get().to_dict()['name']
    return name


print('start....')

##===========================================================================================
try:
    cred = credentials.Certificate('store2022-2-firebase-adminsdk-ccya1-c78fa5b43b.json')
    firebase_admin.initialize_app(cred)
except:
    pass

db = firestore.client()
# bal = check_balance('2874668560376')

try:
    df_stock = get_stock()
    print(df_stock)

    df_stock['name'] = [findProductName(x) for x in df_stock['barcode']]
    df_stock = df_stock[['barcode', 'name', 'amount']]
    

    st.write("## Current Stock")
    #df_stock = df_stock.applymap(str)
    #df_stock = df_stock.drop(columns=['barcode'])
    st.write(df_stock.to_html(escape=False), unsafe_allow_html=True)
except:
    pass
##----------------------------------------------------------------------
try:
    df_balance = get_all_balance()
    df_balance = df_balance.sort_values(["name"])  #,ascending=False

    st.write("## All Balance")
    st.write(df_balance.to_html(escape=False), unsafe_allow_html=True)
except:
    pass


##----------------------------------------------------------------------
st.write('***')

st.write('## Add Money')
sheet_url = 'https://docs.google.com/spreadsheets/d/1y7ioKeDwksad6LBjOBD65N2jlqsj04Q3xEtq1oZnaig/edit#gid=0'
st.write(sheet_url)
if st.button('Add Money'):
    # sheet_url = 'https://docs.google.com/spreadsheets/d/1y7ioKeDwksad6LBjOBD65N2jlqsj04Q3xEtq1oZnaig/edit#gid=0'
    url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    addmoney_df = pd.read_csv(url)

    B = []
    for x in addmoney_df['barcode']:
        try:
            B.append(str(int(x)))
        except:
            B.append(None)
    addmoney_df['barcode'] = B
    st.write(addmoney_df)

    sta = add_money(addmoney_df)
    st.write(sta,time.time())
    st.write(f'Clear data -->{sheet_url}')

##----------------------------------------------------------------------
st.write('## Add Stock')
sheet_url = 'https://docs.google.com/spreadsheets/d/1FWYRTRhGqz4XfE0SXrMNhtzKLfhcMLxgCkA36iRiEHo/edit#gid=0'
st.write(sheet_url)
if st.button('Add Stock'):
    # sheet_url = 'https://docs.google.com/spreadsheets/d/1FWYRTRhGqz4XfE0SXrMNhtzKLfhcMLxgCkA36iRiEHo/edit#gid=0'
    url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    addstock_df = pd.read_csv(url)
    addstock_df['barcode'] = addstock_df['barcode'].apply(str)
    st.write(addstock_df.to_html(escape=False), unsafe_allow_html=True)

    if all_addstock_exist(addstock_df):
        print('all_addstock_exist')
        st.write('all_addstock_exist')
        H = {}
        for index, row in addstock_df.iterrows():
            time_now = datetime.now(tz=timezone(timedelta(hours = 7))).strftime("%H%M%S%f")
            date_now = datetime.now(tz=timezone(timedelta(hours = 7))).strftime("%Y%m%d")
            print(row['barcode'],row['amount'])

            update_current_stock(row['barcode'],row['amount'])

            try:
                H[row['barcode']] = int(row['amount'])
            except:
                H[row['barcode']] = 0
        update_history_stock(H)
        st.write('complete! Add Stock')
        st.write(f'Clear data -->{sheet_url}')
    else:
        print('add stock not match')
        st.write('add stock not match -->please update product')

st.write('***')

##----------------------------------------------------------------------
st.write('## Update Product')
# sheet_url = 'https://docs.google.com/spreadsheets/d/1XSC_4xKRSHTaKXsz5L0y52RJ0oCyWI2yFl98fJ8qQ9A/edit#gid=0'
sheet_url = 'https://docs.google.com/spreadsheets/d/1FWYRTRhGqz4XfE0SXrMNhtzKLfhcMLxgCkA36iRiEHo/edit#gid=0'
st.write(sheet_url)
if st.button('Update Product'):
    # sheet_url = 'https://docs.google.com/spreadsheets/d/1XSC_4xKRSHTaKXsz5L0y52RJ0oCyWI2yFl98fJ8qQ9A/edit#gid=0'
    url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df_products = pd.read_csv(url)
    df_products['barcode'] = df_products['barcode'].apply(str)
    # df_products = df_products.drop(['amount'], axis='columns', inplace=True)
    df_products = df_products.drop(columns=['amount'])
    st.write(df_products.to_html(escape=False), unsafe_allow_html=True)

    for index, row in df_products.iterrows():
        print(str(row['barcode']),row['name'],row['price'])
        update_products(str(row['barcode']),row['name'],int(row['price']))

    st.write('update_products complete!')

##----------------------------------------------------------------------
st.write('## Update Customers')
# sheet_url = 'https://docs.google.com/spreadsheets/d/1QX09dM7rZqZVkUHwEekoQ3XkSbIQLhwdetjgLe9ZngA/edit#gid=0'
sheet_url = 'https://docs.google.com/spreadsheets/d/1y7ioKeDwksad6LBjOBD65N2jlqsj04Q3xEtq1oZnaig/edit#gid=0'
st.write(sheet_url)
if st.button('Update Customers'):
    # sheet_url = 'https://docs.google.com/spreadsheets/d/1FWYRTRhGqz4XfE0SXrMNhtzKLfhcMLxgCkA36iRiEHo/edit#gid=0'
    url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df_customers = pd.read_csv(url)
    df_customers['barcode'] = df_customers['barcode'].apply(str)
    df_customers = df_customers[df_customers.name != 'Total']

    # df_customers = [str(int(x)) for x in df_customers['barcode']]
    B = []
    for x in df_customers['barcode']:
        try:
            B.append(str(int(float(x))))
        except:
            print(x,type(x))
            B.append(None)
    df_customers['barcode'] = B
    st.write(df_customers.to_html(escape=False), unsafe_allow_html=True)

    for index, row in df_customers.iterrows():
        print(str(int(row['barcode'])),row['name'])
        update_customers(str(row['barcode']),row['name'])
    st.write('complete! Update Customers')

##----------------------------------------------------------------------

st.write('## Update Shortcut')
sheet_url = 'https://docs.google.com/spreadsheets/d/1Hm3G33Rv85VVhE0N0joqhMa1qdgYSrZz5mdwI7J-DBI/edit#gid=0'
st.write(sheet_url)
if st.button('Update Shortcut'):
    # sheet_url = 'https://docs.google.com/spreadsheets/d/1FWYRTRhGqz4XfE0SXrMNhtzKLfhcMLxgCkA36iRiEHo/edit#gid=0'
    url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df_shortcut = pd.read_csv(url)

    X = []
    for x in df_shortcut['barcode']:
        if str(x) != 'nan':
            X.append(str(int(x)))
        else:
            X.append(None)
    df_shortcut['barcode'] = X
    # df_shortcut['barcode'] = df_shortcut['barcode'].apply(str)
    st.write(df_shortcut)
    C = {}
    for index, row in df_shortcut.iterrows():
        print("row['barcode']",row['barcode'],type(row['barcode']))
        if row['barcode']:
            print(type(row['barcode']))
            C[str(int(row['no']))] = row['barcode']
    print('C',C)
    update_shortcut(C)
    st.write('complete! Update Shortcut complete')


    # if st.button('Add Money'):
    #     sta = add_money(addmoney_df)
    #     st.write(sta,time.time())

    # if st.button(sta):
    #     print('STA',sta)

# st.write(pd.DataFrame({d
#     'first column': [1, 2, 3, bal],
#     'second column': [10, 20, 30, s]
# }))
