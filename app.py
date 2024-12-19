import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import pandas as pd
import time

# Streamlit App
def main():
    st.title("LinkedIn Email Extractor")
    st.write("Enter the LinkedIn post URL to extract email addresses from comments.")

    # Input fields for LinkedIn credentials and post URL
    linkedin_email = st.text_input("LinkedIn Email", type="default")
    linkedin_password = st.text_input("LinkedIn Password", type="password")
    post_url = st.text_input("LinkedIn Post URL")

    # Button to start the process
    if st.button("Extract Emails"):
        if linkedin_email and linkedin_password and post_url:
            with st.spinner("Extracting emails... Please wait!"):
                emails = scrape_emails(linkedin_email, linkedin_password, post_url)
                if emails:
                    # Save emails to CSV
                    df = pd.DataFrame(emails, columns=["Email"])
                    csv_file = "emails.csv"
                    df.to_csv(csv_file, index=False)
                    st.success(f"Extraction complete! {len(emails)} emails found.")
                    st.download_button(
                        label="Download Emails as CSV",
                        data=open(csv_file, "rb"),
                        file_name="emails.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("No emails found. Please check the post URL or try again.")
        else:
            st.error("Please fill in all the required fields.")

# Function to scrape emails using Selenium
import undetected_chromedriver as uc

def scrape_emails(email, password, post_url):
    # Configure headless Chrome with undetected_chromedriver
    options = uc.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")  # Required for environments like Streamlit Cloud
    options.add_argument("--disable-dev-shm-usage")  # Prevent crashes due to limited resources
    
    driver = uc.Chrome(options=options)

    try:
        # Open LinkedIn and log in
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, '//button[text()="Sign in"]').click()
        time.sleep(5)

        # Open the LinkedIn post
        driver.get(post_url)
        time.sleep(5)

        # Scroll to load all comments
        for _ in range(20):  # Adjust based on the number of comments
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Extract comments
        comments = driver.find_elements(By.CLASS_NAME, "comments__comment")
        emails = []

        # Extract emails using regex
        for comment in comments:
            email_matches = re.findall(
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", comment.text
            )
            emails.extend(email_matches)

        # Deduplicate emails
        emails = list(set(emails))

        return emails

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
