my_little_ldap
==============

a little helper to work with ldap

```
Usage:
    my_little_ldap.py user add <username> <first_name> <last_name> <email_address> <password>
    my_little_ldap.py user rm <username>
    my_little_ldap.py user addto <username> <groupname>
    my_little_ldap.py user rmfrom <username> <groupname>
    my_little_ldap.py user passwd <username>
    my_little_ldap.py user ls
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
    group ls            List of groups and members.
```
