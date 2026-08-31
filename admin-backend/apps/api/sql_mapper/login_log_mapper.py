# coding: utf-8


class LoginLogMapper:
    @staticmethod
    def insert_log():
        return '''
            INSERT INTO login_log (user_name, action, ip, user_agent, message, create_time)
            VALUES (%s, %s, %s, %s, %s, NOW())
        '''

    @staticmethod
    def select_page_list(where_sql):
        return f'''
            SELECT id, user_name, action, ip, user_agent, message, create_time
            FROM login_log
            {where_sql}
            ORDER BY id DESC
            LIMIT %s, %s
        '''

    @staticmethod
    def select_total_count(where_sql):
        return f'''
            SELECT COUNT(*) AS num
            FROM login_log
            {where_sql}
        '''
