import base
from app01 import models


def run():
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

if __name__ == '__main__':
    run()