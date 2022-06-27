import sys
import os
import django


base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(base_dir)
sys.path.append(base_dir)
# 加载配置文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracer.settings')
# 启动django服务
django.setup()

from app02.models import PriceStrategy

"""
    type = models.IntegerField(verbose_name='分类', choices=((0, '免费版'), (1, '收费版')))
    name = models.CharField(verbose_name='标题', max_length=16)
    price = models.IntegerField(verbose_name='价格')
    project_num_count = models.SmallIntegerField(verbose_name='项目个数')
    project_member_count = models.SmallIntegerField(verbose_name='项目成员数量')
    project_size = models.SmallIntegerField(verbose_name='每个项目空间')
    upload_size = models.SmallIntegerField(verbose_name='最大上传文件大小')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
"""
PriceStrategy.objects.create(
    type=0,
    name='免费用户',
    price=0,
    project_num_count=5,
    project_member_count=5,
    project_size=10,
    upload_size= 2
)
print("用户初始化完成")