import base
from app01 import models


def run():
    """免费用户价格策略"""
    exist = models.PricePolicy.objects.filter(category=1, title = "个人免费版").exists()
    if not exist:
        models.PricePolicy.objects.create(
            category=1,
            title="个人免费版",
            price=0,
            project_num=3,
            project_member=2,
            project_space=20,
            per_file_size=5
        )
        print("创建完成!")


def run2():
    """VIP价格策略"""
    exist = models.PricePolicy.objects.filter(category=2, title="VIP").exists()
    if not exist:
        models.PricePolicy.objects.create(
            category=2,
            title="VIP",
            price=99,
            project_num=10,
            project_member=5,
            project_space=50,
            per_file_size=20
        )
        print("VIP创建完成!")


def run3():
    """VVIP价格策略"""
    exist = models.PricePolicy.objects.filter(category=2, title="VVIP").exists()
    if not exist:
        models.PricePolicy.objects.create(
            category=2,
            title="VVIP",
            price=199,
            project_num=20,
            project_member=10,
            project_space=100,
            per_file_size=50
        )
        print("VVIP创建完成!")


def run4():
    """SVIP价格策略"""
    exist = models.PricePolicy.objects.filter(category=2, title="SVIP").exists()
    if not exist:
        models.PricePolicy.objects.create(
            category=2,
            title="SVIP",
            price=299,
            project_num=50,
            project_member=50,
            project_space=200,
            per_file_size=100
        )
        print("SVIP创建完成!")


if __name__ == '__main__':
    run()
    run2()
    run3()
    run4()