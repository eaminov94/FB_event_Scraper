from __future__ import absolute_import
from selenium import webdriver 
import scrapy
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib.request
import boto3
from boto3.s3.transfer import S3Transfer
from datetime import datetime,date
from ..items import FbEventsItem
timeout=15
import numpy as np
import psycopg2
import psycopg2.extras as extras

class SpiderSpider(scrapy.Spider):
    name = 'FB_events'
    allowed_domains = ['facebook.com']
    start_urls =['https://www.facebook.com/']


    def __init__(self, *args, **kwargs):
        super(SpiderSpider, self).__init__(*args, **kwargs)

        options = Options()
        # Pass the argument 1 to allow and 2 to block
        options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})
        options.add_argument("--disable-extensions")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-infobars")
        options.add_argument('--disable-dev-shm-usage') 
        options.add_argument("start-maximized")
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(chrome_options=options, executable_path='/usr/bin/chromedriver')

    def parse(self, response):
        #loging in to S3
        s3=boto3.client('s3',aws_access_key_id='AKIA2BXHMBBUCXR3IRG7',
                        aws_secret_access_key='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')
        
        
        self.driver.get(response.url)
        
        usr ="jyothishr@outlook.com"
        pwd = "ABCabc123!@#"
        time.sleep(10)
        try:
            username_box = self.driver.find_element_by_id('email')
            username_box.send_keys(usr)
        except:
            username_box2 = WebDriverWait(self.driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,'#email')))
            username_box2.send_keys(usr)  
        time.sleep(3)
        try:
            password_box = WebDriverWait(self.driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,'#pass')))
            password_box.send_keys(pwd)
        except:
            password_box2 = self.driver.find_element_by_id('pass')
            password_box2.send_keys(pwd)
        time.sleep(3)
        try:
            login_btn = self.driver.find_element_by_css_selector('#u_0_b')
        except:
            login_btn = WebDriverWait(self.driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,'#u_0_b')))
        login_btn.submit()
        time.sleep(5)
        self.driver.get('https://www.facebook.com/events/discovery/?acontext=%7B%22event_action_history%22%3A[]%7D')
        time.sleep(30)
        #more -> San Diego, California -> enter
        seq = self.driver.find_elements_by_tag_name('iframe')
        print("No of frames present in the web page are: ", len(seq))
        iframe = self.driver.find_elements_by_tag_name('iframe')[0]
        self.driver.switch_to.frame(iframe)
        html_list = self.driver.find_elements_by_class_name("_47ni")[1]

        items = html_list.find_elements_by_tag_name("span")
        action = ActionChains(self.driver)

        for item in items:    
            action.move_to_element(item).click().perform()
        time.sleep(3)
        inputElement = self.driver.find_element_by_class_name("_58al")
        time.sleep(1)
        inputElement.send_keys('San Diego, California')
        time.sleep(1)
        inputElement.send_keys(Keys.ENTER)
        time.sleep(3)
        #html = self.driver.find_element_by_tag_name('html')
        #river.switch_to.default_content()
        #this week 
        this_week=self.driver.find_element_by_xpath('//*[@id="u_0_1"]/div/div[1]/div/ul/li[2]/div/ul/li[5]/label/label')
        this_week_items = this_week.find_elements_by_tag_name("span")
        action = ActionChains(self.driver)
        for item in this_week_items:    
            action.move_to_element(item).click().perform()
        time.sleep(20)
        lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                lastCount = lenOfPage
                time.sleep(5)
                lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                    match=True
        #get all the links from the page
        elemsTW = self.driver.find_elements_by_tag_name("a")
        #and clening the links
        event_links=[]
        for lnk in elemsTW:
            i=lnk.get_attribute("href")
            if len(str(i)) > 32:
                if i[:32] == 'https://www.facebook.com/events/':
                    if i[:42] != 'https://www.facebook.com/events/discovery/':
                        event_links.append(i)
        #next week
        next_week=self.driver.find_element_by_xpath('//*[@id="u_0_1"]/div/div[1]/div/ul/li[2]/div/ul/li[7]/label/label')
        next_week_items = next_week.find_elements_by_tag_name("span")
        for item in next_week_items:    
            action.move_to_element(item).click().perform()
        time.sleep(5)
        #just move a bit up to load the page
        self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
        time.sleep(10)
        #scroll till the end
        lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                lastCount = lenOfPage
                time.sleep(5)
                lenOfPage = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                    match=True
        #get all the links from the page    
        elemsNW = self.driver.find_elements_by_tag_name("a")
        #and clening the links
        for lnk in elemsNW:
            i=lnk.get_attribute("href")
            if len(str(i)) > 32:
                if i[:32] == 'https://www.facebook.com/events/':
                    if i[:42] != 'https://www.facebook.com/events/discovery/':
                        event_links.append(i)       
        event_linksc = list(dict.fromkeys(event_links))     
       ########################## S3 - link duplication check #################################
        #reading id file from s3 
        obj = s3.get_object(Bucket='fbeventsdata', Key='Idlinks.csv')
        Id=pd.read_csv(obj['Body'])

        #removing the new links to evdnt_idc from the idlinks csv
        idlinks=list(Id['scrape_source_url'])
        for i in range(len(idlinks)):
            try:
                event_linksc.remove(idlinks[i])
            except:
                continue
        #clening the links evdnt_id 
        for i in range(len(event_linksc)):
            idlinks.append(event_linksc[i])
        idlinksc = list(dict.fromkeys(idlinks))  
        Idlinks=pd.DataFrame({'scrape_source_url':idlinksc})
        print('Number of events found :',len(event_linksc))
        ####################### event link ittratration ##########################
        evdnt_id=[]
        event_title=[]
        Timestamp=[]
        event_description=[]
        start_date=[]
        start_time=[]
        end_date=[]
        end_time=[]
        event_datetime_string =[]
        event_description=[]
        image_original_url=[]
        venue_address_string=[]
        scrape_source_url=[]
        buy_tickets_url=[]
        venue_name=[]
        venue_url=[]
        spider_scrape_datetime=[] 
        date_added=[]
        category_string=[]
        image_s3_url=[]
        venue_postal_code=[]
        online_event=[]
        cnt=0 
        twf=25
        print('scraping events.....')
        for url in event_linksc:
            self.driver.get(url)
            time.sleep(5)
            #scrape_source_url
            scrape_source_url.append(url)
            #evdnt_id
            evdnt_id.append(url[32:48].replace('/',''))
            #Timestamp
            Timestamp.append(time.time())
            soup=BeautifulSoup(self.driver.page_source,"html.parser")
            #event_title #done
            try:
                event_title.append(soup.findAll('h2',{'class':"gmql0nx0 l94mrbxd p1ri9a11 lzcic4wl d2edcug0 hpfvmrgz"})[1].text)
                ET=soup.findAll('h2',{'class':"gmql0nx0 l94mrbxd p1ri9a11 lzcic4wl d2edcug0 hpfvmrgz"})[1].text
            except:
                event_title.append(None)
            #event_description #done
            try:
                if soup.find('div',{'class':"dati1w0a hv4rvrfc"}).span.text.count(' ') > 200:
                    event_description.append(' '.join(i.split(' ')[:200]))
                else:
                    event_description.append(soup.find('div',{'class':"dati1w0a hv4rvrfc"}).span.text)
            except:
                event_description.append(None)
            #########Start & End -date & Time################ done###########
            CY=date.today().year
            try:
                SP=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')
                if len(SP) == 2:
                    try:
                        SD=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[0].split('AT ')[0].strip()
                        if len(SD.split(','))>=3:
                            dty=SD.split(', ')[-2].split(' ')[0][:3]+' '+SD.split(', ')[-2].split(' ')[-1]+' '+SD.split(', ')[-1]
                            date_time_obj = datetime.strptime(dty, '%b %d %Y').date()
                            start_date.append(date_time_obj)
                        else:
                            date_time_str = SD+' '+str(CY)
                            date_time_obj = datetime.strptime(date_time_str, '%b %d %Y').date()
                            start_date.append(date_time_obj)

                    except:
                        start_date.append(date.today())
                    # start_time 
                    try:
                        ST=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[0].split('AT ')[-1].strip().replace('UTC+05:30','').strip()
                        try:
                            in_time = datetime.strptime(ST, "%I %p")
                        except:
                            in_time = datetime.strptime(ST, "%I:%M %p")
                        out_time_ST = datetime.strftime(in_time, "%H:%M:%S")
                        start_time.append(out_time_ST)
                    except:
                        start_time.append(None)
                    # end_date
                    try:
                        ED=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[-1].strip().split('AT ')[0].strip().replace('UTC+05:30','')
                        if len(ED)>=25:
                            dty=ED.split(', ')[-2].split(' ')[0][:3]+' '+ED.split(', ')[-2].split(' ')[-1]+' '+ED.split(', ')[-1]
                            date_time_obj = datetime.strptime(dty, '%b %d %Y').date()
                            end_date.append(date_time_obj)
                            ET=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[-1].split('AT ')[-1].strip().replace('UTC+05:30','').strip()
                            try:
                                in_time = datetime.strptime(ET, "%I %p")
                            except:
                                in_time = datetime.strptime(ET, "%I:%M %p")
                            out_time_ET = datetime.strftime(in_time, "%H:%M:%S")
                            end_time.append(out_time_ET)
                        else:
                            ED=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[-1].strip().split('AT ')
                            if len(ED) != 2:
                                ET=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[-1].split('AT ')[-1].strip().replace('UTC+05:30','').strip()
                            # end_time
                                try:
                                    in_time = datetime.strptime(ET, "%I %p")
                                except:
                                    in_time = datetime.strptime(ET, "%I:%M %p")
                                out_time_ET = datetime.strftime(in_time, "%H:%M:%S")
                                end_date.append(None)
                                end_time.append(out_time_ET)
                            else:
                                ED=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[-1].split('AT ')[0].strip()
                                if ED.split(' ')[0]=='JAN':
                                    CY=CY+1
                                try:
                                    date_time_str = ED+' '+str(CY)
                                    date_time_obj = datetime.strptime(date_time_str, '%b %d %Y').date()
                                    end_date.append(date_time_obj)
                                except:
                                    end_date.append(date_time_obj)
                                try:
                                    ET=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[-1].split('AT ')[-1].strip().replace('UTC+05:30','').strip()
                                    try:
                                        in_time = datetime.strptime(ET, "%I %p")
                                    except:
                                        in_time = datetime.strptime(ET, "%I:%M %p")
                                    out_time = datetime.strftime(in_time, "%H:%M:%S")
                                    end_time.append(out_time)
                                except:
                                    end_time.append(None)
                    except:
                        end_date.append(date_time_obj)
                        end_time.append(None)
                else:
                    try:
                        SD=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[0].split('AT ')[0].strip()
                        if len(SD.split(','))>=3:
                            dty=SD.split(', ')[-2].split(' ')[0][:3]+' '+SD.split(', ')[-2].split(' ')[-1]+' '+SD.split(', ')[-1]
                            date_time_obj = datetime.strptime(dty, '%b %d %Y').date()
                            start_date.append(date_time_obj)
                        else:
                            if len(SD) > 10:
                                start_date.append(SD.split(',')[1].strip().split(' ')[0][:3]+' '+SD.split(',')[1].strip().split(' ')[1]+" "+SD.split(',')[-1].strip())
                            else:
                                date_time_str = SD+' '+str(CY)
                                date_time_obj = datetime.strptime(date_time_str, '%b %d %Y').date()
                                start_date.append(date_time_obj)

                    except:
                        start_date.append(None)
                    # start_time 
                    try:
                        ST=soup.find('div',{'class':"bi6gxh9e aov4n071"}).text.split('–')[0].split('AT ')[-1].strip().replace('UTC+05:30','').strip()
                        try:
                            in_time = datetime.strptime(ST, "%I %p")
                        except:
                            in_time = datetime.strptime(ST, "%I:%M %p")
                        out_time = datetime.strftime(in_time, "%H:%M:%S")
                        start_time.append(out_time)
                    except:
                        start_time.append(None)
                    end_date.append(date_time_obj)
                    end_time.append(None)
            except:
                start_time.append(None)
                start_date.append(date.today())
                end_date.append(None)
                end_time.append(None)
            #event_datetime_string #done
            try:
                event_datetime_string.append(soup.find('div',{'class':"bi6gxh9e aov4n071"}).text)
            except:
                event_datetime_string.append(None)
            #image_original_url #done
            try:
                image_original_url.append(soup.find('img',{'data-imgperflogname':"profileCoverPhoto"}).get('src'))
            except:
                image_original_url.append(None)
            #image_s3_url #done
            try:
                name=str((str(image_original_url[-1][57:].split('.jpg')[0])+'.jpg'))
                urllib.request.urlretrieve(image_original_url[-1],name)
                transfer = S3Transfer(s3)
                transfer.upload_file(name, 'fbeventsdata', 'full'+'/'+name)
                response = s3.put_object_acl(ACL='public-read', Bucket='fbeventsdata', Key="%s/%s" % ('full', name))
                image_s3_url.append('full/'+name)
            except:
                image_s3_url.append(None)

            #venue_address_string & Venue name #done
            try:
                Topleft=soup.findAll('div',{'class':"bi6gxh9e aov4n071"})[2]
                if Topleft.text[-13:]=='United States':
                    venue_address_string.append(Topleft.text)
                    online_event.append(False)
                else:
                      WroNg
            except:
                try:
                    mapbot=soup.findAll('div',{'class':"ihqw7lf3"})[5].findAll('div',{'class':"qzhwtbm6 knvmm38d"})[-1]
                    if mapbot.text[-13:]=='United States':
                        venue_address_string.append(mapbot.text)
                        online_event.append(False)
                    else:
                        WroNg
                except:
                    try:
                        mapbottom_c1=soup.findAll('div',{'class':"ihqw7lf3"})[7].findAll('div',{'class':"qzhwtbm6 knvmm38d"})[-1]
                        if mapbottom_c1.text[-13:]=='United States':
                            venue_address_string.append(mapbottom_c1.text)
                            online_event.append(False)
                        else:
                            WroNg
                    except:
                        venue_address_string.append('Online Event')
                        online_event.append(True)
            try:
                if Topleft.text.strip() != 'Online Event' and Topleft.text.strip()!='NULL':
                    venue_name.append(Topleft.text)
                else:
                    venue_name.append(None)
            except:
                venue_name.append(None)

            #venue_postal_code #done
            if len(venue_address_string[-1]) > 12:
                postal_code=venue_address_string[-1].split('CA')[-1]
                if len(postal_code.split('-')) == 2:
                    if len(postal_code.split('-')[0].strip()) > 4:
                        venue_postal_code.append(round(int(float(postal_code.split('-')[0].strip()))))
                    else:
                        venue_postal_code.append(None)
                else:
                    if len(re.sub("[^0123456789\.]","",postal_code)) > 3:
                        venue_postal_code.append(round(int(float(re.sub("[^0123456789\.]","",postal_code)))))
                    else:
                        venue_postal_code.append(None)
            else:
                venue_postal_code.append(None)
            #buy_tickets_url #done
            try:
                buy_tickets_url(soup.find('a',{'aria-label':"Find Tickets"}).get('href'))
            except:
                buy_tickets_url.append(None)

            if  venue_address_string[-1] != 'Online Event':
                #venue_url
                try:
                    venue_url.append(soup.find('div',{'class':"l9j0dhe7 stjgntxs ni8dbmo4 do00u71z"}).div.get('style').split('"')[1])
                except:
                    venue_url.append(None)
            else:
                venue_url.append(None)
            #spider_scrape_datetime
            spider_scrape_datetime.append(datetime.now())
            #date_added
            date_added.append(datetime.now().date())
            #category_string
            try:
                CAT=[]
                for cat in soup.find('div',{'class':"lhclo0ds j83agx80"}).findAll('span'):
                    CAT.append(cat.text.replace('[','').replace(']','NULL').replace("'",''))
                category_string.append(CAT)
            except:
                category_string.append('NULL')
            cnt=cnt+1
            if cnt== twf:
                twf=twf+25
                print('remaing evnts to scrap ',len(event_linksc)-cnt)

        data=pd.DataFrame({
        'event_title':event_title,
        'start_date':start_date,
        'start_time':start_time,
        'end_date':end_date,
        'end_time':end_time,
        'event_description':event_description,
        'event_datetime_string':event_datetime_string,
        'scrape_source_name': 'Facebook',
        'scrape_source_url': scrape_source_url,
        'original_source_name': None,
        'original_source_url':None,
        'buy_tickets_url': buy_tickets_url,          
        'tickets_by':None,
        'ticket_vendor_image_url':None,
        'tickets_sold_out':False,
        'venue_name':venue_name,
        'venue_url':venue_url,
        'venue_event_url':None,
        'venue_address_string':venue_address_string,
        'venue_address1':None,
        'venue_address2':None,
        'venue_city':'San Diego',
        'venue_state':'California',
        'venue_country':'USA',
        'venue_postal_code':venue_postal_code, 
        'venue_neighbourhood':None,
        'venue_latitude':None,
        'venue_longitude':None,
        'venue_gmap_url':None,
        'cost_string': None,
        'cost_min_extract':None,
        'cost_max_extract':None,
        'cost_is_free':False,
        'age_restrictions_string':None,
        'age_minimum':None,
        'is_cancelled':False,
        'image_original_url':image_original_url,
        'image_s3_url':image_s3_url,
        'image_height':None,
        'image_width':None,
        'contact_phone':None,
        'contact_email':None,
        'spider_name':'FB_evetes',
        'spider_scrape_datetime':spider_scrape_datetime,
        'date_added':date_added,
        'date_updated':None,
        'date_last_seen':None,
        'suspected_duplicate_event':False,
        'online_event':online_event,
        'processed': True,
        'inappropriate_events':False,
        'category_string':category_string})
        data.rename(index={0:'id'},inplace=True)
        data.to_csv('data.csv',index=False)
        Idlinks.to_csv('Idlinks.csv')
        
        print('Scrapying done, building pipeline')
        #connecting to Postgres
        connection = psycopg2.connect(user="yohptqqwkueivi",
                              password="d71d9d14019340b254a42d5959b1f292be6730747a8aa558a8a0e88d6de22b29",
                              host="ec2-54-91-178-234.compute-1.amazonaws.com",
                              port="5432",
                              database="db9au898jdrq9s")
        cursor = connection.cursor()
        #wringing to postgres
        def execute_values(conn, df, table):
            # Create a list of tupples from the dataframe values
            tuples = [tuple(x) for x in df.to_numpy()]
            # Comma-separated dataframe columns
            cols = ','.join(list(df.columns))
            # SQL quert to execute
            query  = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
            cursor = conn.cursor()
            try:
                extras.execute_values(cursor, query, tuples)
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("Error: %s" % error)
                conn.rollback()
                cursor.close()
                return 1
            print("execute_values() done")
            cursor.close()
            
        execute_values(connection,data,'events_event')

        print('uploading data to aws s3')
        #uploading the updated links to s3
        s3.upload_file('Idlinks.csv','fbeventsdata','Idlinks.csv')
        s3.upload_file('data.csv','fbeventsdata','data.csv')
