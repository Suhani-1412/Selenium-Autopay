from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import time
import random
from selenium.webdriver.support.ui import Select

load_dotenv()

LOGIN = os.getenv("LOGIN") or "http://127.0.0.1:5000/"
USERNAMME = (os.getenv("USERNAMME") or "testuser").strip()
print(USERNAMME)
PASSWORD = (os.getenv("PASSWORD") or "pass123").strip()
EMAIL = (os.getenv("EMAIL") or "test@example.com").strip()
CARDNUM=os.getenv("CARDNUM") or 4242424242424242
EXPIRY=os.getenv("EXPIRY") or 12/27
CVC=os.getenv("CVC") or 123

debugging = True


def explicit_wait(driver,locator_type, locator, timeout=5, clickable=False):
    if clickable:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((locator_type, locator))
        )
    else:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((locator_type, locator))
        )

# --- Attempt login ---
def Login(driver,user_str,pass_str):
    username = explicit_wait(driver, By.NAME, "username")
    
    username.clear()
    username.send_keys(user_str)

    password = explicit_wait(driver,By.NAME, "password")
    password.send_keys(pass_str)

    button = explicit_wait(driver,By.XPATH, '//*[@id="authForm"]/button', clickable=True)
    button.click()
    
#---Registartion---
def registration(driver,base_username,password):
    
    # Switch to register form
    toggle = explicit_wait(driver,By.CLASS_NAME, "toggle", clickable=True)
    toggle.click()
    explicit_wait(driver, By.ID, "registerForm")  # wait for form to load
    print("➡️ Switched to register form")

    # Generate unique username/email
    rand_id = str(random.randint(1000, 9999))
    reg_name = explicit_wait(driver,By.XPATH, '//*[@id="registerForm"]//input[@name="username"]')
    new_username = f"{base_username}_{rand_id}"
    reg_name.clear()
    reg_name.send_keys(new_username)
    

    reg_pass = explicit_wait(driver,By.XPATH, '//*[@id="registerForm"]//input[@name="password"]')
    new_password = password
    reg_pass.send_keys(new_password)

    reg_mail = explicit_wait(driver,By.XPATH, '//*[@id="registerForm"]//input[@name="email"]')
    new_email = f"{USERNAMME}_{rand_id}@gmail.com"
    reg_mail.send_keys(new_email)

    reg_button = explicit_wait(driver,By.XPATH, '//*[@id="registerForm"]/button', clickable=True)
    reg_button.click()
    print("✅ Registration submitted")
    
    return new_username,new_password,new_email

def payment(driver,email,country):
    
    payment_email=explicit_wait(driver,By.ID,"email")
    payment_email.send_keys(email)
    
    card_num=explicit_wait(driver,By.ID,"cardNumber")
    card_num.send_keys(CARDNUM)
    
    expiry_date=explicit_wait(driver,By.ID,"cardExpiry")
    expiry_date.send_keys(EXPIRY)
    
    cvc_card=explicit_wait(driver,By.ID,"cardCvc")
    cvc_card.send_keys(CVC)
    
    cardholder=explicit_wait(driver,By.ID,"billingName")
    cardholder.clear()
    cardholder.send_keys(USERNAMME)
    
    cardLocation=explicit_wait(driver,By.ID,"billingCountry")
    select=Select(cardLocation)
    
    select.select_by_value(f"{country}")
        
    zip=explicit_wait(driver,By.ID,"billingPostalCode",timeout=10)
    zip.send_keys("12345") 
    
    # This works only if the element exists in the DOM at some point within timeout.
    # If the element doesn’t exist at all until after some other interaction, your explicit_wait will fail if called too early. so either increse timeout or do it manually after some interacion or webdriver wait again as shown in below code
    
    # zip_input = WebDriverWait(driver, 5).until(
    #     EC.visibility_of_element_located((By.ID, "billingPostalCode"))
    # )
    # zip_input.send_keys("12345")
    
    #In Stripe’s checkout:
    #The ZIP code input does not exist in the DOM until after you select a country.
    #The card number, expiry, and CVC inputs are inside iframes, so they are not accessible via driver.find_element directly.
    #This means your usual explicit_wait cannot find them before the field appears or without switching to iframe.
    
    # (bcz input field was not visible in css and span too so u used label)
    label_checkbox = driver.find_element(By.CSS_SELECTOR, "label[for='enableStripePass']")
    label_checkbox.click()
    
    phn_num=explicit_wait(driver,By.ID,"phoneNumber",timeout=8)
    phn_num.send_keys("2015551234")
    
    pay_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='hosted-payment-submit-button']")

# Use JavaScript to click the button bcz its hindered by some blocking event which i cant identify
    driver.execute_script("arguments[0].click();", pay_button)
    
    
def main():
    options = webdriver.ChromeOptions()
    if debugging:
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option("detach", True)
    else:
        options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(LOGIN)
    Login(driver,USERNAMME,PASSWORD)
    
    # --- Check for login error ---
    err = driver.find_elements(By.CLASS_NAME, "error")
    if err:
        print(f"login failed: {err[0].text}")
        time.sleep(2)
        new_user,new_pass,new_email=registration(driver,USERNAMME,PASSWORD)
        time.sleep(2)
        
        Login(driver,new_user,new_pass)
        proceed = explicit_wait(driver, By.XPATH, "//form//button[contains(text(), 'Proceed')]", clickable=True)
        proceed.click()
        time.sleep(2)
        
        payment(driver,new_email,"US")

    else:
        print("✅ Login successful")
    

    if not debugging:
        driver.quit()

if __name__=="__main__":
    main()