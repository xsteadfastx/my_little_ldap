my_little_ldap
==============

a little helper to work with ldap

```
Usage:
    my_little_ldap.py adduser <username> <first_name> <last_name> <email_address> <password>
    my_little_ldap.py passwd <username>
    my_little_ldap.py rm <username>
    my_little_ldap.py fromgroup (add | del) <group> <user>
    my_little_ldap.py ls
    my_little_ldap.py (-h | --help)

Options:
    -h --help   Show this screen.
    adduser     Adds a new user.
    passwd      Changes password of a user.
    rm          Deletes user.
    fromgroup   Manages group. Not implemented yet.
    ls          Outputs a list of users
```
