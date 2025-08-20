import wikipedia


wikipedia.set_lang('en')


page_title = 'Pakistan'
try:
    page = wikipedia.page(page_title)
    print(f"Page title: {page.title}")
    print(f"Page summary:\n{page.summary[:500]}...")  
except wikipedia.exceptions.PageError:
    print(f"Page '{page_title}' does not exist.")
except wikipedia.exceptions.DisambiguationError as e:
    print(f"Disambiguation error: {e.options}")