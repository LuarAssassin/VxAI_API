from django.core.management.base import BaseCommand
from django.db import connection
import uuid

class Command(BaseCommand):
    help = '修复数据库中的UUID格式问题'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始修复UUID格式...'))
        
        # 使用原始SQL查询获取所有用户ID
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users_customuser")
            user_ids = cursor.fetchall()
        
        fixed_count = 0
        
        for (user_id,) in user_ids:
            try:
                # 尝试将ID转换为UUID对象
                uuid_obj = uuid.UUID(str(user_id))
                # ID格式正确，不需要修复
                continue
            except ValueError:
                # 如果ID不是有效的UUID格式，则生成新的UUID
                new_uuid = str(uuid.uuid4())
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users_customuser SET id = %s WHERE id = %s",
                        [new_uuid, user_id]
                    )
                    if cursor.rowcount > 0:
                        fixed_count += 1
                        self.stdout.write(self.style.WARNING(f'用户ID格式无效，已从 {user_id} 更新为 {new_uuid}'))
        
        self.stdout.write(self.style.SUCCESS(f'UUID修复完成！共修复了 {fixed_count} 个用户记录。')) 