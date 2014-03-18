'''
Usage:
    my_little_ldap.py user add <username> <first_name> <last_name> <email_address> <password>
    my_little_ldap.py user rm <username>
    my_little_ldap.py user addto <username> <groupname>
    my_little_ldap.py user rmfrom <username> <groupname>
    my_little_ldap.py user passwd <username>
    my_little_ldap.py user ls
    my_little_ldap.py group add <groupname> <username>
    my_little_ldap.py group rm <groupname>
    my_little_ldap.py group ls
    my_little_ldap.py (-h | --help)

Options:
    -h --help           Show this screen.
    user add            Adds a new user.
    user rm             Deletes user.
    user addto          Adds user to group.
    user rmfrom         Removes user from group.
    user passwd         Changes password of a user.
    user ls             List of users.
    group add           Add group.
    group rm            Delete group.
    group ls            List of groups and members.
'''
import ldap
import ldap.modlist as modlist
import sha
import string
from base64 import encodestring
from docopt import docopt
from getpass import getpass


arguments = docopt(__doc__)

LDAP_SERVER = 'localhost'
LDAP_USER_BASE = 'ou=user,dc=ecclesianuernberg,dc=de'
LDAP_GROUP_BASE = 'ou=groups,dc=ecclesianuernberg,dc=de'
LDAP_ADMIN = 'cn=admin,dc=ecclesianuernberg,dc=de'


def encode_password(password):
    '''encode password to sha'''
    sha_digest = sha.new(password).digest()
    return '{SHA}' + string.strip(encodestring(sha_digest))


def get_full_user_dn(username):
    '''get full dn for username'''
    # define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['cn']
    search_filter = 'uid=' + username

    # connection and bind
    l = ldap.open(LDAP_SERVER)

    # search for full dn
    ldap_result_id = l.search(LDAP_USER_BASE, search_scope, search_filter,
                              retrieve_attributes)

    return l.result(ldap_result_id)[1][0][0]


def get_full_group_dn(group):
    #define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['cn']
    search_filter = 'cn=' + group

    # connect
    l = ldap.open(LDAP_SERVER)

    # search for full dn
    ldap_result_id = l.search(LDAP_GROUP_BASE, search_scope, search_filter,
                              retrieve_attributes)

    return l.result(ldap_result_id)[1][0][0]


def user_add():
    # get passwort from commandline
    admin_password = getpass('Admin Password: ')

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # dn of the new user
    new_user_dn = 'cn=%s %s,%s' % (arguments['<first_name>'],
                                   arguments['<last_name>'], LDAP_USER_BASE)

    # encode password
    password = encode_password(arguments['<password>'])

    # getting ldap attributes together
    attrs = {}
    attrs['objectclass'] = ['top', 'inetOrgPerson']
    attrs['cn'] = '%s %s' % (arguments['<first_name>'],
                             arguments['<last_name>'])
    attrs['mail'] = arguments['<email_address>']
    attrs['givenName'] = arguments['<first_name>']
    attrs['sn'] = arguments['<last_name>']
    attrs['uid'] = arguments['<username>']
    attrs['userPassword'] = password

    # create ldif
    ldif = modlist.addModlist(attrs)

    # print ldif and ask if data is right
    print '%s%s%s' % ('\033[1m', new_user_dn, '\033[0m')
    for i in ldif:
        print '%s: %s' % (i[0], i[1])
    confirmation = raw_input('confirm y/n: ')

    if confirmation == 'y':
        # add ldif to server
        l.add_s(new_user_dn, ldif)

    # disconnect
    l.unbind_s()


def user_addto():
    ''' adds user to group'''
    # get passwort from commandline
    admin_password = getpass('Admin Password: ')

    # get full dn's
    full_group_dn = get_full_group_dn(arguments['<groupname>'])
    full_user_dn = get_full_user_dn(arguments['<username>'])

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # getting attrs together
    mod_attrs = [(ldap.MOD_ADD, 'member', full_user_dn)]

    l.modify_s(full_group_dn, mod_attrs)

    # disconnect
    l.unbind_s()


def user_rmfrom():
    ''' removes user from group'''
    # get passwort from commandline
    admin_password = getpass('Admin Password: ')

    # get full dn's
    full_group_dn = get_full_group_dn(arguments['<groupname>'])
    full_user_dn = get_full_user_dn(arguments['<username>'])

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # getting attrs together
    mod_attrs = [(ldap.MOD_DELETE, 'member', full_user_dn)]

    l.modify_s(full_group_dn, mod_attrs)

    # disconnect
    l.unbind_s()


def user_ls():
    #define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['cn', 'uid']
    search_filter = 'uid=*'

    # connect
    l = ldap.open(LDAP_SERVER)

    # search
    ldap_result_id = l.search(LDAP_USER_BASE, search_scope, search_filter,
                              retrieve_attributes)

    # print result
    for i in l.result(ldap_result_id)[1]:
        print '%s%s%s: %s' % ('\033[1m', i[1]['uid'][0], '\033[0m', i[1]['cn'][0])


def user_passwd():
    # define variables
    admin_password = getpass('Admin Password: ')
    new_password = getpass('New Password for '+arguments['<username>']+': ')
    full_dn = get_full_user_dn(arguments['<username>'])

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # encode password
    password = encode_password(new_password)

    # create mod list and modify ldap entry
    mod_list = ((ldap.MOD_REPLACE, 'userPassword', password),)
    l.modify(full_dn, mod_list)

    # disconnect
    l.unbind_s()


def user_rm():
    # define variables
    admin_password = getpass('Admin Password: ')
    full_dn = get_full_user_dn(arguments['<username>'])

    #connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # confirmation
    print 'you are going to delete user: %s' % (arguments['<username>'])
    confirmation = raw_input('confirm y/n: ')

    if confirmation == 'y':
        # delete
        l.delete_s(full_dn)

    # disconnect
    l.unbind_s()


def group_add():
    # get password from commandline
    admin_password = getpass('Admin Password: ')

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # dn of the new group
    new_group_dn = 'cn=%s,%s' % (arguments['<groupname>'], LDAP_GROUP_BASE)

    # getting ldap attributes together
    attrs = {}
    attrs['objectClass'] = ['top', 'groupOfNames']
    attrs['cn'] = arguments['<groupname>']
    attrs['member'] = get_full_user_dn(arguments['<username>'])

    # create ldif
    ldif = modlist.addModlist(attrs)

    # confirmation
    print '%s%s%s' % ('\033[1m', new_group_dn, '\033[0m')
    for i in ldif:
        print '%s: %s' % (i[0], i[1])
    confirmation = raw_input('confirm y/n: ')

    if confirmation == 'y':
        # add ldif to server
        l.add_s(new_group_dn, ldif)

    # disconnect
    l.unbind_s()


def group_rm():
    # definde variables
    admin_password = getpass('Admin Password: ')
    full_dn = get_full_group_dn(arguments['<groupname>'])

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # confirmation
    print 'you are going to delete group: %s' % (arguments['<groupname>'])
    confirmation = raw_input('confirm y/n: ')

    if confirmation == 'y':
        # delete
        l.delete_s(full_dn)

    # disconnect
    l.unbind_s()


def group_ls():
    #define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['cn', 'member']
    search_filter = 'objectClass=groupOfNames'

    # connect
    l = ldap.open(LDAP_SERVER)

    # search
    ldap_result_id = l.search(LDAP_GROUP_BASE, search_scope, search_filter,
                              retrieve_attributes)

    # print result
    for i in l.result(ldap_result_id)[1]:
        print '\033[1m' + i[1]['cn'][0] + '\033[0m'
        for j in i[1]['member']:
            print '- ' + j


def main():
    if arguments['user']:
        if arguments['add']:
            user_add()
        elif arguments['addto']:
            user_addto()
        elif arguments['rmfrom']:
            user_rmfrom()
        elif arguments['ls']:
            user_ls()
        elif arguments['passwd']:
            user_passwd()
        elif arguments['rm']:
            user_rm()
    elif arguments['group']:
        if arguments['ls']:
            group_ls()
        elif arguments['add']:
            group_add()
        elif arguments['rm']:
            group_rm()


if __name__ == '__main__':
    main()
