from parser_text import ParserText

class ParserFactory:
  
  def get_parser(self, callback, parser_type='text'):
    if parser_type == 'text':
      parser = ParserText()
      parser.start(callback)
      return parser
          
