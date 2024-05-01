import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector as mydb
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
#creating a function to change image to text
def img_to_txt (path):
    # exporting image
    input_img= Image.open(path)
    # converting the image output into an array
    image_arr= np.array(input_img)
    # converting the array into text using easyocr
    reader= easyocr.Reader(['en'])
    text_img= reader.readtext(image_arr, detail=0)
    return text_img, input_img
# writing a function to convert the data into a dict
def text_extractor(text):
    # creating a empty dict
    details={"NAME":[], "DESIGNATION":[], "COMPANY NAME":[], "CONTACT":[], "WEBSITE":[], 
             "ADDRESS":[], "EMAIL":[], "PINCODE":[]}
    # assinging the values to each of the key in the dict
    details["NAME"].append(text[0])
    details["DESIGNATION"].append(text[1])
    for i in range(2, len(text)):
        if text[i].startswith("+") or (text[i].replace("-","").isdigit() and '-' in text[i]):
            details["CONTACT"].append(text[i])
        elif "@" in text[i] and ".com" in text[i]:
            details["EMAIL"].append(text[i])
        elif "www" in text[i] or "WWW" in text[i] or "Www" in text[i] or "wWw" in text[i] or "wwW" in text[i]:
            small=text[i].lower()
            details["WEBSITE"].append(small)
        elif "TamilNadu" in text[i] or "Tamil Nadu" in text[i] or "Tamil nadu" in text[i] or "Tamilnadu" in text[i] or text[i].isdigit():
            details["PINCODE"].append(text[i])
        elif re.match(r'^[A-Za-z]', text[i]):
            details["COMPANY NAME"].append(text[i])
        else:
            clear=re.sub(r'[,;]','',text[i])
            details["ADDRESS"].append(text[i])
    # handling the null values
    for key,value in details.items():
        if len(value)>0:
            concad= " ".join(value)
            details[key]=[concad]
        else:
            value="NA"
            details[key]=[value]
    return details
#streamlit codes
st.set_page_config(layout="wide")
st.title("Data extraction and modification from Business card Using OCR")
with st.sidebar:
    select=option_menu("Main Menu", ["Home", "Upload & Modify", "Delete"])
if select=="Home":
    st.markdown("### :blue[**Tools used:**] Python, EasyOCR, Streamlit, SQlite, Pandas")
    st.write("### :blue[**About :**] Bizcard is a Python application designed to extract information from business cards.")
    st.write("### :blue[**Purpose :**] The purpose of this application is to automate the data extraction from a Business Card and the store the information in the database.")
elif select=="Upload & Modify":
    img= st.file_uploader("Please select the image", type=["png", "jpg", "jpeg"])
    if img is not None:
        st.image(img, width=350)
        text_img, input_img= img_to_txt(img)
        text_dict= text_extractor(text_img)
        if text_dict:
            st.success("Data extracted successfully :)")
        df= pd.DataFrame(text_dict)
        st.dataframe(df)
        button=st.button("Upload")
        if button:
            db = mydb.connect(host="127.0.0.1",
                                port="3306",
                                user="root",
                                password="Spidey@123$",
                                database= "bizcard")
            cursor=db.cursor()
            create_table='''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(225),
                                                            designation varchar(225),
                                                            company_name varchar(225),
                                                            contact varchar(225),
                                                            website varchar(225),
                                                            address varchar(225),
                                                            email varchar(225),
                                                            pincode varchar(225))'''
            cursor.execute(create_table)
            db.commit()
            insert_query= '''INSERT INTO bizcard_details(name, designation, company_name, contact, website, address, email, pincode)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            datas= df.values.tolist()[0]
            cursor.execute(insert_query, datas)
            db.commit()
            st.success("Uploaded successfully! :)")
    method = st.radio("Select the method", ["None", "Preview", "Modify"])
    if method=="Preview":
        db = mydb.connect(host="127.0.0.1",
                            port="3306",
                            user="root",
                            password="Spidey@123$",
                            database= "bizcard")
        cursor=db.cursor()
        # select query
        select_query= '''SELECT * FROM bizcard_details'''
        cursor.execute(select_query)
        table= cursor.fetchall()
        db.commit()
        table_df= pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY NAME", "CONTACT", "WEBSITE", "ADDRESS", "EMAIL", "PINCODE"))
        st.dataframe(table_df)
    elif method == "Modify":
        db = mydb.connect(host="127.0.0.1",
                            port="3306",
                            user="root",
                            password="Spidey@123$",
                            database= "bizcard")
        cursor=db.cursor()
        #select query
        select_query = "SELECT * FROM bizcard_details"
        cursor.execute(select_query)
        table = cursor.fetchall()
        db.commit()
        table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY NAME", "CONTACT", "WEBSITE", "ADDRESS", "EMAIL", "PINCODE"))
        col1,col2 = st.columns(2)
        with col1:
            selected_name = st.selectbox("Select the name", table_df["NAME"])
            df_3 = table_df[table_df["NAME"] == selected_name]
            df_4 = df_3.copy() 
            col1,col2 = st.columns(2)
        with col1:
            mo_name = st.text_input("Name", df_3["NAME"].unique()[0])
            mo_desi = st.text_input("Designation", df_3["DESIGNATION"].unique()[0])
            mo_com_name = st.text_input("Company_name", df_3["COMPANY NAME"].unique()[0])
            mo_contact = st.text_input("Contact", df_3["CONTACT"].unique()[0])
            mo_email = st.text_input("Email", df_3["EMAIL"].unique()[0])
            df_4["NAME"] = mo_name
            df_4["DESIGNATION"] = mo_desi
            df_4["COMPANY NAME"] = mo_com_name
            df_4["CONTACT"] = mo_contact
            df_4["EMAIL"] = mo_email
        with col2:        
            mo_website = st.text_input("Website", df_3["WEBSITE"].unique()[0])
            mo_addre = st.text_input("Address", df_3["ADDRESS"].unique()[0])
            mo_pincode = st.text_input("Pincode", df_3["PINCODE"].unique()[0])
            df_4["WEBSITE"] = mo_website
            df_4["ADDRESS"] = mo_addre
            df_4["PINCODE"] = mo_pincode
            st.dataframe(df_4)
            col1,col2= st.columns(2)
        with col1:
            button_3 = st.button("Modify", use_container_width = True)
        if button_3:
            db = mydb.connect(host="127.0.0.1",
                                port="3306",
                                user="root",
                                password="Spidey@123$",
                                database= "bizcard")
            cursor=db.cursor()
            cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{selected_name}'")
            db.commit()
            # Insert Query
            insert_query = '''INSERT INTO bizcard_details(name, designation, company_name, contact, website, address, email, pincode)
                                                            values(?,?,?,?,?,?,?,?)'''
            datas = df_4.values.tolist()[0]
            cursor.execute(insert_query,datas)
            db.commit()
            st.success("MODIFIED SUCCESSFULLY")
elif select == "Delete":
    db = mydb.connect(host="127.0.0.1",
                        port="3306",
                        user="root",
                        password="Spidey@123$",
                        database= "bizcard")
    cursor=db.cursor()
    col1,col2 = st.columns(2)
    with col1:
        select_query = "SELECT NAME FROM bizcard_details"
        cursor.execute(select_query)
        table1 = cursor.fetchall()
        db.commit()
        names = []
        for i in table1:
            names.append(i[0])
            name_select = st.selectbox("Select the name", names)
    with col2:
        select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME ='{name_select}'"
        cursor.execute(select_query)
        table2 = cursor.fetchall()
        db.commit()
        designations = []
        for j in table2:
            designations.append(j[0])
            designation_select = st.selectbox("Select the designation", options = designations)
    if name_select and designation_select:
        col1,col2,col3 = st.columns(3)
        with col1:
            st.write(f"Selected Name : {name_select}")
            st.write("")
            st.write("")
            st.write("")
            st.write(f"Selected Designation : {designation_select}")
        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            remove = st.button("Delete", use_container_width= True)
            if remove:
                cursor.execute(f"DELETE FROM bizcard_details WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
                db.commit()
                st.warning("DELETED")