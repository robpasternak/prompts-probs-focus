from pydantic import BaseModel


class BracketingModel(BaseModel):
    name: str
    start_bracket: str
    end_bracket: str

class MarkdownBoldModel(BracketingModel):
    name: str = 'markdown_bold'
    start_bracket: str = '**'
    end_bracket: str = '**'

class MarkdownEmphasisModel(BracketingModel):
    name: str = 'markdown_emphasis'
    start_bracket: str = '*'
    end_bracket: str = '*'

class MarkdownItalicsModel(BracketingModel):
    name: str = 'markdown_italics'
    start_bracket: str = '_'
    end_bracket: str = '_'

class HTMLBoldModel(BracketingModel):
    name: str = 'html_bold'
    start_bracket: str = '<b>'
    end_bracket: str = '</b>'

class HTMLEmphasisModel(BracketingModel):
    name: str = 'html_emphasis'
    start_bracket: str = '<em>'
    end_bracket: str = '</em>'

class HTMLItalicsModel(BracketingModel):
    name: str = 'html_italics'
    start_bracket: str = '<i>'
    end_bracket: str = '</i>'

class HTMLUnderlineModel(BracketingModel):
    name: str = 'html_underline'
    start_bracket: str = '<u>'
    end_bracket: str = '</u>'

ALL_BRACKETING_MODELS : list[BracketingModel] = [
    MarkdownBoldModel(),
    MarkdownEmphasisModel(),
    MarkdownItalicsModel(),
    HTMLBoldModel(),
    HTMLEmphasisModel(),
    HTMLItalicsModel(),
    HTMLUnderlineModel(),
]