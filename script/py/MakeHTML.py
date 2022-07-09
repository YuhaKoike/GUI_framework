def StartTag(tag,attribute={}):
    html = "<"+tag
    for key,val in attribute.items():
        html += " {}='{}'".format(key,val)
        #html += ' ' + key + '="' + val + '"'
    html += '>\n'
    return html

def EndTag(tag):
    return "</{}\n>".format(tag)

def Content(content):
    return content + '\n'

def Element(tag,content="",attribute={}):
    html = StartTag(tag,attribute)
    html += Content(content)
    html = html.replace("\n","")
    html += EndTag(tag)
    return html
