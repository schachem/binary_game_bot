from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep

# --- Algumas opções para evitar bugs no Selenium, opcional
chromeOptions = webdriver.ChromeOptions()
#chromeOptions.add_argument("--headless")
chromeOptions.add_argument('--disable-gpu')
chromeOptions.add_argument("--no-sandbox")
chromeOptions.add_argument("--disable-dev-shm-usage")
chromeOptions.add_argument("--window-size=1920x1080")
chromeOptions.add_argument("start-maximised")

#Contador para o número de problemas resolvidos pelo bot
contador = 0

driver = webdriver.Chrome('chromedriver.exe', options=chromeOptions)

#Conectando com a página usando o driver
driver.get('https://learningcontent.cisco.com/games/binary/index.html')
sleep(5) #Tempo de carregamento da página

btn_start = driver.find_element_by_class_name('modal-body').find_element_by_tag_name('button')
driver.execute_script("arguments[0].click();", btn_start) #Usar o execute_script evita bucks do .click()

#Função principal
def play(limit):
    contador = 0
    while True:
        #Joga até chegar no limite de problemas resolvidos
        if contador >= limit:
            return

        sleep(2)

        #Parseando página atualizada com BeautifulSoup
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
        except:
            print('Erro ao conectar-se com a página.')
        
        #Verifica o aparecimento de popups e fecha com .click()
        try:
            btn_next_level = driver.find_element_by_class_name('modal-body').find_element_by_tag_name('button')
            if btn_next_level != None:
                driver.execute_script("arguments[0].click();", btn_next_level)
                continue
        except:
            pass

        #Capturando o campo com o problema binário
        problem_class = soup.find("div", {"style" : 'transform: translateY(0%);'}).select_one('div.digits.isProblem')
        
        #Se for None, é outro tipo de problema (exsitem dois)
        if problem_class == None:
            final_number = soup.find("div", {"style" : 'transform: translateY(0%);'}).select_one('div.digits').text

            #Convertendo para binário o número final
            string_binary = '{:08b}'.format(int(final_number))
            list_numbers = list(string_binary)

            #Achando lista de números
            number_boxes = soup.find("div", {"style" : 'transform: translateY(0%);'}).select_one('div.bits').findAll('button')
            for i in range(0, len(number_boxes)):

                #Clicando nos dígitos corretos
                if int(list_numbers[i]) != int(number_boxes[i].text):
                    btn_bit = driver.find_element_by_css_selector('div[style="transform: translateY(0%);"]').find_elements_by_tag_name('button')
                    driver.execute_script("arguments[0].click();", btn_bit[i])

            contador += 1
        else:
            problem_class = soup.find("div", {"style" : 'transform: translateY(0%);'}).select_one('div.digits.isProblem')
            if problem_class == None: #Em caso de atrasos
                continue

            final_number = 0
            #Achando lista de números
            number_boxes = soup.find("div", {"style" : 'transform: translateY(0%);'}).select_one('div.bits').findAll('button')
            
            #Calculando o número final correto
            for i in range(0, 8):
                if int(number_boxes[i].text) == 1:
                    final_number += 1 * 2**(i + (7 - i*2))

            #Clicando na caixa para aparecer a 'calculadora':
            btn_bit = driver.find_element_by_css_selector('div[style="transform: translateY(0%);"]').find_element_by_class_name('digits')
            driver.execute_script("arguments[0].click();", btn_bit)
            sleep(1)

            #Parseando a nova página com a calculadora
            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
            except:
                print('Erro ao conectar-se com a nova página.')

            #Capturando os botões da calculadora
            digits = driver.find_element_by_class_name('calculator.fade-enter-done').find_elements_by_tag_name('button')

            #Clicando nos digitos corretos:
            for number in list(str(final_number)):
                if int(number) == 0:
                    driver.execute_script("arguments[0].click();", digits[1])
                else:
                    driver.execute_script("arguments[0].click();", digits[int(number)+2])
            
            #submit
            driver.execute_script("arguments[0].click();", digits[2])   

            contador += 1

#O bot jogará um número de vezes equivalente ao tamanho da lista abaixo
    #Cada valor corresponde a um número de problemas resolvidos
list_of_limits = [5, 10, 15, 20]
for i in list_of_limits:
    play(i)
    sleep(130) #aguarda até perder para jogar novamente

#Encerrando o driver
driver.close()

print('The end.')



        
