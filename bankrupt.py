from selenium import webdriver
from selenium.webdriver.common.keys import Keys


driver = webdriver.Chrome(executable_path='chromedriver.exe')
driver.get('https://bankrot.fedresurs.ru/DebtorsSearch.aspx')

INN = 575404653331
driver.find_element_by_xpath('//*[@id="ctl00_cphBody_rblDebtorType_1"]').click()
field = driver.find_element_by_xpath('//*[@id="ctl00_cphBody_PersonCode1_CodeTextBox"]')
driver.execute_script(f"arguments[0].value='{INN}'", field)
driver.find_element_by_xpath('//*[@id="ctl00_cphBody_btnSearch"]').click()

print(driver.find_element_by_xpath('//*[@id="ctl00_cphBody_gvDebtors"]/tbody/tr/td').text)
if 'По заданным критериям не найдено ни одной записи. Уточните критерии поиска' == driver.find_element_by_xpath('//*[@id="ctl00_cphBody_gvDebtors"]/tbody/tr/td').text:
    print('Этот человек не числится банкротом')
else:
    print('Этот человек является банкротом')

driver.quit()




