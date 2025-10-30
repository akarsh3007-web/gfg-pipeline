
import re
import os
import sys
import requests
from selectolax.parser import HTMLParser
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

username = os.getenv("GFG_USERNAME")
password = os.getenv("GFG_PASSWORD")

print(f" Username loaded: {username}")
print(f" Password loaded: {'*' * len(password) if password else 'None'}")

def get_last_valid_cpp_md_link():
    url = "https://github.com/Hunterdii/GeeksforGeeks-POTD"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    html = HTMLParser(response.text)

    tables = html.css("table")
    for table in tables:
        rows = table.css("tr")
        data_rows = [row for row in rows if len(row.css("td")) >= 4]

        for row in reversed(data_rows):
            tds = row.css("td")
            cpp_cell = tds[3]
            link_tag = cpp_cell.css_first("a")
            if link_tag and "href" in link_tag.attributes:
                problem_name = tds[1].text(strip=True)
                return link_tag.attributes["href"], problem_name

    raise Exception("No valid C++ link found in any table")





def extract_cpp_with_playwright(blob_url):
    full_url = f"https://github.com{blob_url}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(full_url)
        page.wait_for_selector("div.highlight-source-c\\+\\+", timeout=10000)

        blocks = page.query_selector_all("div.highlight-source-c\\+\\+")
        for block in blocks:
            pre = block.query_selector("pre")
            if not pre:
                continue

            spans = pre.query_selector_all("span")
            has_pl_k = any("pl-k" in (span.get_attribute("class") or "") for span in spans)
            if has_pl_k:
                cpp_code = pre.inner_text()
                browser.close()
                return cpp_code

        browser.close()
        raise Exception("No valid C++ code block found (none contained pl-k).")
    



def save_cpp_to_file(code, problem_name):
    safe_name = re.sub(r'[^\w\s-]', '', problem_name).replace(' ', '_')
    filename = f"gfg.cpp"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    print(f" Saved to {filename}")





def login_to_gfg(page, username, password):
    page.goto("https://auth.geeksforgeeks.org/")

    page.wait_for_selector("input#luser", timeout=10000)
    page.fill("input#luser", username)

    page.wait_for_selector("input#password", timeout=10000)
    page.fill("input#password", password)

    page.click("button[type='submit']")
    page.wait_for_timeout(3000)
  




def get_potd_problem_link(page):
    page.goto("https://practice.geeksforgeeks.org/problem-of-the-day")
    page.wait_for_selector("#potd_solve_prob", timeout=10000)
    problem_link = page.locator("#potd_solve_prob").get_attribute("href")
    if not problem_link:
        raise Exception(" Could not extract POTD problem link")
    print(" Found POTD problem link:", problem_link)
    return problem_link




def submit_solution(page, cpp_code):
    # Wait for Ace Editor to load
    page.wait_for_selector(".ace_text-input", timeout=10000)

    # Inject code directly into Ace Editor using its API
    page.evaluate(f"""
        const editor = ace.edit(document.querySelector(".ace_editor"));
        editor.setValue({repr(cpp_code)}, -1);  // -1 moves cursor to start
    """)

    # Optional: select C++ language
    try:
        page.select_option("select#language", "C++")
        print(" Language set to C++")
    except:
        print(" Language dropdown not found or already set")

    # Wait for hydration
    page.wait_for_timeout(2000)

    # Submit the solution
    submit_btn = page.locator("button.problems_submit_button__6QoNQ")
    submit_btn.scroll_into_view_if_needed()
    submit_btn.click()

    page.wait_for_timeout(3000)
  

    print(" Submitted solution (via Ace API)")




def run_pipeline():
    print("🌿 Fetching latest C++ POTD from GitHub...")
    blob_md_url, problem_name = get_last_valid_cpp_md_link()
    clean_blob_url = blob_md_url.split('#')[0]
    cpp_code = extract_cpp_with_playwright(clean_blob_url)

    print(f"\n Problem: {problem_name.encode('ascii', 'replace').decode()}\n")
    print(cpp_code)
    save_cpp_to_file(cpp_code, problem_name)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        login_to_gfg(page, username, password)

        problem_link = get_potd_problem_link(page)
        page.goto(problem_link)
        page.wait_for_timeout(3000)
        

        submit_solution(page, cpp_code)

        browser.close()

if __name__ == "__main__":
    run_pipeline()