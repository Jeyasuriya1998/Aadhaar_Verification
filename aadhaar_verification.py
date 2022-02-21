from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from tkinter.filedialog import askopenfilename
from tkinter import *

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time, re, os, base64, boto3,os,csv
from PIL import Image
import pandas as pd
from datetime import datetime 
import warnings, sys
warnings.filterwarnings('ignore')


# options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-gpu')
# selenium_url = 'http://ec2-65-0-140-243.ap-south-1.compute.amazonaws.com:4444/wd/hub'

# driver = webdriver.Remote(selenium_url, options=options)

# path = os.path.abspath(os.path.join('driver',"chromedriver.exe"))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

path = resource_path('./driver/chromedriver.exe')

# path = os.path.abspath("chromedriver.exe")

ser = Service(path)
op = webdriver.ChromeOptions()
op.add_argument("--headless") 
op.add_argument("--incognito") 
op.add_argument("--disable-gpu") 
op.add_argument("--disabel-extension") 

def read_captcha(data, Image_captcha_dir):
    access_key = "AKIAWNZ5LDXMFU2URWZO"
    secret_key = "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"
    client=boto3.client('textract',region_name='ap-south-1',aws_access_key_id=access_key,  aws_secret_access_key= secret_key)
    
    if len(os.listdir(Image_captcha_dir)) < 1:
        count = 0
    else:
        count = len(os.listdir(Image_captcha_dir))+1

    captcha_img = os.path.join(Image_captcha_dir, f'captcha_{count}.png')
    
    decodeit = open(captcha_img, 'wb')
    decodeit.write(base64.b64decode((data)))
    decodeit.close()
#     Image.open('hello_level.png').resize((400, 200)).convert('RGB').save('hello_level.png')

#     display(Image.open(captcha_img))
    # Read image
    with open(captcha_img, 'rb') as document:
        img = bytearray(document.read())

    # Call Amazon Textract
    response = client.detect_document_text( Document={'Bytes': img})

    # Print detected text
    captcha = re.sub(r'\s|[^a-zA-Z0-9]', '', ''.join([item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"]))
#     print(captcha) 
    return captcha

def final_merging(img, pdf_valid_dir):
    # images_list = [os.path.abspath(os.path.join('assets','digi.jpg')), img,\
    #                os.path.abspath(os.path.join('assets','add.jpg'))]
    images_list = [resource_path('./assets/digi.jpg'), img, resource_path('./assets/add.jpg')]
    imgs = [Image.open(i) for i in images_list]
    
    # If you're using an older version of Pillow, you might have to use .size[0] instead of .width
    # and later on, .size[1] instead of .height
    min_img_width = max(i.width for i in imgs)

    total_height = 0
    for i, img in enumerate(imgs):
        # If the image is larger than the minimum width, resize it
        if img.width > min_img_width:
            imgs[i] = img.resize((min_img_width, int(img.height / img.width * min_img_width)), Image.ANTIALIAS)
        total_height += imgs[i].height

    # I have picked the mode of the first image to be generic. You may have other ideas
    # Now that we know the total height of all of the resized images, we know the height of our final image
    img_merge = Image.new(imgs[0].mode, (min_img_width, total_height))
    y = 0
    for img in imgs:
        img_merge.paste(img, (0, y))

        y += img.height
    img_merge.save(pdf_valid_dir)
    # print("img merge")
#     display(img_merge)
        

def home(aadhaar_details):
    driver = webdriver.Chrome(service=ser, options=op)
    driver.set_window_size(1082, 744)
    driver.maximize_window()
    

    print("Searching https://myaadhaar.uidai.gov.in")
    time.sleep(3)
    driver.get("https://myaadhaar.uidai.gov.in/")
    time.sleep(3)
    # aadhaars = ['762305582030', '9651 5116 5933']
    
    Images_valid_dir = os.path.abspath(os.path.join("aadhar_pngs","valid"))
    Images_invalid_dir = os.path.abspath(os.path.join("aadhar_pngs","Invalid"))
    Image_captcha_dir = os.path.abspath("captcha")
    Image_Validated_captcha_dir = os.path.abspath(os.path.join("captcha","validated_captcha"))
    pdf_valid_dir = os.path.abspath("aadhat_pdf")
    if not os.path.exists(Images_valid_dir): os.makedirs(Images_valid_dir)
    if not os.path.exists(Images_invalid_dir): os.makedirs(Images_invalid_dir)
    if not os.path.exists(Image_Validated_captcha_dir): os.makedirs(Image_Validated_captcha_dir)
    if not os.path.exists(Image_captcha_dir): os.makedirs(Image_captcha_dir)
    if not os.path.exists(pdf_valid_dir): os.makedirs(pdf_valid_dir)

    
    
#     driver.get("https://myaadhaar.uidai.gov.in/verifyAadhaar")
    for idx, aadhaar in aadhaar_details.iterrows():
        print("Click Aadhaar verification")
        time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/section/div[2]/div[9]/div/div[1]/div[2]/div[2]').click()
        time.sleep(3)
        search_box = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[1]/div/form/div/div[1]/div/div/div/input')
        aadhar_number = aadhaar['Adhaar_Num']#input("Enter Your Aadhar Number : ")
        print(f"Enter the Aadhaar number for {aadhaar['Full Name']} is {aadhaar['Adhaar_Num']}")
        search_box.send_keys(aadhar_number)

        time.sleep(3)
        
        try:
            if driver.find_element(By.XPATH,'//*[@id="root"]/div/div[3]/div/div/div[1]/div/form/div/div[1]/div/div[2]/span'):
                print(driver.find_element(By.XPATH,'//*[@id="root"]/div/div[3]/div/div/div[1]/div/form/div/div[1]/div/div[2]/span').text)
                log = f"{datetime.now()} ({aadhaar['S. No']}) ({aadhaar['Full Name']}) ({aadhar_number})  Result (Invaild Aadhaar) \n"
                print(log)
                with open(os.path.abspath("log for aadhar v2.txt"), 'a') as f:
                    f.write(log)
                driver.save_screenshot(os.path.join(Images_invalid_dir, f"{aadhaar['S. No']}_{aadhaar['Full Name']}.png"))
                # //*[@id="root"]/div/div[2]/header/div[2]/div/div[1]/span
                driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/header/div[2]/div/div[1]/span').click()
                print("Get Back to Home Page https://myaadhaar.uidai.gov.in \n")
                continue
       
        except:
            print("Aadhaar is valid")

        captcha_img = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[1]/div/form/div/div[2]/div[2]/img')
        data = captcha_img.screenshot_as_base64
        print("Read The Captcha")
        captcha = read_captcha(data, Image_captcha_dir)
#         print(len(captcha)) 
        for i in range(100):
#             print(i)
            try:
                if len(captcha) == 6:
                    captch_box = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[1]/div/form/div/div[2]/div[1]/div/div/div/input')
                    print(f"Enter the Captcha {captcha}")
                    captch_box.send_keys(captcha)
                    time.sleep(3)
                    button = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[1]/div/form/div/div[3]/div/button')
                    button.click()
                    time.sleep(3)

                    if driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/span[2]'):
                        decodeit = open(os.path.join(Image_Validated_captcha_dir, f"{captcha}.png"), 'wb')
                        decodeit.write(base64.b64decode((data)))
                        decodeit.close()
                        print("Save The Valid Captcha")
                        print(driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/span[2]').text)
                        driver.save_screenshot(os.path.join(Images_valid_dir, f"{aadhaar['S. No']}_{aadhaar['Full Name']}.png"))
                        Image.open(os.path.join(Images_valid_dir, f"{aadhaar['S. No']}_{aadhaar['Full Name']}.png")).resize((810, 825)).save(os.path.join(Images_valid_dir, f"{aadhaar['S. No']}_{aadhaar['Full Name']}.png"))
#                         display(Image.open(os.path.join(Images_valid_dir, f"{aadhaar['S. No']}_{aadhaar['Full Name']}.png")))
                        print("Merge the verified Aadhaar with digiverifier logo and address")
                        final_merging(os.path.join(Images_valid_dir, f"{aadhaar['S. No']}_{aadhaar['Full Name']}.png"), os.path.join(pdf_valid_dir, f"{aadhaar['S. No']}_{aadhaar['Full Name']}.png"))
                        print("Completed")
                        attempt, message = i, "Success"
                        break
                else:
                    driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[1]/div/form/div/div[2]/div[2]/div').click()
                    time.sleep(2)
                    captcha_img = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[1]/div/form/div/div[2]/div[2]/img')
                    data = captcha_img.screenshot_as_base64
                    captcha = read_captcha(data, Image_captcha_dir)
                    attempt, message = i, "Fail"
#                     print(len(captcha)) 
            except:
                try:
                    print(driver.find_element(By.XPATH, '//*[@id="verifyAadhaarAPI"]/div[1]').text)
                    print(f"attepmt {i} captcha {captcha} length of captcha {len(captcha)}")
                    time.sleep(4)
                    captcha_img = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[3]/div/div/div[1]/div/form/div/div[2]/div[2]/img')
                    data = captcha_img.screenshot_as_base64
                    captcha = read_captcha(data, Image_captcha_dir)
#                     print(len(captcha)) 
                    if i==48: 
                        print("Invalid or captcha Issue")
                    attempt, message = i, "Fail"
                except:
                    # driver.save_screenshot(os.path.join(Images_invalid_dir, f"{aadhaar['S. No']}_{aadhaar['Full Name']}.png"))
                    attempt, message = i, "Fail"
        log = f"{datetime.now()} ({aadhaar['S. No']}) ({aadhaar['Full Name']}) ({aadhar_number}) attempt of captcha ({attempt}) Result ({message}) \n"
        print(log)
        with open(os.path.abspath("log for aadhar v2.txt"), 'a') as f:
            f.write(log)
        # log_file.write(log)
        time.sleep(5)
        if message == "Fail":driver.save_screenshot(os.path.join(Images_invalid_dir, f"{aadhaar['S. No']}_{aadhaar['Full Name']}.png"))
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/header/div[2]/div/div[1]/span').click()
        print("Get Back to Home Page https://myaadhaar.uidai.gov.in \n")
        time.sleep(4)
    
    driver.quit()

if __name__ == "__main__":
    win= Tk()
    print("\nMake Sure Excel having Columns 'S. No' 'Full Name' 'Adhaar_Num'\n")
    f_types = [('All Files','*.*')]
    filename = askopenfilename(filetypes=f_types)
    win.destroy()
    print(filename)
    aadhaar_details = pd.read_excel(filename)#[140:141]
    home(aadhaar_details)