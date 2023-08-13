"""
Script for automatically playing Cisco's binary game
URL: https://learningcontent.cisco.com/games/binary/index.html

Original idea by Wiliane Souza: https://github.com/Wili-Souza/binary_game_bot
Completely rewritten and enhanced by Markus Schacherbauer.
"""

# Imports
import logging
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from selenium.common import NoSuchElementException

# Chrome Options
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920x1080")
options.add_argument("start-maximised")

logging.basicConfig(level=logging.INFO)


def play_game(driver):
    """
    Encapsulated game logic.
    1) Starts the Game
    2) Checks if new level reached and if so, starts new level
    3) Determines problem class and calls helper function accordingly
    4) Starts again with (2)

    :param driver: The webdriver that is used
    :return: None
    """

    def start():
        """Starts the game by pressing 'Start' button"""

        logging.info("Loading Game …")

        # Load binary game and wait 5 seconds
        driver.get('https://learningcontent.cisco.com/games/binary/index.html')
        sleep(3)

        # Find start button and press it
        start_game_btn = driver.find_element(
            "class name", 'modal-body').find_element("tag name", "button")
        driver.execute_script("arguments[0].click();", start_game_btn)

        logging.info("Started Game")

    def solve_binary_to_decimal(bits):
        """
        Helper function for solving a binary to decimal problem
        :param bits: The buttons of the page containing the bits
        :return: None
        """

        # Convert bits to decimal number
        decimal_number = 0
        for i in range(0, 8):
            if int(bits[i].text) == 1:
                decimal_number += 1 * 2 ** (i + (7 - i * 2))

        # Find numpad button, press it and wait
        number_input_btn = driver.find_element("css selector", 'div[style="transform: translateY(0%);"]').find_element(
            "class name", 'digits')
        driver.execute_script("arguments[0].click();", number_input_btn)
        sleep(1)

        # Reparse page for numpad and wait
        _ = BeautifulSoup(driver.page_source, 'html.parser')
        sleep(1)

        # Find numpad buttons
        digits = driver.find_element("class name", 'calculator.fade-enter-done').find_elements("tag name", 'button')

        # Input solution with numpad
        for number in list(str(decimal_number)):
            if int(number) == 0:
                driver.execute_script("arguments[0].click();", digits[1])
            else:
                driver.execute_script("arguments[0].click();", digits[int(number) + 2])

        # Press enter button
        driver.execute_script("arguments[0].click();", digits[2])

        logging.info(
            f"Solved binary to decimal problem: {''.join(list(map(lambda x: x.text, bits)))} --> {decimal_number}")

    def solve_decimal_to_binary(bits, digit):
        """
        Helper function for solving a decimal to binary problem
        :param bits: The buttons of the page containing the bits
        :param digit: The decimal number that should be converted to bits
        :return: None
        """

        # Convert to list of bits
        binary_string = '{:08b}'.format(digit)
        list_numbers = list(binary_string)

        # Toggle the bits accordingly
        for i in range(0, len(bits)):
            if int(list_numbers[i]) != int(bits[i].text):
                driver.execute_script("arguments[0].click();", bits[i])

        logging.info(f"Solved decimal to binary problem: {digit} --> {binary_string}")

    def control_flow():
        """Main function"""

        # Start the game
        start()

        # Continuously perform steps (2) to (4)
        while True:

            level = 0

            # Wait and parse the page
            sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Check if next level has been reached and start it if so
            try:
                next_level_btn = driver.find_element("class name", 'modal-body').find_element("tag name", "button")
                if next_level_btn is not None:
                    level += 1
                    logging.info(f"Advancing to Level {level}")
                    driver.execute_script("arguments[0].click();", next_level_btn)
                    continue
            except NoSuchElementException:
                pass

            # If problem exists, determine type and solve, otherwise start loop again
            problem = soup.find("div", {"style": 'transform: translateY(0%);'}).select_one('div.digits')
            if problem is None:
                continue

            # Find the buttons containing the bits
            bit_boxes = (driver.find_element(
                "css selector", 'div[style="transform: translateY(0%);"]')
                         .find_elements("tag name", 'button'))

            # Binary to Decimal Problem
            if problem.text == "?":
                solve_binary_to_decimal(bit_boxes)

            # Decimal to Binary Problem
            elif problem.text.isdigit():
                solve_decimal_to_binary(bit_boxes, int(problem.text))

            # Unknown Problem, raise error
            else:
                raise ValueError("Unknown Problem Type encountered")

    # Start control flow
    control_flow()


# Create driver and play the game
chromeDriver = webdriver.Chrome(options=options)
play_game(chromeDriver)
