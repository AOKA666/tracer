from django.db import models

# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=32, db_index=True)
    password = models.CharField(verbose_name='密码', max_length=32)
    email = models.EmailField(verbose_name='邮箱')
    phone = models.CharField(verbose_name='手机号', max_length=16)

    def __str__(self):
        return self.username


class PriceStrategy(models.Model):
    """价格策略表"""
    type = models.IntegerField(verbose_name='分类', choices=((0, '免费版'), (1, '收费版')))
    name = models.CharField(verbose_name='标题', max_length=16)
    price = models.IntegerField(verbose_name='价格')
    project_num_count = models.SmallIntegerField(verbose_name='项目个数')
    project_member_count = models.SmallIntegerField(verbose_name='项目成员数量')
    project_size = models.SmallIntegerField(verbose_name='每个项目空间')
    upload_size = models.SmallIntegerField(verbose_name='最大上传文件大小')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """交易表"""
    status = models.IntegerField(verbose_name='状态', choices=((0, '待支付'), (1, '已支付')))
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    price = models.ForeignKey(PriceStrategy, on_delete=models.CASCADE)
    payment = models.SmallIntegerField(verbose_name='实际支付')
    start_time = models.DateTimeField('开始时间', auto_now_add=True)
    end_time = models.DateTimeField('结束时间')
    order_num = models.CharField(verbose_name='订单号', max_length=128)

    def __str__(self):
        return '%s :%s' % (self.user, self.order_num)


class Project(models.Model):
    """项目表，我创建的项目"""
    name = models.CharField(verbose_name='项目名称', max_length=32)
    distract = models.CharField(verbose_name='项目描述', max_length=32)
    color = models.CharField(verbose_name='颜色', max_length=16)
    is_star = models.BooleanField(verbose_name='星标', default=False)
    member_num = models.SmallIntegerField(verbose_name='人数')
    starter = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    size = models.SmallIntegerField(verbose_name='已使用空间')

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    """项目参与者，我参与的项目"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    is_star = models.BooleanField(verbose_name='是否星标')

    def __str__(self):
        return '%s: %s' % (self.user, self.project)

