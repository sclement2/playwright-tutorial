"""Web scraping module for Indeed job listings.

This module provides functionality to scrape job listings from Indeed.com using Playwright.
It extracts job details including title, company name, location, and salary information,
then saves the data to an Excel file.
"""

# import libraries
import time

import pandas as pd
from playwright.sync_api import sync_playwright


# function to scrape job listings from Indeed
def scrape_indeed(playwright):
    # initiate the browser
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir='./user_data', 
        channel='chrome',
        headless=False,
        no_viewport=True,
    )
    
    # initiate a new page
    page = browser.new_page()

    # keeping track of page count
    page_count = 0

    jobs = []

    # scraping the list with vacancies
    while page_count < 2:  # limiting to first 2 pages for demonstration

        print("SCRAPING LIST ITEMS")

        # setting a delay to avoid sending requests too quickly
        time.sleep(5)

        # navigating to the actual page
        page.goto('https://www.indeed.com/jobs?q=python+developer&start='+str(page_count * 10))

        # getting a list of all vacancies
        vacancies = page.locator('.cardOutline')
        print(f"Found {vacancies.count()} vacancies on page {page_count + 1}")

        # iterating through each vacancy to get details
        for vacancy in vacancies.element_handles():
            item = {}
            item['Title'] = vacancy.query_selector('h2').inner_text().strip()
            item['URL'] = 'https://www.indeed.com' + vacancy.query_selector('a').get_attribute('href')

            jobs.append(item)

        page_count += 1

    all_items = []

    # scraping each vacancy page for more details
    for job in jobs:
        print("SCRAPING DETAIL PAGE")

        # navigating to the vacancy detail page
        page.goto(job['URL'])

        # setting a delay to avoid sending requests too quickly
        time.sleep(5)

        item = {}

        # extracting job description
        item['Title'] = job['Title']
        item['URL'] = job['URL']
        item['CompanyName'] = ""
        item['Location'] = ""
        item['SalaryInfo'] = ""

        company_name = page.get_by_test_id('inlineHeader-companyName')
        if company_name.count() > 0:
            item['CompanyName'] = company_name.inner_text().strip()
        company_location = page.get_by_test_id('inlineHeader-companyLocation')
        if company_location.count() > 0:
            item['Location'] = company_location.inner_text().strip()
        salary_info = page.get_by_test_id('jobsearch-OtherJobDetailsContainer')
        if salary_info.count() > 0:
            item['SalaryInfo'] = salary_info.inner_text().strip()

        all_items.append(item)

    # closing the browser
    browser.close()
    return all_items

with sync_playwright() as playwright:
    jobs = scrape_indeed(playwright)

    # converting the scraped data to a DataFrame
    df = pd.DataFrame(jobs)

    # saving the DataFrame to Excel
    df.to_excel('indeed_job_listings.xlsx', index=False)
    print("Data saved to indeed_job_listings.xlsx")