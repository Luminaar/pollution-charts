import wikipedia

wikipedia.set_lang("cs")
summary = wikipedia.summary(wikipedia.search("Oxid uhličitý")[0])

print(repr(summary))
