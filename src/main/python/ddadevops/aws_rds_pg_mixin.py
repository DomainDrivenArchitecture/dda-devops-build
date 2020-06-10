from .python_util import execute
from .credential import gopass_password_from_path, gopass_field_from_path
from .devops_build import DevopsBuild


def add_aws_rds_pg_mixin_config(config, rds_host_name, db_name,
                                rds_resolve_dns=False,
                                db_port='5432'):
    config.update({'AwsRdsPgMixin':
                   {'rds_host_name': rds_host_name,
                    'db_name': db_name,
                    'rds_resolve_dns': rds_resolve_dns,
                    'db_port': db_port,
                    }})
    return config


class AwsRdsPgMixin(DevopsBuild):

    def __init__(self, project, config):
        super().__init__(project, config)
        aws_rds_pg_mixin_config = config['AwsRdsPgMixin']
        self.rds_host_name = aws_rds_pg_mixin_config['rds_host_name']
        self.rds_resolve_dns = aws_rds_pg_mixin_config['rds_resolve_dns']
        self.db_name = aws_rds_pg_mixin_config['db_name']
        self.db_port = aws_rds_pg_mixin_config['db_port']

    def execute_pg_rds_sql(self, user, password, sql):
        if self.rds_resolve_dns:
            host_cmd = "dig " + self.rds_host_name + " +short | head -n1"
            host = execute(host_cmd, shell=True)
        else:
            host = self.rds_host_name

        cmd = "PGUSER=" + user + " PGPASSWORD=" + password + \
            " psql --dbname=" + self.db_name + " --host=" + host + " --port=" + self.db_port + \
            " --set=sslmode=require -Atc \"" + sql + "\""
        result = execute(cmd, shell=True)
        print("PSQL: ", host, result.rstrip())
        return result

    def alter_db_user_password(self, gopass_path):
        user_name = gopass_field_from_path(gopass_path, 'user')
        user_old_password = gopass_field_from_path(gopass_path, 'old-password')
        user_new_password = gopass_password_from_path(gopass_path)

        self.execute_pg_rds_sql(user_name, user_old_password,
                                "ALTER ROLE " + user_name + " WITH PASSWORD '" + user_new_password + "';")
        print("changed password:", user_name)

    def add_new_user(self, gopass_path_superuser, gopass_path_new_user, group_role):
        superuser_name = gopass_field_from_path(gopass_path_superuser, 'user')
        superuser_password = gopass_password_from_path(gopass_path_superuser)
        new_user_name = gopass_field_from_path(gopass_path_new_user, 'user')
        new_user_password = gopass_password_from_path(gopass_path_new_user)

        self.execute_pg_rds_sql(superuser_name, superuser_password,
                                "CREATE ROLE " + new_user_name + " WITH LOGIN INHERIT PASSWORD '" + new_user_password + "';" +
                                "GRANT " + group_role + " TO " + new_user_name + ";")
        print("created user:", new_user_name)

    def deactivate_user(self, gopass_path_superuser, to_deactivate_user_name):
        superuser_name = gopass_field_from_path(gopass_path_superuser, 'user')
        superuser_password = gopass_password_from_path(gopass_path_superuser)

        owned_by_wrong_user = self.execute_pg_rds_sql(superuser_name, superuser_password,
                                                      "SELECT count(*) FROM pg_class c, pg_user u WHERE c.relowner = u.usesysid " +
                                                      "and u.usename='" + to_deactivate_user_name + "';")
        
        if int(owned_by_wrong_user) > 0:
            owned_objects = self.execute_pg_rds_sql(superuser_name, superuser_password,
                                                "SELECT c.relname FROM pg_class c, pg_user u WHERE c.relowner = u.usesysid " +
                                                "and u.usename='" + to_deactivate_user_name + "';")
            raise AssertionError(
                "There are still objects owned by the user to be deactivated:", owned_objects,to_deactivate_user_name)

        connections = self.execute_pg_rds_sql(superuser_name, superuser_password,
                                              "SELECT count(*) FROM pg_stat_activity WHERE application_name = " +
                                              "'PostgreSQL JDBC Driver' AND usename = '" + to_deactivate_user_name + "';")
        if int(connections) > 0:
            raise AssertionError("User is still connected.")

        self.execute_pg_rds_sql(superuser_name, superuser_password,
                                "ALTER ROLE " + to_deactivate_user_name + " WITH NOLOGIN NOCREATEROLE;")
        print('deactivated user:', to_deactivate_user_name)

    def change_owned_objects(self, gopass_path_superuser, to_deactivate_user_name, owner):
        superuser_name = gopass_field_from_path(gopass_path_superuser, 'user')
        superuser_password = gopass_password_from_path(gopass_path_superuser)

        alter_objects = f"""SELECT 'ALTER TABLE ' || c.relname || ' OWNER TO {owner};'
            FROM pg_class c, pg_user u
            WHERE c.relowner = u.usesysid 
            and c.relkind = 'r'
            and u.usename='{to_deactivate_user_name}'
            UNION
            SELECT 'ALTER INDEX ' || c.relname || ' OWNER TO {owner};'
            FROM pg_class c, pg_user u
            WHERE c.relowner = u.usesysid 
            and c.relkind = 'i'
            and c.relname not like 'pg_toast%'
            and u.usename='{to_deactivate_user_name}'
            UNION
            SELECT 'ALTER SEQUENCE ' || c.relname || ' OWNER TO {owner};'
            FROM pg_class c, pg_user u
            WHERE c.relowner = u.usesysid 
            and c.relkind = 'S'
            and u.usename='{to_deactivate_user_name}';"""

        alter_stmt = self.execute_pg_rds_sql(superuser_name, superuser_password, alter_objects)
        alter_stmt.strip()

        if (alter_stmt != ''):
            print('apply alter statements? \n', alter_stmt)
            proceed = input('\n[y/n] \n')
            if(proceed == 'y'):
                self.execute_pg_rds_sql(superuser_name, superuser_password, alter_stmt)
