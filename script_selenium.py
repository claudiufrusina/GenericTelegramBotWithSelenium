from dotenv import load_dotenv
from selenium import webdriver
from PIL import Image
from io import BytesIO
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import os
import logging
import asyncio

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up logging to file
file_handler = logging.FileHandler('requests.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(file_handler)

# Clear existing environment variables if necessary
os.environ.pop('User', None)
os.environ.pop('Password', None)

# Load the .env file
load_dotenv()

local_path_screenshot = "screenshots/full_page_screenshot.png"

# Now the environment variables should be updated
User = os.getenv('User')
Password = os.getenv('Password')

class ElementFinderSeleniumBot:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self._screenshot_path = None  # Initialize the screenshot path

    def check_printscreen_folder(self, folder_path):
        # Check if the folder exists
        if not os.path.exists(folder_path):
            # Create the folder
            os.makedirs(folder_path)
            logger.debug(f'Folder "{folder_path}" created.')
        else:
            logger.debug(f'Folder "{folder_path}" already exists.')
        
    # Function to wait for the network to be idle
    def wait_for_network_idle(self, driver, timeout=30):
        driver.execute_script("""
            var callback = arguments[arguments.length - 1];
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/');
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4) {
                    console.log("Network is idle");
                    callback();
                }
            };
            xhr.send();
        """)
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

    def log_http_requests(self, driver):
        driver.execute_script("""
            (function() {
                var open = XMLHttpRequest.prototype.open;
                XMLHttpRequest.prototype.open = function() {
                    this.addEventListener('load', function() {
                        var log = {
                            url: this.responseURL,
                            status: this.status,
                            response: this.responseText
                        };
                        console.log(JSON.stringify(log));
                    });
                    open.apply(this, arguments);
                };

                var fetch = window.fetch;
                window.fetch = function() {
                    return fetch.apply(this, arguments).then(function(response) {
                        response.clone().text().then(function(body) {
                            var log = {
                                url: response.url,
                                status: response.status,
                                response: body
                            };
                            console.log(JSON.stringify(log));
                        });
                        return response;
                    });
                };
            })();
        """)

    # Function to take a screenshot
    def take_screenshot(self, driver):
        self.check_printscreen_folder("screenshots")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{timestamp}.png"
        driver.get_screenshot_as_file(filename)
        logger.debug(f"Screenshot salvato come {filename}")
        self._screenshot_path = filename  # Store the screenshot path

    # Function to take a full page screenshot with particular scrolling
    def get_full_page_screenshot(self, driver, file_path):
        # Scroll to the top of the page
        driver.execute_script("window.scrollTo(0, 0);")
        # Get the total height of the page
        total_height = driver.execute_script("return document.body.scrollHeight")
        # Get the viewport height
        viewport_height = driver.execute_script("return window.innerHeight")
        # Initialize the stitched image
        stitched_image = Image.new('RGB', (driver.execute_script("return document.body.scrollWidth"), total_height))

        for offset in range(0, total_height, viewport_height):
            driver.execute_script(f"window.scrollTo(0, {offset});")
            time.sleep(0.2)
            screenshot = Image.open(BytesIO(driver.get_screenshot_as_png()))
            stitched_image.paste(screenshot, (0, offset))
        # Save the stitched image
        stitched_image.save(file_path)
    # end of get_full_page_screenshot

    # main function to run the script
    async def run_script_on_selenium(self, headless=False):
        # Configure Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--start-fullscreen")  # Start Chrome in fullscreen mode

        # Initialize the driver with the configured options
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Accedi alla pagina di login TO CHANGE
        driver.get('https://www.your_page_placeholder.org/')

        # self.log_http_requests(driver)
        
        # Trova e clicca il pulsante "Login"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Login')]")))
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()

        # Attendi il caricamento della pagina successiva
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))

        logger.debug(f"Read the .env file --> Email: {self.user} and Password: {self.password}")
        # Compila il form di login
        email = driver.find_element(By.ID, 'EMAIL')
        password = driver.find_element(By.ID, 'PASSWORD')
        email.send_keys(self.user)
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)

        SignInXPathSelector = "//button[contains(text(), 'Sign in')]"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, SignInXPathSelector)))
        button = driver.find_element(By.XPATH, SignInXPathSelector)
        button.click()

        # Wait an element to be present before proceeding
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Find some html element before proceeding')]")))

        # click on the element
        driver.find_element(By.ID, "PLACEHOLDER").click()

        # Wait until the network is idle
        self.wait_for_network_idle(driver)

        # Find and click the modify search button
        modify_search_button = driver.find_element(By.XPATH, "//button[@data='SearchButton']")
        modify_search_button.click()

        # Attendi fino a quando la rete è inattiva
        self.wait_for_network_idle(driver)

        await asyncio.sleep(5)  # Wait 5 seconds before taking the screenshot
        # self.take_full_page_screenshot(driver)
        self.get_full_page_screenshot(driver, local_path_screenshot)
        logger.debug(f"Screenshot saved on path {local_path_screenshot}")

        # Find the desired element
        try:
            element = driver.find_element(By.XPATH, "//div[@data='PLACEHOLDER']")
            logger.debug(f"The element has been found: {element.text}")
        except:
            logger.debug("No element found in page")
            
        # close the browser
        driver.quit()

    def get_screenshot_path(self):
        """Getter for the screenshot path."""
        return self._screenshot_path

    def set_screenshot_path(self, path):
        """Setter for the screenshot path."""
        self._screenshot_path = path

def main() -> None:
    # Esegui la funzione ogni 5 minuti
    bot = ElementFinderSeleniumBot(User, Password)
    while True:
        asyncio.run(bot.run_script_on_selenium(headless=False))
        time.sleep(300)  # 300 secondi = 5 minuti

if __name__ == '__main__':
    main()
