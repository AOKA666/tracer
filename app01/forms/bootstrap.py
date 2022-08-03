class BootstrapForm:
    bootstrap_exclude = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in self.bootstrap_exclude:
                continue
            old_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = "{} form-control field".format(old_class)
            field.widget.attrs["placeholder"] = '请输入'+field.label
            field.error_messages['required'] = '此字段必须填写'
