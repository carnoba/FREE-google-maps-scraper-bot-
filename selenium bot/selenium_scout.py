import os
import time
import pandas as pd
import subprocess
import re
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 🔥 MISSION CONFIGURATION (RECURSIVE AGENT) 🔥
# ==========================================
GEMINI_CMD = "gemini-cli" # Change to "gemini" if needed

CITIES = [ "Casper", "Cheyenne", "Gillette", "Rock Springs", "Laramie"]
NICHES = {
    "Roofing Contractor": 12000,
    "Solar Installation": 15000,
    "Junk Removal": 3500,
    "HVAC Repair": 10000,
    "Law Firm": 15000,
    "Medical Clinic": 8000
}

OUTPUT_CSV = "unlimited_leads.csv"

# ==========================================
# 🛠️ STEALTH SYSTEM (ANTI-ROBOT)
# ==========================================
def setup_stealth_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Headless off for captcha solving if needed
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1600,900")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Hide WebDriver
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

# ==========================================
# 🧠 AI RECURSIVE BRAIN
# ==========================================
def call_gemini_ai(prompt):
    """Deep data synthesis using Gemini CLI."""
    try:
        process = subprocess.Popen([GEMINI_CMD, prompt], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        stdout, stderr = process.communicate(timeout=45)
        if process.returncode == 0:
            return stdout.strip()
        return "N/A|N/A|N/A|N/A|N/A|N/A"
    except Exception:
        return "N/A|N/A|N/A|N/A|N/A|N/A"

def recursive_intel_hunt(driver, business_name, city, niche, website="N/A"):
    """Recursive search engine for Decision Makers."""
    print(f"   🕵️ INFILTRATING: {business_name}")
    
    original_window = driver.current_window_handle
    driver.execute_script("window.open('about:blank', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    
    intel_log = []
    found_owner_name = "N/A"
    
    try:
        # STEP 1: Website Deep Scan
        if website != "N/A" and "http" in website:
            print(f"      🌐 Deep Scanning Website...")
            driver.get(website)
            time.sleep(3)
            # Try finding 'About' or 'Team'
            for page in ["About", "Team", "Meet", "Staff", "Owner", "Doctor"]:
                try:
                    target = driver.find_element(By.PARTIAL_LINK_TEXT, page)
                    target.click()
                    time.sleep(2)
                    page_intel = driver.find_element(By.TAG_NAME, "body").text[:2000]
                    intel_log.append(f"WEBSITE_INTEL: {page_intel}")
                    driver.back()
                except: continue

        # STEP 2: Social Dorking (Finding the Name)
        print(f"      📡 Hunting Social Profiles...")
        query_name = f'"{business_name}" {city} (owner OR founder OR CEO OR president)'
        driver.get(f"https://www.google.com/search?q={query_name.replace(' ', '+')}")
        time.sleep(3)
        
        # Check for Recaptcha (Manual wait if needed)
        if "sorry/index" in driver.current_url:
            print("      ⚠️ CAPTCHA DETECTED! Use browser to solve.")
            time.sleep(15) 

        snippets = driver.find_elements(By.CSS_SELECTOR, "div.VwiC3b")
        search_intel = " ".join([s.text for s in snippets[:4]])
        intel_log.append(f"SEARCH_SNIPPETS: {search_intel}")

        # STEP 3: Initial AI Synthesis for Name
        name_prompt = f"From this text, find the Owner/CEO name for {business_name}: {search_intel}. Return ONLY the Name or N/A."
        found_owner_name = call_gemini_ai(name_prompt)

        # STEP 4: RECURSIVE SEARCH (If Name Found, Search for Mobile)
        if found_owner_name != "N/A" and len(found_owner_name) > 3:
            print(f"      🔥 RECURSIVE HUNT: Tracking {found_owner_name}'s direct line...")
            track_query = f'"{found_owner_name}" "{business_name}" (cell OR mobile OR personal OR contact)'
            driver.get(f"https://www.google.com/search?q={track_query.replace(' ', '+')}")
            time.sleep(2)
            deep_snippets = driver.find_elements(By.CSS_SELECTOR, "div.VwiC3b")
            intel_log.append(f"RECURSIVE_INTEL: {' '.join([s.text for s in deep_snippets[:3]])}")

        # STEP 5: Hiring Intelligence
        print(f"      💼 Checking Hiring Status...")
        hiring_query = f'site:linkedin.com/jobs OR site:indeed.com "{business_name}"'
        driver.get(f"https://www.google.com/search?q={hiring_query.replace(' ', '+')}")
        time.sleep(2)
        hiring_intel = "Yes" if len(driver.find_elements(By.TAG_NAME, "h3")) > 0 else "No"

        # FINAL SYNTHESIS
        final_prompt = f"""
        Analyze all intel for {business_name} in {city}.
        INTEL: {" ".join(intel_log)[:8000]}
        
        Extract Decision Maker Data.
        Rules: 
        1. Direct Mobile must NOT be the general office number. Verify context.
        2. Personal Email should be verified.
        3. Hiring Status is '{hiring_intel}'.
        
        OUTPUT FORMAT (Separated by '|'):
        OwnerName|DirectMobile|PersonalEmail|LinkedInProfile|HiringStatus|RevenueLossReason
        """
        
        grand_synthesis = call_gemini_ai(final_prompt)
        parts = grand_synthesis.split('|')
        if len(parts) >= 6:
            return parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]

    except Exception as e:
        print(f"      ⚠️ Intelligence Failure: {e}")
    finally:
        driver.close()
        driver.switch_to.window(original_window)
        
    return found_owner_name, "N/A", "N/A", "N/A", "No", "N/A"

# ==========================================
# 🚀 EXECUTE WARFARE
# ==========================================
def extract_leads():
    driver = setup_stealth_driver()
    processed_leads = []
    
    # Load existing to avoid dupes
    if os.path.exists(OUTPUT_CSV):
        existing_names = pd.read_csv(OUTPUT_CSV)['Business Name'].tolist()
    else:
        existing_names = []

    try:
        for city in CITIES:
            for niche, loss in NICHES.items():
                query = f"{niche} in {city}"
                print(f"\n🚀 MISSION START: {query}")
                
                driver.get(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
                time.sleep(5)
                
                # Simple scroll
                for _ in range(3):
                    try:
                        feed = driver.find_element(By.XPATH, '//div[@role="feed"]')
                        driver.execute_script("arguments[0].scrollTop += 1000", feed)
                        time.sleep(2)
                    except: break

                links = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")[:10] # Target first 10 for deep intel
                
                for link in links:
                    try:
                        # Basic Info extraction from Maps
                        name = link.get_attribute("aria-label")
                        if name in existing_names: continue
                        
                        driver.execute_script("arguments[0].click();", link)
                        time.sleep(2)
                        
                        phone_office = "N/A"
                        try:
                            phone_office = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Phone:")]').get_attribute("aria-label").replace("Phone: ", "")
                        except: pass
                        
                        website = "N/A"
                        try:
                            website = driver.find_element(By.XPATH, '//a[contains(@aria-label, "Website")]').get_attribute("href")
                        except: pass

                        # RECURSIVE DEEP INTEL
                        o_name, d_phone, p_email, l_profile, h_status, loss_reason = recursive_intel_hunt(driver, name, city, niche, website)
                        
                        lead = {
                            "Business Name": name,
                            "Owner Name": o_name,
                            "Direct Mobile": d_phone,
                            "Personal Email": p_email,
                            "LinkedIn Profile": l_profile,
                            "Hiring Status": h_status,
                            "Office Line": phone_office,
                            "Estimated Revenue Loss": f"${loss}",
                            "Loss Reason": loss_reason,
                            "Website": website
                        }
                        
                        # Progress Store
                        processed_leads.append(lead)
                        pd.DataFrame(processed_leads).to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
                        print(f"      ✅ TARGET SECURED: {name} | {o_name} | {d_phone}")
                        
                    except Exception as e: continue

    finally:
        driver.quit()
        print(f"\n⚡ MISSION COMPLETE: {len(processed_leads)} targets stored in {OUTPUT_CSV}")

if __name__ == "__main__":
    extract_leads()
