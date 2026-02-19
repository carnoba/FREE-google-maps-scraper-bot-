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

CITIES = ["Mississippi", "West Virginia", "Arkansas", "Wyoming", "South Dakota"]
NICHES = {
   
    "Junk Removal": 3500,
    "HVAC Repair": 10000,
    "Law Firm": 15000,
    "Medical Clinic": 8000,
    "Roofing Contractor": 12000,
    "Solar Installation": 15000
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

def find_emails(text, driver=None):
    """Extract emails from text using regex and mailto links."""
    emails = []
    if text:
        emails.extend(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
    
    if driver:
        try:
            links = driver.find_elements(By.XPATH, '//a[contains(@href, "mailto:")]')
            for link in links:
                href = link.get_attribute("href")
                email = href.replace("mailto:", "").split("?")[0].strip()
                if email: emails.append(email)
        except: pass
    
    # Return unique emails, prioritizing common patterns
    return list(set(emails))

def recursive_intel_hunt(driver, business_name, city, niche, website="N/A", phone_office="N/A"):
    """Recursive search engine for Decision Makers."""
    print(f"   🕵️ INFILTRATING: {business_name}")
    
    original_window = driver.current_window_handle
    driver.execute_script("window.open('about:blank', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    
    intel_log = []
    found_owner_name = "N/A"
    all_found_emails = []
    
    try:
        # STEP 1: Website Deep Scan
        if website != "N/A" and "http" in website:
            print(f"      🌐 Deep Scanning Website...")
            try:
                driver.get(website)
                time.sleep(4)
                
                # Check homepage first
                homepage_text = driver.find_element(By.TAG_NAME, "body").text
                all_found_emails.extend(find_emails(homepage_text, driver))
                
                # Find all links to potentially relevant pages
                potential_pages = []
                links = driver.find_elements(By.TAG_NAME, "a")
                keywords = ["about", "team", "meet", "staff", "owner", "contact", "management", "who"]
                
                for link in links:
                    try:
                        text = link.text.lower()
                        if any(k in text for k in keywords):
                            potential_pages.append(link.get_attribute("href"))
                    except: continue
                
                # Visit up to 4 most relevant pages
                for page_url in list(set(potential_pages))[:4]:
                    try:
                        if not page_url or page_url == website: continue
                        driver.get(page_url)
                        time.sleep(2)
                        body_text = driver.find_element(By.TAG_NAME, "body").text
                        page_emails = find_emails(body_text, driver)
                        all_found_emails.extend(page_emails)
                        if page_emails:
                            intel_log.append(f"EMAILS_ON_{page_url}: {', '.join(set(page_emails))}")
                        intel_log.append(f"WEBSITE_PAGE_INTEL: {body_text[:1500]}")
                    except: continue
            except Exception as e:
                print(f"      ⚠️ Website Scan Issue: {e}")

        # STEP 2: Social Dorking (Finding the Name & Email)
        print(f"      📡 Hunting Social Profiles...")
        query_name = f'"{business_name}" {city} (owner OR founder OR CEO OR "contact email")'
        driver.get(f"https://www.google.com/search?q={query_name.replace(' ', '+')}")
        time.sleep(3)
        
        if "sorry/index" in driver.current_url:
            print("      ⚠️ CAPTCHA! Waiting...")
            time.sleep(15) 

        snippets = driver.find_elements(By.CSS_SELECTOR, "div.VwiC3b")
        search_intel = " ".join([s.text for s in snippets[:5]])
        search_emails = find_emails(search_intel)
        all_found_emails.extend(search_emails)
        intel_log.append(f"SEARCH_SNIPPETS: {search_intel}")

        # STEP 3: Initial AI Synthesis for Name
        name_prompt = f"From this text, find the Owner/CEO name for {business_name}: {search_intel}. Return ONLY the Name or N/A."
        found_owner_name = call_gemini_ai(name_prompt)
        if found_owner_name == "N/A" or len(found_owner_name) > 30: # Likely failed or junk
             # Fallback: simple heuristic for names in snippets
             match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', search_intel)
             if match: found_owner_name = match.group(1)

        # STEP 4: RECURSIVE SEARCH
        if found_owner_name != "N/A" and len(found_owner_name) > 3:
            print(f"      � RECURSIVE HUNT: Tracking {found_owner_name}...")
            track_query = f'"{found_owner_name}" "{business_name}" (email OR "@")'
            driver.get(f"https://www.google.com/search?q={track_query.replace(' ', '+')}")
            time.sleep(2)
            deep_snippets = driver.find_elements(By.CSS_SELECTOR, "div.VwiC3b")
            deep_text = ' '.join([s.text for s in deep_snippets[:3]])
            deep_emails = find_emails(deep_text)
            all_found_emails.extend(deep_emails)
            intel_log.append(f"RECURSIVE_INTEL: {deep_text}")

        # Ensure we have unique emails
        all_found_emails = list(set(all_found_emails))

        # FINAL AI SYNTHESIS
        final_prompt = f"""
        Analyze all intel for {business_name} in {city}.
        EMAILS FOUND BY SCRAPER: {all_found_emails}
        INTEL LOG: {" ".join(intel_log)[:7000]}
        
        TASK: Extract EXACT Decision Maker Data.
        EMAIL PRIORITY:
        1. Owner/CEO personal email.
        2. Senior Decision Maker (Manager/VP) email.
        3. General Company email (info@, etc.).
        If multiple emails exist, pick the BEST one for a decision maker.
        
        RULES: 
        1. Direct Mobile MUST NOT be {phone_office}.
        2. If you see an email in 'EMAILS FOUND BY SCRAPER', use the one that matches a decision maker best.
        
        OUTPUT FORMAT (Separated by '|'):
        OwnerName|DirectMobile|PersonalEmail|LinkedInProfile|HiringStatus|RevenueLossReason
        """
        
        grand_synthesis = call_gemini_ai(final_prompt)
        parts = [p.strip() for p in grand_synthesis.split('|')]
        
        if len(parts) >= 6:
            res_name, res_mobile, res_email, res_link, res_hiring, res_loss = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
            
            # PYTHON FALLBACK: If AI returned N/A for email but we found some, pick the first one
            if (res_email == "N/A" or "@" not in res_email) and all_found_emails:
                res_email = all_found_emails[0]
            
            return res_name, res_mobile, res_email, res_link, res_hiring, res_loss

    except Exception as e:
        print(f"      ⚠️ Intelligence Failure: {e}")
    finally:
        driver.close()
        driver.switch_to.window(original_window)
        
    # Final Python-Only Fallback
    final_email = all_found_emails[0] if all_found_emails else "N/A"
    return found_owner_name, "N/A", final_email, "N/A", "No", "N/A"

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
                        o_name, d_phone, p_email, l_profile, h_status, loss_reason = recursive_intel_hunt(driver, name, city, niche, website, phone_office)
                        
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
