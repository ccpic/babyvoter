from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class Voter:
    def __init__(self, header, cookies):
        self.header = header
        self.cookie = {}
        for i in cookies.split("; "):
            self.cookie[i.split("=")[0]] = i.split("=")[1]
        self.success = 0

    def set_up(self):
        chrome_opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(chrome_options=chrome_opt)
        driver.set_page_load_timeout(30)  # 设置超时报错
        driver.set_script_timeout(30)  # 设置脚本超时时间。
        return driver

    def xpath_babyname(self, driver, index):
        return driver.find_element_by_xpath(
                    "/html/body/div[1]/div[4]/ul/li[%s]/div/p[1]" % index
                )

    def xpath_votenum(self, driver, index):
        return driver.find_element_by_xpath(
                    "/html/body/div[1]/div[4]/ul/li[%s]/div/div" % index
                )

    def xpath_votebtn(self, driver, index):
        return  driver.find_element_by_xpath(
                    "/html/body/div[1]/div[4]/ul/li[%s]/div/div/a" % index
                )

    def get_baby_index(self, driver):
        for i in range(20):
            baby = self.xpath_babyname(driver, i+1)
            if baby.text[:3] == '石箫诚':
                break
        return i+1



    def vote(self, loop_num=1):
        start = time.time()
        start_url = "https://mobile.beile.com/h5/vote/index?id=4"
        delay = 30  # seconds

        for i in range(loop_num):
            driver = self.set_up()

            try:
                driver.get(start_url)
                # 等待30秒或投票按钮可见
                WebDriverWait(driver, delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[1]/div[4]/ul/li[9]/div/div/a")
                    )
                )
                # 向下翻页
                driver.execute_script("window.scrollBy(0,1000)")

                index = self.get_baby_index(driver)

                # 根据XPATH定位宝宝姓名、票数及投票按钮
                baby = self.xpath_babyname(driver, index)
                vote_num = self.xpath_votenum(driver, index)
                vote_btn = self.xpath_votebtn(driver, index)
                highlight(driver, vote_btn)

                # 点击投票
                print("尝试%s %s-%s" % (i+1, baby.text, vote_num.text[:6]))
                action = ActionChains(driver)
                action.move_to_element(vote_btn).click().perform()
                time.sleep(1)
                print("成功 %s-%s" % (baby.text, vote_num.text[:6]))
            # except UnexpectedAlertPresentException:
            #     WebDriverWait(driver, delay).until(EC.alert_is_present())
            #     driver.switch_to.alert.accept()
            #     print("失败")
            #     driver.quit()
            #     continue
            except:
                print("失败")
                driver.close()
                driver.quit()
                continue

            self.success += 1
            driver.close()
            driver.quit()


        print("用时%s秒，尝试%s次，共成功投票%s次" % (time.time() - start, loop_num, self.success))


def highlight(driver, element):
    # 封装好的高亮显示页面元素的方法
    # 使用JavaScript代码将传入的页面元素对象的背景颜色和边框颜色分别
    # 设置为绿色和红色
    driver.execute_script(
        "arguments[0].setAttribute('style',arguments[1]);",
        element,
        "background:green ;border:2px solid red;",
    )


if __name__ == "__main__":
    header = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    cookie = "FSSBBIl1UgzbN7N80S=CIZMmWgUJuIp4X2JSfF2C_RZsqDr5ADMfAnvWR4rsmmSSqyh2B.2Yejdp79k54mk; token=zIECDO4CGEgI2Ov1ZJ7cNTOdBFlZ97WFS5zTCvTn3Dw3CTr4RtlnBWTJAsE; FSSBBIl1UgzbN7N80T=365sqkBMI51dqorpVnTc8f.imnowcodsN5PL8r62XGEBquO6B4gvtiRqVFPe30orUOyuIlCB10VyeRRGCJBY_lFrMhKl0MRFdyNBDJVO43rQ_3W6Ak4MhLnAu70X3.D8keslCDrylI5VwS5R5SYI.NDwDLLu71YxEV_fjcIMi7pBBOslAHL6vxLhjw4dYFOFNrBfPCjrd5zIsfEZ0dP_.zue7OY013V5N_ncZpOpH.BvsE5pGMlCBw_dxirKoCcHBnH9BcpUkXp7YfimkIKycYe6wKSe76VYCx1xHUGs.9zbhClZmoEr3tMKzP.lkjIcHEBmTUBq4MOeFgXaohjX6Q7kStW9nKfcBagu.tPYauMzCbq"
    v = Voter(header=header, cookies=cookie)
    v.vote(30000)
