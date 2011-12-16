# -*- encoding: utf-8 -*-

from django import forms

class SearchForm(forms.Form):
    search_type = forms.ChoiceField(label = 'Search type', choices=[('thread', 'search in threads'), ('post', 'search in posts')], widget=forms.RadioSelect)
    search_text = forms.CharField(label = 'Search text', max_length = 250)
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        
        self.fields['search_type'].widget.attrs.update({'class' : 'search_type'})
        
