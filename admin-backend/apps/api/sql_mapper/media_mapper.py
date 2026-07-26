# coding: utf-8


class MediaMapper:
    @staticmethod
    def select_media_page_list(file_type=None, keyword=None):
        sql = '''
                SELECT id, name, file_path, ext, file_type, file_size, create_time, update_time
                FROM media_file
                WHERE del_flag = '0'
            '''
        if file_type:
            sql += ' AND file_type = %s'
        if keyword:
            sql += ' AND name LIKE %s'
        sql += ' ORDER BY create_time DESC LIMIT %s, %s'
        return sql

    @staticmethod
    def select_media_total_count(file_type=None, keyword=None):
        sql = '''
                SELECT count(1) AS num
                FROM media_file
                WHERE del_flag = '0'
            '''
        if file_type:
            sql += ' AND file_type = %s'
        if keyword:
            sql += ' AND name LIKE %s'
        return sql

    @staticmethod
    def select_media_by_id():
        return '''
                SELECT id, name, file_path, ext, file_type, file_size, create_time, update_time
                FROM media_file
                WHERE id = %s AND del_flag = '0'
            '''

    @staticmethod
    def insert_media():
        return '''
                INSERT INTO media_file
                (name, file_path, ext, file_type, file_size, del_flag, create_time, update_time)
                VALUES (%s, %s, %s, %s, %s, '0', NOW(), NOW())
            '''

    @staticmethod
    def rename_media():
        return '''
                UPDATE media_file
                SET name = %s, update_time = NOW()
                WHERE id = %s AND del_flag = '0'
            '''

    @staticmethod
    def del_media():
        return '''
                UPDATE media_file
                SET del_flag = '1', update_time = NOW()
                WHERE id = %s AND del_flag = '0'
            '''
