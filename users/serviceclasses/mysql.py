from servicebase import ServiceBase
from servicefield import ServiceField
from django import forms
from django.conf import settings
from updatefunctions import updateStateField
from django.db import connection, IntegrityError, DatabaseError, transaction
from django.contrib import messages
from users.models import Service
from services import sendInfoMaterial
from sh import ErrorReturnCode, cd, mysqldump

STATES = (
    ('d', 'disabled'),
    ('l', 'locked'),
    ('a', 'active')
)


class MySQL(ServiceBase):
    servicetype = "mysql"

    def __init__(self):
        self.default_database = settings.DATABASES['default']['NAME']
        self.fields = (ServiceField("MySQL", "mysql", self, forms.ChoiceField(choices=STATES), updateStateField,
                                    forms.BooleanField(label="MySQL")),)

    def initServiceToUser(self, request, user, **kw):

        cur = connection.cursor()
        try:
            username_dotless = user.username.replace(".", "_")
            # Check if database for username exists
            cur.execute("SHOW DATABASES")
            databases = cur.fetchall()

            if username_dotless in databases:
                messages.error(request, "MySQLError: Database for user is already created")
                return False

            # Making database for user
            try:
                cur.execute("USE mysql")
                cur.execute("CREATE DATABASE %s" % (username_dotless))
            except DatabaseError as de:
                cur.execute("USE %s" % (self.default_database))
                messages.error(request, "MySQLError: {}".format(de.args[1]))
                # Giving database of previous user to new user by deleting content of database?
                #TODO: Confirmation

                #return False

            # Creating MySQL-user
            try:
                stmt = "CREATE USER '{}'@'%%'".format(username_dotless)
                print "stmt = {}".format(stmt)
                cur.execute(stmt)

            except DatabaseError as de:
                print de.args
                cur.execute("DROP DATABASE %s" % (username_dotless))
                cur.execute("USE %s" % (self.default_database))
                messages.error(request, "MySQLError: {}".format(de.args[1]))
                return False

            #Setting privileges
            try:
                stmt = "GRANT ALL PRIVILEGES ON {}.* TO '{}'@'%%'".format(username_dotless,username_dotless)
                cur.execute(stmt)
                cur.execute("FLUSH PRIVILEGES")
            except IntegrityError as ie:
                stmt = "DROP USER USER '{}'@'%%'".format(username_dotless)
                cur.execute(stmt)
                cur.execute("DROP DATABASE %s" % (username_dotless))
                cur.execute("USE %s" % (self.default_database))
                messages.error(request, "MySQLError: Failed to grant privileges for user to database")
                return False

            cur.execute("USE %s" % (self.default_database))
            mysql = MySQL()
            tmp = Service.objects.create(user=user, servicetype=mysql.getServiceType(), state='a')
        finally:
            cur.execute("USE %s" % (self.default_database))
            cur.close()
        messages.success(request, "MySQL initialized for user.")
        return True

    def toggleServiceFromUser(self, request, user, lock):
        """
        At first we are getting grants for user. If user is granted to use own database, then rights will be revoked.
        """

        already_locked = False
        username = user.username.replace(".", "_")
        cur = connection.cursor()
        cur.execute("USE mysql")
        stmt = "SHOW GRANTS FOR '{}'@'%%'".format(username)
        cur.execute(stmt)
        linecount = len(cur.fetchall())
        if (linecount < 2 and lock) or (linecount > 1 and not lock):  # MUST FIX IF USER CAN ACCESS MULTIPLE DATABASES;
            messages.success(request, "MySQL service has been locked from user")
            cur.execute("USE %s" % (self.default_database))
            already_locked = True
        else:
            try:
                if lock:
                    stmt = "REVOKE ALL PRIVILEGES ON {}.* FROM '{}'@'%%'".format(username,username)
                    messages.success(request, "MySQL service has been locked from user")
                else:
                    stmt = "GRANT ALL PRIVILEGES ON {}.* TO '{}'@'%%'".format(username,username)
                    messages.success(request, "MySQL service has been unlocked from user")
                cur.execute(stmt)
                cur.execute("FLUSH PRIVILEGES")
            except IntegrityError:
                cur.execute("USE %s" % (self.default_database))
                if lock:
                    messages.error(request, "MySQLError: Failed to revoke privileges.")
                else:
                    messages.error(request, "MySQLError: Failed to grant privileges.")
                return False
            finally:
                cur.execute("USE %s" % (self.default_database))
                cur.close()
        mysql = MySQL()
        tmp = Service.objects.filter(user=user, servicetype=mysql.getServiceType())[0]
        if lock:
            tmp.state = 'l'
        else:
            tmp.state = 'a'
        tmp.save()
        if not already_locked:
            if lock:
                sendInfoMaterial(self, "Your MySQL-service has been locked.", user)
            else:
                sendInfoMaterial(self, "Your MySQL-service has been unlocked.", user)

    def lockServiceFromUser(self, request, user):
        return self.toggleServiceFromUser(request, user, True)

    def unlockServiceFromUser(self, request, user):
        return self.toggleServiceFromUser(request, user, False)

    def resetUsersPassword(self, request, user, password):
        username = user.username.replace(".", "_")
        cur = connection.cursor()
        cur.execute("USE mysql")
        try:
            cur.execute("SET PASSWORD FOR '%s'@'%%' = PASSWORD('%s')" % (username, password))
            messages.success(request, "Password for MySQL user successfully changed")
        except IntegrityError as ie:
            dir(ie)
            messages.error(request, "MySQLError: Couldn't change user's password.")
        finally:
            cur.close()


    def disableServiceFromUser(self, request, user):
        username = user.username.replace(".", "_")
        homedir = '/home/%s' % (user)
        cur = connection.cursor()

        try:
            cd(homedir)
            password = settings.DATABASES["default"]["PASSWORD"]

            try:
                s = mysqldump("-u", "root", "-p%s" % (password), username)
                sqldumpfile = open('sqldump.sql', 'w')
                for line in s:
                    sqldumpfile.write(line)
                cur.execute("USE mysql")

                try:
                    cur.execute("DROP DATABASE %s" % (username))

                    try:
                        stmt = "DROP USER '{}'@'%%'".format(username)
                        cur.execute(stmt)
                        mysql = MySQL()
                        tmp = Service.objects.filter(user=user, servicetype=mysql.getServiceType())[0]
                        tmp.delete()
                        sendInfoMaterial(self, "Your MySQL-service has been disabled.", user)
                        messages.success(request, "MySQL service removed from user. SQLdump has been made")

                    except ErrorReturnCode:
                        messages.error(request, "Could'nt remove user")

                except ErrorReturnCode:
                    messages.error(request, "Could'nt remove user's database.")

            except ErrorReturnCode:
                messages.error(request, "MySQLdump failed.")

        except ErrorReturnCode:
            messages.error(request, "%s does'nt exist!" % (homedir))

        finally:
            cur.execute("USE %s" % (self.default_database))
            cur.close()