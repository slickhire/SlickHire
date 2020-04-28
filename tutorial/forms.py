from django import forms  
class StudentForm(forms.Form):  
    file      = forms.FileField() # for creating file input 
    #file.widget.attrs.update({'class':'file btn btn-lg btn-primary'})
