from django import forms
import re

class UserNameField(forms.Field):
    
    def clean(self,value):
        if len(value) > 16:
            raise forms.ValidationError("Maximum length of username is 16 characters")
        p = re.compile('^\w+-?\w+\.\w+-?\w+\.?\w*-?\w*$')
        a = p.match(value)
        if a:
            return a.group()
        else:
            raise forms.ValidationError("Insert valid username(<firstname>.<lastname>)")