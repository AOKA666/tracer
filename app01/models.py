from operator import mod
from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=32, db_index=True)
    password = models.CharField(verbose_name='密码', max_length=32)
    email = models.EmailField(verbose_name='邮箱')
    phone = models.CharField(verbose_name='手机号', max_length=16)

    def __str__(self):
        return self.username


class PricePolicy(models.Model):
    """价格策略"""
    category_choices = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他'),
    )
    category = models.SmallIntegerField(verbose_name='收费类型', choices=category_choices, default=1)
    title = models.CharField(verbose_name='标题', max_length=32)
    price = models.PositiveIntegerField(verbose_name='价格')
    project_num = models.PositiveIntegerField(verbose_name='项目数')
    project_member = models.PositiveIntegerField(verbose_name='项目成员数')
    project_space = models.PositiveIntegerField(verbose_name='单项目空间')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小(M)')

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Transaction(models.Model):
    """交易记录"""
    status_choices = (
        (1, '未支付'),
        (2, '已支付')
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices)
    order = models.CharField(verbose_name='订单号', max_length=64, unique=True)
    user = models.ForeignKey(verbose_name='用户', to='UserInfo', on_delete=models.CASCADE)
    price_policy = models.ForeignKey(verbose_name='价格策略', to='PricePolicy', on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='数量(年)', help_text='0表示无期限')
    price = models.IntegerField(verbose_name='实际支付价格')
    start_time = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Project(models.Model):
    """创建的项目"""
    color_choices = (
        (1, "#fa5151"),
        (2, "#c87d2f"),
        (3, "#91d300"),
        (4, "#10aeff"),
        (5, "#6467f0"),
        (6, "#07c160")
    )
    name = models.CharField(verbose_name='项目名', max_length=32)
    color = models.SmallIntegerField(verbose_name='颜色', choices=color_choices, default=3)
    desc = models.CharField(verbose_name='项目描述', max_length=255, null=True, blank=True)
    use_space = models.IntegerField(verbose_name='项目已用空间', default=0)
    star = models.BooleanField(verbose_name='星标', default=False)

    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    bucket = models.CharField(verbose_name='cos桶', max_length=128)


class ProjectUser(models.Model):
    """参加的项目"""
    user = models.ForeignKey(verbose_name='用户', to='UserInfo', related_name='projects', on_delete=models.CASCADE)
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    inviter = models.ForeignKey(verbose_name='邀请者', to='UserInfo', related_name='invites', on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name='星标', default=False)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Wiki(models.Model):
    """文档库"""
    title = models.CharField(verbose_name="标题", max_length=32)
    content = models.TextField(verbose_name="内容")
    project = models.ForeignKey("Project", verbose_name="项目", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", verbose_name="父文章", on_delete=models.CASCADE, related_name="children", blank=True, null=True)
    depth = models.SmallIntegerField(verbose_name="文档层级", default=1)

    def __str__(self):
        return self.title


class FileRepository(models.Model):
    """文件库"""
    name = models.CharField(verbose_name="文件夹名", max_length=32)
    project = models.ForeignKey(verbose_name="所属项目", to="Project", on_delete=models.CASCADE)
    type = models.SmallIntegerField(choices=((1, "文件"), (2, "文件夹")))
    file_size = models.IntegerField(verbose_name="文件大小", null=True, blank=True)
    file_path = models.CharField(verbose_name="文件路径", max_length=256, null=True, blank=True)
    key = models.CharField(verbose_name="COS中的key", max_length=128, blank=True, null=True)
    update_user = models.ForeignKey(verbose_name="更新者", to="UserInfo", on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    parent = models.ForeignKey(verbose_name="父文件夹", to="self", related_name="children", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '<FileRepository %s>' % self.name

