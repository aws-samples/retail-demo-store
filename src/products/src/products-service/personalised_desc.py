import langchain

class PersonalisedDescriptionGenerator:
    bedrockllm = langchain.llms.Bedrock(...)
    prompt_template = ""
        
        
    def get_user_details(self, user):
        '''
        Get user details from users service.
        :param user:
        :return:
        :rtype: dict
        
        '''
        ...
        

        
    def make_prompt(self, user_details,product_details):
        '''
        Generate prompt for the description generator.
        :param user_details:
        :param product_details:
        :return: prompt to be passed to bedrock.
        :rtype: str
        
        '''
        ...

    
    def generate_description(self, user, product):
       '''
       Generate personalised description for the user.
       :param user:
       :return:
       :rtype: dict
       
       '''
       ...
       prompt = self.make_prompt(user,product)
       return self.bedrockllm(prompt)