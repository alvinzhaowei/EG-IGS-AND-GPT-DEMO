from django import forms


class URL(forms.Form):
    Amazon_item_url = forms.CharField()


class DemoMessage(forms.Form):
    my_text = forms.CharField(widget=forms.Textarea)
