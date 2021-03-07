from bot_amazon import BotAmazon

class BotFactory:
  
  def get_bot(self, bot_provider='amazon'):
    if bot_provider == 'amazon':
      bot_provider = BotAmazon()
    return bot_provider
          
