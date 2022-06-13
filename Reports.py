import streamlit as st
import numpy as np
import pandas as pd
import datetime
from datetime import date
import mysql.connector
import time
# import openpyxl

class Class_Reports:
    # Initialize connection.
    # Uses st.cache to only run once.
    st.title('Web Scrapping Reports')

    # @st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
    def __init__(self):
        self.conn = self.con_init()
        self.display_results()
        self.main()

    # @st.cache(allow_output_mutation=True)
    def con_init(self):
        return mysql.connector.connect(**st.secrets["db_credentials"])
    # @st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
    # @st.cache(hash_funcs={DBConnection: id})
    def query(self, query):
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()
        
    def count_forsale(self, d):
        result = self.query(f"SELECT COUNT(IF(status = 'for_sale', 1, NULL)) 'For Sale' FROM hemnet_bostad_salda WHERE date_created = '{d}';")
        return result[0][0]

    def count_sold(self, d):
        result = self.query(f"SELECT COUNT(IF(status = 'sold', 1, NULL)) 'Sold' FROM hemnet_bostad_salda WHERE date_updated = '{d}';")
        return result[0][0]

    def count_private(self, d):
        result = self.query(f"SELECT COUNT(IF(status = 'private', 1, NULL)) 'Private' FROM hemnet_bostad_salda WHERE date_updated = '{d}';")
        return result[0][0]
    
    def forsale(self):
        result = self.query(f"{st.secrets["countforsale"]}")
        return result[0][0]

    def sold(self):
        result = self.query(f"{st.secrets["countsold"]}")
        return result[0][0]

    def private(self):
        result = self.query(f"{st.secrets["countprivate"]}")
        return result[0][0]
    
    def display_results(self):
        st.header('Total Records')
        st.write(f'For Sale: {self.forsale()}')
        st.write(f'Sold: {self.sold()}')
        st.write(f'Private: {self.private()}')

    def main(self):

        d3 = st.date_input("Please select date range: ", [])
        if (len(d3) > 1):
            dates = pd.date_range(start=d3[0], end=d3[1])
#             additional functions
            self.dateindex = pd.date_range(start=d3[0], end=d3[1],freq='D')

            # st.write(dates)
            if not dates.empty:
                status = st.radio("Select status: ", ('For Sale', 'Sold', 'Private', 'All'))
                st.info(f"Showing results from {d3[0].strftime('%d, %B %Y')} to {d3[1].strftime('%d, %B %Y')}")

                if status == 'For Sale':
                    st.header('For Sale Properties')
                    self.table(dates, 1, statusText = "For Sale Properties")
                elif status == 'Sold':
                    st.header('Sold Properties')
                    self.table(dates, 2, statusText = "Sold Properties")
                elif status == 'Private':
                    st.header('Private Properties')
                    self.table(dates, 3, statusText = "Private Properties")
                else: 
                    st.header('All Properties')
                    self.table(dates, 0, statusText = "All Properties")

    def switch(self, option, dates):

        if option == 1:
            return self.count_forsale(dates)
     
        elif option == 2:
            return self.count_sold(dates)
     
        elif option == 3:
            return self.count_private(dates)
        else:
            return 0

    def table(self, coveredDates, status, statusText):
        my_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1)
        my_bar.empty()

        if (status == 0):
            df = pd.DataFrame(columns=['For Sale Properties', 'Sold Properties', 'Private Properties'])
        else:
            df = pd.DataFrame(columns=[statusText])
            
            
        for i in range(len(coveredDates)):
            d = coveredDates[i].strftime('%Y-%m-%d')
            
            if (status == 0):
                arr = []
                for x in range(1, 4):
                    res = self.switch(x, d)
                    arr.append(res)

                df = df.append({'For Sale Properties': arr[0], 'Sold Properties': arr[1], 'Private Properties': arr[2]}, ignore_index=True)
            else:
                result = self.switch(status, d)
#                 df = df.append([{'Dates': d, str(statusText): result}], ignore_index=True)
#                 a = str(result)
                df = df.append({statusText: result}, ignore_index=True)
    
        df.index = self.dateindex
        st.table(df)
        # st.line_chart(df
        st.area_chart(df)
        st.balloons()
 
if __name__ == '__main__':
    try:
        Class_Reports()
        pass
    except Exception as e:
        raise e
    
