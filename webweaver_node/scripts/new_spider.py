#!/usr/bin/env python3


import requests
from webweaver_node.common.enums import ParamTypeEnum
from webweaver_node.mapping import RouteMap


CREATE_SPIDER_ROUTE = RouteMap.DOMAIN+RouteMap.CREATE_SPIDER
CREATE_PARAMS_ROUTE = RouteMap.DOMAIN+RouteMap.CREATE_PARAMS

class Create:

    def _fail(self, msg:str="Bruh..."):
        """Wtf?"""
        print(msg)
        exit(1)


class CreateSpider(Create):

    def __init__(self):
        self.spider_id = None
        self.spider_name = None
        self.spider_type = None
        self.domain = None
        self.description = None


    def create_spider(self):
        """Creates a SpiderAsset DB object and generates all the module files
        required to start scraping.
        """
        self._create_spider_details()
        print(f"\nSpider Name:\t{self.spider_name}\nDirectory:\t{self.spider_name.lower()}/\nSpider Type:\t{self.spider_type}\nStarting Url:\t{self.domain}\nDescription:\t{self.description}\n")
        confirm = input(">> Confirm details? (y/n): ").lower()
        if confirm != 'y':
            self._fail()

        res = self._send_asset_details()
        if res.status_code != 200:
            self._fail("Spider rejected. lol")
        data = res.json()
        self.spider_id = data['spider_id']
        print('spider id: ', self.spider_id)
        print(f"\nSpider \033[1m{self.spider_name}\033[0m successfully created.\n")
        

    def _send_asset_details(self) -> requests.Response:
        """Sends the SpiderAsset details to the app's route for creating 
        new SpiderAsset objects, then returns the deserialized JSON response.
        """
        spider_data = {
            'spider_asset': {
                'spider_name': self.spider_name,
                'domain': self.domain,
                'description': self.description,
                'is_active': True,
            },
            'spider_module': {
                'spider_type': self.spider_type,
            },
        }
        response = requests.post(f"{CREATE_SPIDER_ROUTE}", json=spider_data)
        return response


    def _create_spider_details(self):
        """Creates a dictionary of all details required for a new SpiderAsset model object.
        Does not create the model object until after we have verified 
        """
        self.spider_name = input(">> Spider Name: ")
        spider_type_choice = input(">> Async or Playwright spider? (a/p): ")
        match spider_type_choice.lower():
            case "a":
                self.spider_type = "AsyncSpider"
            case "p":
                self.spider_type = "PlaywrightSpider"
            case _:
                self._fail()
        self.domain = input(">> Website domain: ")
        self.description = input(">> Description: ")
        if self.spider_name[-6:] == "Spider":
            self.spider_name = self.spider_name[:-6]

        return


class CreateParams(Create):

    param_types = ParamTypeEnum
    
    def __init__(self, spider_id:int):
        self.spider_id = spider_id
        self.params = []

    def send_params(self) -> requests.Response:
        """Send the params to the param creation route."""
        param_data = {
            "spider_id": self.spider_id,
            "params": self.params
        }
        res = requests.post(CREATE_PARAMS_ROUTE, json=param_data)
        print(res.status_code)


    def create_params(self):
        """Add as many params as the user wants to self.params and then send
        the params off to the param creation route.
        """
        while True:
            add_param_prompt = input(">> Add a new parameter? (y/n): ").lower()
            if add_param_prompt == 'y':
                self.add_param()
                print()
            elif add_param_prompt == 'n':
                break
            else:
                print("Bruh... (y/n)")
        self.send_params()


    def add_param(self):
        """Add a new parameter to the list of params."""
        d = {}
        d["param_name"] = input(">> Enter param name: ")
        print("\nParam types:")
        for param_type in ParamTypeEnum:
            print(f"  {param_type.value}")
        print()
        while True:
            param_type_choice = input(">> Enter parameter type: ").upper()
            if param_type_choice in ParamTypeEnum.__members__:
                break
            else:
                print("Invalid param type. Please choose from the list above.")
        d["param_type"] = param_type_choice
        d["param_description"] = input(">> Enter parameter description: ")
        print("\nParameter added.")
        self.params.append(d)


if __name__ == "__main__":

    spider_handler = CreateSpider()
    spider_handler.create_spider()
    has_params = input(">> Does this spider have any parameters? (y/n): ").lower()
    if has_params == "y":
        print()
        params_handler = CreateParams(spider_handler.spider_id)
        params_handler.create_params()
    print("\nGoodbye")
    exit(0)