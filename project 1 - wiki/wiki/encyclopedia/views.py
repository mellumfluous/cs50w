from django.http import HttpResponse
from django.shortcuts import render

import markdown2
import re

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, id):
    if id in util.list_entries():
        return HttpResponse(markdown2.markdown_path(f"entries/{id}.md"))
    else:
        return render(request, "encyclopedia/error.html")
    
def search(request):
    query = request.GET['q']

    matches = []
    for each in util.list_entries():
        if re.search(query, each, re.IGNORECASE):
            return HttpResponse(markdown2.markdown_path(f"entries/{each}.md"))

        if re.search('(.*)'+query.lower()+'(.*)', each.lower()):
            matches.append(each)
    return render(request, "encyclopedia/search.html", {
            "matches": matches
    })
    # return HttpResponse(f'query: {query}\nutil.list_entries(): {util.list_entries()}\nquery type: {type(query)}')

#urls.py

# urlpatterns = [
#     path('search', views.search, name='search
# ]

# test.html

# <form action={% url 'search' %}>
# <input type='text' name='q'>
# <input type='submit'>
# </form>

# views.py

# def search(request):
#     value = request.GET['q']
#     return HttpResponse(f'value')