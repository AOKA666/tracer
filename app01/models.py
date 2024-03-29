from operator import mod
from statistics import mode
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

    def __str__(self):
        return self.title


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
    use_space = models.IntegerField(verbose_name='项目已用空间', default=0, help_text="字节")
    star = models.BooleanField(verbose_name='星标', default=False)

    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    bucket = models.CharField(verbose_name='cos桶', max_length=128)

    def __str__(self):
        return self.name


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
    key = models.CharField(verbose_name="COS中的key", max_length=256, blank=True, null=True)
    update_user = models.ForeignKey(verbose_name="更新者", to="UserInfo", on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    parent = models.ForeignKey(verbose_name="父文件夹", to="self", related_name="children", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '<FileRepository %s>' % self.name


class Module(models.Model):
    project = models.ForeignKey(verbose_name="项目", to='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name="模块名", max_length=32)

    def __str__(self):
        return self.title


class IssueType(models.Model):
    default_type = ['任务','功能','Bug']
    project = models.ForeignKey(verbose_name="项目", to='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name="问题类型", max_length=32)

    def __str__(self):
        return self.title


class Issue(models.Model):
    """问题"""
    project = models.ForeignKey(verbose_name="项目",to="Project", on_delete=models.CASCADE)
    issue_type = models.ForeignKey(verbose_name="问题类型", to="IssueType", on_delete=models.CASCADE)
    module = models.ForeignKey(verbose_name="模块", to="Module", blank=True, null=True, on_delete=models.CASCADE)
    subject = models.CharField(verbose_name="主题", max_length=128)
    desc = models.TextField(verbose_name="问题描述")
    priority_choices = (
        ('danger', '高'),
        ('warning', '中'),
        ('success', '低')
    )
    priority = models.CharField(verbose_name="优先级", max_length=16, choices=priority_choices, default='danger')
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)
    assign = models.ForeignKey(verbose_name="指派", to='UserInfo', related_name='task', null=True, blank=True, on_delete=models.CASCADE)
    attention = models.ManyToManyField(verbose_name='关注者', to='UserInfo', blank=True)
    start_date = models.DateField(verbose_name='开始日期', blank=True, null=True)
    end_date = models.DateField(verbose_name='结束日期', blank=True, null=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式')
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)
    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', blank=True, null=True, on_delete=models.SET_NULL)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='issues', on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_update_time = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject


class IssueReply(models.Model):
    """问题记录"""
    issue = models.ForeignKey(verbose_name="问题", to='Issue', on_delete=models.CASCADE)
    creator = models.ForeignKey(verbose_name="记录者", to='UserInfo', on_delete=models.CASCADE)
    content = models.CharField(verbose_name="记录内容", max_length=32)
    type_choices = (
        (1, '修改记录'),
        (2, '回复')
    )
    type = models.SmallIntegerField(verbose_name="记录类型", choices=type_choices)
    time = models.DateTimeField(verbose_name="记录时间", auto_now_add=True)
    parent = models.ForeignKey(verbose_name="父记录", to="self", blank=True, null=True, on_delete=models.CASCADE)
    depth = models.SmallIntegerField(verbose_name="深度", default=1)


class ProjectInvite(models.Model):
    """项目邀请码"""
    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.CASCADE)
    code = models.CharField(verbose_name="邀请码", max_length=128, unique=True)
    count = models.PositiveIntegerField(verbose_name="限制数量", null=True, blank=True, help_text="空表示无数量限制")
    use_count = models.PositiveIntegerField(verbose_name="已邀请数量", default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.SmallIntegerField(verbose_name="有效期", choices=period_choices, default=1440)
    inviter = models.ForeignKey(verbose_name="邀请者", to="UserInfo", related_name="invite", on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)