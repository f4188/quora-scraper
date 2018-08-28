
# from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import json

import argparse

class JsonWriter(object):

    def open(self):
        with open('./quora.json', 'r+') as f:
        	try:
        		self.data = json.load(f)
        		return self.data
        	except ValueError:
        		self.data = dict()

    def close(self):
        with open('quora.json', 'w') as f:
        	f.write(json.dumps(self.data))

    def process_item(self, item):
        self.data[item['url']] = item
        return item

    def process_item_write_im(self,item):
    	self.data[item['url']] = item
    	with open('quora.json', 'w') as f:
        	f.write(json.dumps(self.data))
        return item

class elements_added(object):

	def __init__(self):
		self.numElems = 0

	def __call__(self, driver):
		elemList = driver.find_elements(By.XPATH, '//a[@class="question_link"]')
		if len(elemList) > self.numElems:
			self.numElems = len(elemList)
			return elemList
		else:
			return False

class element_is_present(object):

	def __init__(self, by, locator):
		self.locator = locator
		self.by = by
		self.numElems = 0

	def __call__(self, driver):
		elem = driver.find_elements(self.by, self.locator)
		if elem:
			return elem
		else:
			return False

def init():
	opts = Options()
	opts.set_headless()
	# return Firefox(options=opts)
	return Chrome(options=opts)

def fetchQURLs(N, attempts):
	browser = init()
	browser.get('https://www.quora.com/search?q=vaccine&type=question')
	wait = WebDriverWait(browser, 10)
	elemList = []

	while len(elemList) < N:
		print('Num elements found: %d' % len(elemList))
		browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
		try:
			elemList.extend(wait.until(elements_added())[len(elemList):])
		except TimeoutException:
			attempts = attempts - 1
			if not attempts:
				break

	urls = [elem.get_attribute('href') for elem in elemList]

def fetchFAQS():

	browser = init()
	wait = WebDriverWait(browser, 10)

	print('opening json file')
	writer = JsonWriter()
	data = writer.open()

	for url in data.keys():

		if data[url].has_key('question') and data[url].has_key('answer'):
			continue

		print("fetch faq at: %s" % url)
		item = dict()
		item['url'] = url

		browser.get(url)

		try:
			item['question'] = wait.until(element_is_present(By.XPATH, '//div[@class="header"]//h1'))[0].text
			item['answer'] = wait.until(element_is_present(By.XPATH, '//div[@class="ui_qtext_expanded"]'))[0].text
			print('Q: %s' % item['question'])
			print('A: %s' % item['answer'])
			writer.process_item_write_im(item)
		except TimeoutException:
			print('Timeout')
			#break

	#writer.close()

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='scrape quora')
	parser.add_argument('-N', '--count', type=int, default=1000, help="number of questions to fetch")
	parser.add_argument('-A','--attempts', type=int, default=3, help="number of timeouts")
	#parser.add_argument('-J', type=)
	args = parser.parse_args()

	print('fetching questions')
	# fetchQURLs(args.count, args.attempts)
	fetchFAQS()

	print('finished')

