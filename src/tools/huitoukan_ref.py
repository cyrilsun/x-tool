import pymysql
import logging
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('WorkOrderTool')

# 退回回头看待处理
class WorkOrderBackTool:
    def __init__(self, host: str, port: int, user: str, password: str, database: str = None):
        """
        初始化工单处理工具类，建立数据库连接
        
        Args:
            host: 数据库主机地址
            port: 数据库端口
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称（可选）
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
    def connect(self):
        """
        连接到数据库
        
        Returns:
            bool: 连接成功返回 True，失败返回 False
        """
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()
    
    def huitoukan_to_handle(self, order_list: List[str]):
        """
        移到回头看待处理
        Args:
            order_list: 工单列表，每个工单是一个工单号
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        if not self.connection or not self.connection.open:
            if not self.connect():
                return {"status": "error", "message": "数据库连接失败"}
        
        try:
            with self.connection.cursor() as cursor:
                results = []
                # 遍历工单列表
                for order_id in order_list:
                    # 查询工单信息
                    sql = "SELECT id, gdh, qdcb, htkzt, htkshzt, htkclfs, htkclzt FROM tb_gov_hot_line WHERE gdh = %s"
                    cursor.execute(sql, (order_id,))
                    result = cursor.fetchall()
                    # 输出result的值
                    logger.info(f'根据工单号: {order_id}, 查询工单信息: {result}')
                    
                    if not result:
                        results.append({"status": "error", "message": f"工单 {order_id} 不存在", "order": order_id})
                        continue
                    # 判断查询列表大于1条
                    if len(result) > 1:
                        # 处理重办单 qdcb=1的工单
                        for item in result:
                            if item['qdcb'] == 1:
                                # 更新工单表回头看状态
                                sql1 = "update tb_gov_hot_line set htkzt =1, htkshzt=0, htkclfs=0, htkclzt=0 WHERE id = %s"
                                logger.info(f'执行更新重办工单表回头看状态SQL: {sql1}, 参数: {item["id"]}')
                                cursor.execute(sql1, (item['id'],))
                                # 更新办理部门回头看状态
                                sql2 = "update tb_gov_hot_line_handle_department set htkzt =1, htkshzt=0, htkclfs=0, htkclzt=0 WHERE event_id = %s"
                                logger.info(f'执行更新重办单办理部门回头看状态SQL: {sql2}, 参数: {item["id"]}')
                                cursor.execute(sql2, (item['id'],))
                            else:
                                # 办理单移除回头看
                                sql1 = "update tb_gov_hot_line set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE id = %s"
                                logger.info(f'执行更新重办工单表回头看状态SQL: {sql1}, 参数: {item["id"]}')
                                cursor.execute(sql1, (item['id'],))
                                # 更新办理部门回头看状态
                                sql2 = "update tb_gov_hot_line_handle_department set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE event_id = %s"
                                logger.info(f'执行更新重办单办理部门回头看状态SQL: {sql2}, 参数: {item["id"]}')
                                cursor.execute(sql2, (item['id'],))
                    else:
                        for item in result:
                            # 更新办理单工单表回头看状态
                            sql1 = "update tb_gov_hot_line set htkzt =1, htkshzt=0, htkclfs=0, htkclzt=0 WHERE id = %s"
                            logger.info(f'执行更新办理单工单表回头看状态SQL: {sql1}, 参数: {item["id"]}')
                            cursor.execute(sql1, (item['id'],))
                            # 更新办理部门回头看状态
                            sql2 = "update tb_gov_hot_line_handle_department set htkzt =1, htkshzt=0, htkclfs=0, htkclzt=0 WHERE event_id = %s"
                            logger.info(f'执行更新办理单办理部门回头看状态SQL: {sql2}, 参数: {item["id"]}')
                            cursor.execute(sql2, (item['id'],))
                # 提交事务
                self.connection.commit()
                return {"status": "success", "results": results}
                
        except Exception as e:
            self.connection.rollback()
            return {"status": "error", "message": f"处理工单时发生错误: {str(e)}"}
        finally:
            self.close()


    def huitoukan_qd_pass(self, order_list: List[str]):
        """
        更新回头看审核状态-青岛已通过
        Args:
            order_list: 工单列表，每个工单是一个工单号

        Returns:
            Dict[str, Any]: 处理结果
        """
        if not self.connection or not self.connection.open:
            if not self.connect():
                return {"status": "error", "message": "数据库连接失败"}

        try:
            with self.connection.cursor() as cursor:
                results = []
                # 遍历工单列表
                for order_id in order_list:
                    # 查询工单信息
                    sql = "SELECT id, gdh, qdcb, htkzt, htkshzt, htkclfs, htkclzt FROM tb_gov_hot_line WHERE gdh = %s"
                    cursor.execute(sql, (order_id,))
                    result = cursor.fetchall()
                    # 输出result的值
                    logger.info(f'根据工单号: {order_id}, 查询工单信息: {result}')

                    if not result:
                        results.append({"status": "error", "message": f"工单 {order_id} 不存在", "order": order_id})
                        continue
                    # 判断查询列表大于1条
                    if len(result) > 1:
                        # 处理重办单 qdcb=1的工单
                        for item in result:
                            if item['qdcb'] == 1:
                                # 更新工单表回头看状态
                                sql1 = "update tb_gov_hot_line set htkzt =3, htkshzt=3, htkclfs=1, htkclzt=1 WHERE id = %s"
                                logger.info(f'执行更新重办工单表回头看审核状态SQL: {sql1}, 参数: {item["id"]}')
                                cursor.execute(sql1, (item['id'],))
                                # 更新办理部门回头看状态
                                sql2 = "update tb_gov_hot_line_handle_department set htkzt =3, htkshzt=3, htkclfs=1, htkclzt=1 WHERE event_id = %s"
                                logger.info(f'执行更新重办单办理部门回头看审核状态SQL: {sql2}, 参数: {item["id"]}')
                                cursor.execute(sql2, (item['id'],))
                    else:
                        for item in result:
                            # 更新办理单工单表回头看状态
                            sql1 = "update tb_gov_hot_line set htkzt =3, htkshzt=3, htkclfs=1, htkclzt=1 WHERE id = %s"
                            logger.info(f'执行更新办理单工单表回头看状态SQL: {sql1}, 参数: {item["id"]}')
                            cursor.execute(sql1, (item['id'],))
                            # 更新办理部门回头看状态
                            sql2 = "update tb_gov_hot_line_handle_department set htkzt =3, htkshzt=3, htkclfs=1, htkclzt=1 WHERE event_id = %s"
                            logger.info(f'执行更新办理单办理部门回头看审核状态SQL: {sql2}, 参数: {item["id"]}')
                            cursor.execute(sql2, (item['id'],))
                # 提交事务
                self.connection.commit()
                return {"status": "success", "results": results}

        except Exception as e:
            self.connection.rollback()
            return {"status": "error", "message": f"处理工单时发生错误: {str(e)}"}
        finally:
            self.close()


    def huitoukan_pass_remove(self, order_list: List[str]):
        """
        回头看审核-已通过 移除待处理
        Args:
            order_list: 工单列表，每个工单是一个工单号

        Returns:
            Dict[str, Any]: 处理结果
        """
        if not self.connection or not self.connection.open:
            if not self.connect():
                return {"status": "error", "message": "数据库连接失败"}

        try:
            with self.connection.cursor() as cursor:
                results = []
                # 遍历工单列表
                for order_id in order_list:
                    # 查询工单信息
                    sql = "SELECT id, gdh, qdcb, htkzt, htkshzt, htkclfs, htkclzt FROM tb_gov_hot_line WHERE gdh = %s and htkzt = 1"
                    cursor.execute(sql, (order_id,))
                    result = cursor.fetchall()
                    # 输出result的值
                    logger.info(f'根据工单号: {order_id}, 查询工单信息: {result}')

                    if not result:
                        results.append({"status": "error", "message": f"工单 {order_id} 不存在", "order": order_id})
                        continue
                    for item in result:
                        # 更新工单表回头看状态
                        sql1 = "update tb_gov_hot_line set htkzt =0, htkshzt=3, htkclfs=1, htkclzt=1 WHERE id = %s"
                        logger.info(f'执行更新工单表回头看待处理状态SQL: {sql1}, 参数: {item["id"]}')
                        cursor.execute(sql1, (item['id'],))
                        # 更新办理部门回头看状态
                        sql2 = "update tb_gov_hot_line_handle_department set htkzt =0, htkshzt=3, htkclfs=1, htkclzt=1 WHERE event_id = %s"
                        logger.info(f'执行更新办理部门回头看待处理状态SQL: {sql2}, 参数: {item["id"]}')
                        cursor.execute(sql2, (item['id'],))
                # 提交事务
                self.connection.commit()
                return {"status": "success", "results": results}

        except Exception as e:
            self.connection.rollback()
            return {"status": "error", "message": f"处理工单时发生错误: {str(e)}"}
        finally:
            self.close()


    def huitoukan_remove(self):
        """
        移出回头看 微信、省政务网站、追加工单
        Args:
            order_list: 工单列表，每个工单是一个工单号

        Returns:
            Dict[str, Any]: 处理结果
        """
        if not self.connection or not self.connection.open:
            if not self.connect():
                return {"status": "error", "message": "数据库连接失败"}

        try:
            with self.connection.cursor() as cursor:
                results = []
                # 遍历工单列表
                # for order_id in order_list:
                # 查询工单信息
                sql = "SELECT id, gdh, qdcb, htkzt, htkshzt, htkclfs, htkclzt FROM tb_gov_hot_line WHERE htkzt = 1 and (gdh like %s or slqd in (8, 60))"
                cursor.execute(sql, ('%-%',))
                result = cursor.fetchall()
                # 输出result的值
                logger.info(f'查询工单信息: {result}')

                if result:
                    for item in result:
                        # 更新工单表回头看状态
                        sql1 = "update tb_gov_hot_line set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE id = %s"
                        logger.info(f'工单表移出回头看SQL: {sql1}, 参数: {item["id"]}')
                        cursor.execute(sql1, (item['id'],))
                        # 更新办理部门回头看状态
                        sql2 = "update tb_gov_hot_line_handle_department set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE event_id = %s"
                        # logger.info(f'办理部门表移出回头看SQL: {sql2}, 参数: {item["id"]}')
                        cursor.execute(sql2, (item['id'],))
                # 提交事务
                self.connection.commit()
                return {"status": "success", "results": results}

        except Exception as e:
            self.connection.rollback()
            return {"status": "error", "message": f"处理工单时发生错误: {str(e)}"}
        finally:
            self.close()


    def huitoukan_remove_2(self, order_list: List[str]):
        """
        移出回头看
        Args:
            order_list: 工单列表，每个工单是一个工单号

        Returns:
            Dict[str, Any]: 处理结果
        """
        if not self.connection or not self.connection.open:
            if not self.connect():
                return {"status": "error", "message": "数据库连接失败"}

        try:
            with self.connection.cursor() as cursor:
                results = []
                # 遍历工单列表
                for order_id in order_list:
                    # 查询工单信息
                    sql = "SELECT id, gdh, qdcb, htkzt, htkshzt, htkclfs, htkclzt FROM tb_gov_hot_line WHERE gdh = %s"
                    cursor.execute(sql, (order_id,))
                    result = cursor.fetchall()
                    # 输出result的值
                    logger.info(f'根据工单号: {order_id}, 查询工单信息: {result}')

                    if not result:
                        results.append({"status": "error", "message": f"工单 {order_id} 不存在", "order": order_id})
                        continue
                    for item in result:
                        # 更新工单表回头看状态
                        sql1 = "update tb_gov_hot_line set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE id = %s"
                        logger.info(f'执行更新工单表回头看待处理状态SQL: {sql1}, 参数: {item["id"]}')
                        cursor.execute(sql1, (item['id'],))
                        # 更新办理部门回头看状态
                        sql2 = "update tb_gov_hot_line_handle_department set htkzt =0, htkshzt=0, htkclfs=0, htkclzt=0 WHERE event_id = %s"
                        logger.info(f'执行更新办理部门回头看待处理状态SQL: {sql2}, 参数: {item["id"]}')
                        cursor.execute(sql2, (item['id'],))
                # 提交事务
                self.connection.commit()
                return {"status": "success", "results": results}

        except Exception as e:
            self.connection.rollback()
            return {"status": "error", "message": f"处理工单时发生错误: {str(e)}"}
        finally:
            self.close()


    def huitoukan_qd_pass2(self, order_list: List[str]):
        """
        更新回头看青岛待审核状态工单-设置青岛已通过
        Args:
            order_list: 工单列表，每个工单是一个工单号

        Returns:
            Dict[str, Any]: 处理结果
        """
        if not self.connection or not self.connection.open:
            if not self.connect():
                return {"status": "error", "message": "数据库连接失败"}

        try:
            with self.connection.cursor() as cursor:
                results = []
                # 遍历工单列表
                for order_id in order_list:
                    # 查询工单信息
                    sql = "SELECT id, gdh, qdcb, htkzt, htkshzt, htkclfs, htkclzt FROM tb_gov_hot_line WHERE gdh = %s and htkshzt = 2"
                    cursor.execute(sql, (order_id,))
                    result = cursor.fetchall()
                    # 输出result的值
                    logger.info(f'根据工单号: {order_id}, 查询工单信息: {result}')

                    if not result:
                        results.append({"status": "error", "message": f"工单 {order_id} 不存在", "order": order_id})
                        continue
                    # 判断查询列表大于1条
                    if len(result) > 1:
                        # 处理重办单 qdcb=1的工单
                        for item in result:
                            if item['qdcb'] == 1:
                                # 更新工单表回头看状态
                                sql1 = "update tb_gov_hot_line set htkshzt=3 WHERE id = %s"
                                logger.info(f'执行更新重办工单表回头看审核状态SQL: {sql1}, 参数: {item["id"]}')
                                cursor.execute(sql1, (item['id'],))
                                # 更新办理部门回头看状态
                                sql2 = "update tb_gov_hot_line_handle_department set htkshzt=3 WHERE event_id = %s"
                                logger.info(f'执行更新重办单办理部门回头看审核状态SQL: {sql2}, 参数: {item["id"]}')
                                cursor.execute(sql2, (item['id'],))
                    else:
                        for item in result:
                            # 更新办理单工单表回头看状态
                            sql1 = "update tb_gov_hot_line set  htkshzt=3 WHERE id = %s"
                            logger.info(f'执行更新办理单工单表回头看状态SQL: {sql1}, 参数: {item["id"]}')
                            cursor.execute(sql1, (item['id'],))
                            # 更新办理部门回头看状态
                            sql2 = "update tb_gov_hot_line_handle_department set htkshzt=3 WHERE event_id = %s"
                            logger.info(f'执行更新办理单办理部门回头看审核状态SQL: {sql2}, 参数: {item["id"]}')
                            cursor.execute(sql2, (item['id'],))
                # 提交事务
                self.connection.commit()
                return {"status": "success", "results": results}

        except Exception as e:
            self.connection.rollback()
            return {"status": "error", "message": f"处理工单时发生错误: {str(e)}"}
        finally:
            self.close()

# 处理回头看工单状态
if __name__ == "__main__":
    # 初始化工单处理工具
    work_order_tool = WorkOrderBackTool(
        host="112.6.205.8",
        port=35403,
        user="root",
        password="$927%Nauk6C5@*J4qP",
        database="jiaoxinban"  # 数据库 work_order_db
    )
    
    # 工单列表
    orders = [
        "250405085102166202",
        "250410095337832502",
        "250508112737568102",
        "250306081853252102"
        # "250924134302869702"
    ]

    # 设置选项：
    # 1表示移到回头看待处理(htkzt=1,htkshzt=0,htkclfs=0,htkclzt=0)
    # 2表示青岛已通过(htkzt=3,htkshzt=3,htkclfs=1,htkclzt=1)
    # 3青岛通过移出待处理(htkzt=0,htkshzt=3,htkclfs=1, htkclzt=1)
    # 4移出回头看(htkzt=0,htkshzt=0,htkclfs=0,htkclzt=0) - 微信、省政务网站、追加工单等
    # 5移除回头看(htkzt=0,htkshzt=0,htkclfs=0,htkclzt=0)
    # 6青岛已通过（htkshzt=3 青岛查询待审核的工单,不修改其它状态）
    option = 1 # 可以修改为1或2来选择不同的处理方法

    # 根据选项调用不同的方法
    if option == 1:
        # 移到回头看待处理
        result = work_order_tool.huitoukan_to_handle(orders)
        logger.info(f"移入回头看待处理结果={result}")
    elif option == 2:
        # 设置回头看审核状态 - 青岛已通过
        result = work_order_tool.huitoukan_qd_pass(orders)
        logger.info(f"青岛已通过处理结果={result}")
    elif option == 3:
        # 回头看审核已通过 移出待处理
        result = work_order_tool.huitoukan_pass_remove(orders)
        logger.info(f"青岛已通过回头看，移出待处理={result}")
    elif option == 4:
        # 移出待处理(微信、省政务网站、追加工单)
        result = work_order_tool.huitoukan_remove()
        logger.info(f"青岛已通过回头看，移出待处理={result}")
    elif option == 5:
        # 移出回头看
        result = work_order_tool.huitoukan_remove_2(orders)
        logger.info(f"移出回头看={result}")
    elif option == 6:
        # 移出回头看
        result = work_order_tool.huitoukan_qd_pass2(orders)
        logger.info(f"移出回头看={result}")
    else:
        logger.error("无效的选项")

    logger.info(f"处理回头看工单，重试结果={result}")