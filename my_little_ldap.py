'''
Usage:
    my_little_ldap.py adduser <username> <first_name> <last_name> <email_address> <password>
    my_little_ldap.py passwd <username>
    my_little_ldap.py fromgroup (add | del) <group> <user>
    my_little_ldap.py ls
    my_little_ldap.py (-h | --help)
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
LDAP_BASE = 'ou=user,dc=ecclesianuernberg,dc=de'
LDAP_ADMIN = 'cn=admin,dc=ecclesianuernberg,dc=de'


def encode_password(password):
    sha_digest = sha.new(password).digest()
    return '{SHA}' + string.strip(encodestring(sha_digest))


def adduser():
    # get passwort from commandline
    admin_password = getpass()

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # dn of the new user
    new_user_dn = "cn=%s %s,%s" % (arguments['<first_name>'],
                                   arguments['<last_name>'], LDAP_BASE)

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
    for i in ldif:
        print '%s: %s' % (i[0], i[1])
    confirmation = raw_input('confirm y/n: ')

    if confirmation == 'y':
        # add ldif to server
        l.add_s(new_user_dn, ldif)

    # disconnect
    l.unbind_s()


def ls():
    #define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['cn', 'uid']
    search_filter = 'uid=*'

    # connect
    l = ldap.open(LDAP_SERVER)

    # search
    ldap_result_id = l.search(LDAP_BASE, search_scope, search_filter,
                              retrieve_attributes)

    # print result
    for i in l.result(ldap_result_id)[1]:
        print '%s: %s' % (i[1]['uid'][0], i[1]['cn'][0])


def passwd():
    # define variables
    admin_password = getpass('Admin Password: ')
    new_password = getpass('New Password for '+arguments['<username>']+': ')
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['cn']
    search_filter = 'uid='+arguments['<username>']

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # search for full dn
    ldap_result_id = l.search(LDAP_BASE, search_scope, search_filter,
                              retrieve_attributes)
    full_dn = l.result(ldap_result_id)[1][0][0]

    # encode password
    password = encode_password(new_password)

    # create mod list and modify ldap entry
    mod_list = ((ldap.MOD_REPLACE, 'userPassword', password),)
    l.modify(full_dn, mod_list)

    # disconnect
    l.unbind_s()


def main():
    if arguments['adduser']:
        adduser()
    elif arguments['ls']:
        ls()
    elif arguments['passwd']:
        passwd()


if __name__ == '__main__':
    main()
