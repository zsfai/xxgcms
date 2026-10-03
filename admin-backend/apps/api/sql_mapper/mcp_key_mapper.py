# coding: utf-8


class McpKeyMapper:
    @staticmethod
    def insert_key():
        return '''
            INSERT INTO mcp_api_key
                (user_id, name, key_prefix, key_hash, site_id, enabled, create_time)
            VALUES (%s, %s, %s, %s, %s, 'Y', NOW())
        '''

    @staticmethod
    def select_by_user():
        return '''
            SELECT
                k.id, k.name, k.key_prefix, k.site_id, k.enabled,
                k.last_used_at, k.create_time, s.name AS site_name, s.desc AS site_desc
            FROM mcp_api_key k
            LEFT JOIN site s ON s.id = k.site_id
            WHERE k.user_id = %s
            ORDER BY k.id DESC
        '''

    @staticmethod
    def select_by_hash():
        return '''
            SELECT
                k.id, k.user_id, k.name, k.key_prefix, k.key_hash,
                k.site_id, k.enabled, k.last_used_at, k.create_time,
                u.user_name, u.status AS user_status
            FROM mcp_api_key k
            INNER JOIN user u ON u.id = k.user_id
            WHERE k.key_hash = %s
            LIMIT 1
        '''

    @staticmethod
    def select_owned():
        return '''
            SELECT id, user_id, enabled
            FROM mcp_api_key
            WHERE id = %s AND user_id = %s
            LIMIT 1
        '''

    @staticmethod
    def revoke():
        return '''
            UPDATE mcp_api_key
            SET enabled = 'N'
            WHERE id = %s AND user_id = %s
        '''

    @staticmethod
    def touch_last_used():
        return '''
            UPDATE mcp_api_key
            SET last_used_at = NOW()
            WHERE id = %s
        '''
