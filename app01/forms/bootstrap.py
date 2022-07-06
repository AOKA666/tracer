class BootstrapForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control field"
            field.widget.attrs["placeholder"] = '请输入'+field.label
            field.error_messages['required'] = '此字段必须填写'
