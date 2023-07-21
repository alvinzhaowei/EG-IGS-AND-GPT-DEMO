from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import URL
from .EIGS_test_customized_input import EIGS_Tester


def home_view(request):
    tester = EIGS_Tester()
    print("initialized tester")
    if request.method == 'POST':
        form = URL(request.POST)
        if form.is_valid():
            text = form.cleaned_data['Amazon_item_url']
            flag, des = tester.crawl_description(text)
            if flag == 0:
                return render(request, 'home.html', {
                    'form': form, 'description': des,
                })
            else:
                messages, target_node = tester.test_EIGS(None)
                text = ""
                # print(messages)
                for message in messages:
                    if message == '':
                        continue
                    if len(message) > 200:
                        text += message[:200] + '...\n'
                    else:
                        text += message + '...\n'
                text += target_node + '\n'
                return render(request, 'home.html', {
                    'form': form, 'description': ":" + des[:200] + "... (omitted from here)", 'text': text
                })
    else:
        form = URL()

    return render(request, 'home.html', {
        'form': form,
    })
