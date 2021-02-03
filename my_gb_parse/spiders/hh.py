import scrapy
from my_gb_parse.loaders import HHjobLoader
from my_gb_parse.loaders import HHcompanyLoader



class HHSpider(scrapy.Spider):
    name = "HH"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113/"]

    xpath_query = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
        'job_urls': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    }

    job_xpath = {
        "job_title": '//h1[@data-qa="vacancy-title"]/text()',
        "wage": '//p[@class="vacancy-salary"]//text()',
        "job_description": '//div[@data-qa="vacancy-description"]//text()',
        "key_skills": '//div[@data-qa="bloko-tag bloko-tag_inline skills-element"]/text()',
        "company_url": '//a[@data-qa="vacancy-company-name"]/@href',
    }


    company_xpath = {
        'company_title': '//h1/span[@data-qa = "company-header-title-name"]/text()',
        'company_web': '//a[contains(@data-qa, "company-site")]/@href',
        'activity_areas': '//div[contains(@class, "employer-sidebar-block")]//p/text()',
        'company_description': '//div[contains(@data-qa, "company-description")]//text()',
        "company_vacancies" : '//a[@data-qa = "employer-page__employer-vacancies-link"]//@href'

    }


    def parse(self, response, **kwargs):
        pagination_links = response.xpath(self.xpath_query["pagination"])
        yield from self.gen_task(response, pagination_links, self.parse)

        job_links = response.xpath(self.xpath_query["job_urls"])
        yield from self.gen_task(response, job_links, self.job_parse)


    def job_parse(self, response):
        loader = HHjobLoader(response=response)
        loader.add_value("job_url", response.url)

        for key, selector in self.job_xpath.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()

        company_links = response.xpath(self.job_xpath["company_url"])
        yield from self.gen_task(response, company_links, self.company_parse)



    def company_parse(self, response):
        loader = HHcompanyLoader(response=response)
        loader.add_value("url", response.url)

        for key, selector in self.company_xpath.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()
        company_vacancies_links = response.xpath(self.company_xpath["company_vacancies"])
        yield from self.gen_task(response, company_vacancies_links, self.parse)




    @staticmethod
    def gen_task(response, link_list, callback):
        for link in link_list:
            yield response.follow(link, callback=callback)



