from bot_amazon import BotAmazon
from bot_amazon_de import BotAmazonDe

class BotFactory:
  
  def get_bot(self, bot_provider='amazon'):
    if bot_provider == 'amazon':
      bot_provider = BotAmazon()
    if bot_provider == 'amazon-de':
      bot_provider = BotAmazonDe()
    return bot_provider
          
