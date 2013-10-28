import logging
from datetime import datetime

from turbogears import config, identity
from turbogears.database import PackageHub
from turbogears.util import load_class
from turbojson.jsonify import jsonify_sqlobject, jsonify

from sqlobject import (SQLObject, SQLObjectNotFound, RelatedJoin,
    DateTimeCol, IntCol, StringCol, UnicodeCol)
from sqlobject.dberrors import DuplicateEntryError


log = logging.getLogger('turbogears.identity.soprovider')

hub = PackageHub('turbogears.identity')
__connection__ = hub


def to_db_encoding(s, encoding):
    if not isinstance(s, basestring) and hasattr(s, '__unicode__'):
        s = unicode(s)
    if isinstance(s, unicode):
        s = s.encode(encoding)
    return s


# Global class references --
# these will be set when the provider is initialized.
user_class = None
group_class = None
permission_class = None
visit_class = None


class SqlObjectIdentity(object):
    """Identity that uses a model from a database (via SQLObject)."""

    def __init__(self, visit_key=None, user=None):
        self.visit_key = visit_key
        if user:
            self._user = user
            if visit_key is not None:
                self.login()

    @property
    def user(self):
        """Get user instance for this identity."""
        try:
            return self._user
        except AttributeError:
            # User hasn't already been set
            pass
        # Attempt to load the user. After this code executes, there *will* be
        # a _user attribute, even if the value is None.
        visit = self.visit_link
        if visit:
            try:
                self._user = user_class.get(visit.user_id)
            except SQLObjectNotFound:
                log.warning("No such user with ID: %s", visit.user_id)
                self._user = None
        else:
            self._user = None
        return self._user

    @property
    def user_name(self):
        """Get user name of this identity."""
        if not self.user:
            return None
        return self.user.user_name

    @property
    def user_id(self):
        """Get user id of this identity."""
        if not self.user:
            return None
        return self.user.id

    @property
    def anonymous(self):
        """Return true if not logged in."""
        return not self.user

    @property
    def permissions(self):
        """Get set of permission names of this identity."""
        try:
            return self._permissions
        except AttributeError:
            # Permissions haven't been computed yet
            pass
        if not self.user:
            self._permissions = frozenset()
        else:
            self._permissions = frozenset(
                p.permission_name for p in self.user.permissions)
        return self._permissions

    @property
    def groups(self):
        """Get set of group names of this identity."""
        try:
            return self._groups
        except AttributeError:
            # Groups haven't been computed yet
            pass
        if not self.user:
            self._groups = frozenset()
        else:
            self._groups = frozenset(g.group_name for g in self.user.groups)
        return self._groups

    @property
    def group_ids(self):
        """Get set of group IDs of this identity."""
        try:
            return self._group_ids
        except AttributeError:
            # Groups haven't been computed yet
            pass
        if not self.user:
            self._group_ids = frozenset()
        else:
            self._group_ids = frozenset(g.id for g in self.user.groups)
        return self._group_ids

    @property
    def visit_link(self):
        """Get the visit link to this identity."""
        if self.visit_key is None:
            return None
        try:
            return visit_class.by_visit_key(self.visit_key)
        except SQLObjectNotFound:
            return None

    @property
    def login_url(self):
        """Get the URL for the login page."""
        return identity.get_failure_url()

    def login(self):
        """Set the link between this identity and the visit."""
        visit = self.visit_link
        if visit:
            visit.user_id = self._user.id
        else:
            try:
                visit = visit_class(
                    visit_key=self.visit_key, user_id=self._user.id)
            except DuplicateEntryError:
                visit = self.visit_link
                if not visit:
                    raise
                visit.user_id = self._user.id

    def logout(self):
        """Remove the link between this identity and the visit."""
        visit = self.visit_link
        if visit:
            visit.destroySelf()
        # Clear the current identity
        identity.set_current_identity(SqlObjectIdentity())


class SqlObjectIdentityProvider(object):
    """IdentityProvider that uses a model from a database (via SQLObject)."""

    def __init__(self):
        super(SqlObjectIdentityProvider, self).__init__()
        glob_ns = globals()

        for classname in ('user', 'group', 'permission', 'visit'):
            default_classname = '.TG_' + (classname == 'visit'
                and 'VisitIdentity' or classname.capitalize())
            class_path = config.get('identity.soprovider.model.%s' % classname,
                __name__ + default_classname)
            class_ = load_class(class_path)
            if class_:
                log.info('Successfully loaded "%s".', class_path)
                glob_ns['%s_class' % classname] = class_
            else:
                log.error('Could not load class "%s".'
                    ' Check identity.soprovider.model.%s setting',
                    class_path, classname)
        try:
            encoding = glob_ns[
                'user_class'].sqlmeta.columns['user_name'].dbEncoding
        except (KeyError, AttributeError):
            encoding = None
        self.user_class_db_encoding = encoding or 'utf-8'

    def encrypt_password(self, password):
        # Default encryption algorithm is to use plain text passwords
        algorithm = config.get('identity.soprovider.encryption_algorithm', None)
        return identity.encrypt_pw_with_algorithm(algorithm, password)

    def create_provider_model(self):
        """Create the database tables if they don't already exist."""
        try:
            hub.begin()
            user_class.createTable(ifNotExists=True)
            group_class.createTable(ifNotExists=True)
            permission_class.createTable(ifNotExists=True)
            visit_class.createTable(ifNotExists=True)
            hub.commit()
            hub.end()
        except KeyError:
            log.warning("No database is configured:"
                " SqlObjectIdentityProvider is disabled.")
            return

    def validate_identity(self, user_name, password, visit_key):
        """Validate the identity represented by user_name using the password.

        Must return either None if the credentials weren't valid or an object
        with the following properties:
            user_name: original user name
            user: a provider dependent object (TG_User or similar)
            groups: a set of group names
            permissions: a set of permission names

        """
        try:
            user_name = to_db_encoding(user_name, self.user_class_db_encoding)
            user = user_class.by_user_name(user_name)
            if not self.validate_password(user, user_name, password):
                log.info("Passwords don't match for user: %s", user_name)
                return None
            log.info("Associating user (%s) with visit (%s)",
                user_name, visit_key)
            return SqlObjectIdentity(visit_key, user)
        except SQLObjectNotFound:
            log.warning("No such user: %s", user_name)
            return None

    def validate_password(self, user, user_name, password):
        """Check the user_name and password against existing credentials.

        Note: user_name is not used here, but is required by external
        password validation schemes that might override this method.
        If you use SqlObjectIdentityProvider, but want to check the passwords
        against an external source (i.e. PAM, a password file, Windows domain),
        subclass SqlObjectIdentityProvider, and override this method.

        """
        return user.password == self.encrypt_password(password)

    def load_identity(self, visit_key):
        """Lookup the principal represented by user_name.

        Return None if there is no principal for the given user ID.

        Must return an object with the following properties:
            user_name: original user name
            user: a provider dependent object (TG_User or similar)
            groups: a set of group names
            permissions: a set of permission names

        """
        return SqlObjectIdentity(visit_key)

    def anonymous_identity(self):
        """Return anonymous identity.

        Must return an object with the following properties:
            user_name: original user name
            user: a provider dependent object (TG_User or similar)
            groups: a set of group names
            permissions: a set of permission names

        """
        return SqlObjectIdentity()

    def authenticated_identity(self, user):
        """Constructs Identity object for users with no visit_key."""
        return SqlObjectIdentity(user=user)


class TG_User(SQLObject):
    """Reasonably basic User definition."""

    user_name = UnicodeCol(length=16, alternateID=True,
        alternateMethodName='by_user_name')
    email_address = UnicodeCol(length=255, alternateID=True,
        alternateMethodName='by_email_address')
    display_name = UnicodeCol(length=255)
    password = UnicodeCol(length=40)
    created = DateTimeCol(default=datetime.now)

    # groups this user belongs to
    groups = RelatedJoin('TG_Group', intermediateTable='user_group',
        joinColumn='user_id', otherColumn='group_id')

    def _get_permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    def _set_password(self, cleartext_password):
        """Run cleartext_password through the hash algorithm before saving."""
        try:
            hash = identity.current_provider.encrypt_password(cleartext_password)
        except identity.exceptions.IdentityManagementNotEnabledException:
            # Creating identity provider just to encrypt password
            # (so we don't reimplement the encryption step).
            ip = SqlObjectIdentityProvider()
            hash = ip.encrypt_password(cleartext_password)
            if hash == cleartext_password:
                log.info("Identity provider not enabled,"
                    " and no encryption algorithm specified in config."
                    " Setting password as plaintext.")
        self._SO_set_password(hash)

    def set_password_raw(self, password):
        """Save the password as-is to the database."""
        self._SO_set_password(password)

@jsonify.when('isinstance(obj, TG_User)')
def jsonify_user(obj):
    """Convert user to JSON."""
    result = jsonify_sqlobject(obj)
    result.pop('password', None)
    result['groups'] = [g.group_name for g in obj.groups]
    result['permissions'] = [p.permission_name for p in obj.permissions]
    return result


class TG_Group(SQLObject):
    """An ultra-simple group definition."""

    group_name = UnicodeCol(length=16, alternateID=True,
        alternateMethodName='by_group_name')
    display_name = UnicodeCol(length=255)
    created = DateTimeCol(default=datetime.now)

    # collection of all users belonging to this group
    users = RelatedJoin('TG_User', intermediateTable='user_group',
        joinColumn='group_id', otherColumn='user_id')

    # collection of all permissions for this group
    permissions = RelatedJoin('TG_Permission', joinColumn='group_id',
        intermediateTable='group_permission',
        otherColumn='permission_id')

@jsonify.when('isinstance(obj, TG_Group)')
def jsonify_group(obj):
    """Convert group to JSON."""
    result = jsonify_sqlobject(obj)
    result['users'] = [u.user_name for u in obj.users]
    result['permissions'] = [p.permission_name for p in obj.permissions]
    return result


class TG_Permission(SQLObject):
    """Permissions for a given group."""

    class sqlmeta:
        table = 'permission'

    permission_name = UnicodeCol(length=16, alternateID=True,
        alternateMethodName='by_permission_name')
    description = UnicodeCol(length=255)

    groups = RelatedJoin('TG_Group', intermediateTable='group_permission',
        joinColumn='permission_id', otherColumn='group_id')

@jsonify.when('isinstance(obj, TG_Permission)')
def jsonify_permission(obj):
    """Convert permissions to JSON."""
    result = jsonify_sqlobject(obj)
    result['groups'] = [g.group_name for g in obj.groups]
    return result


class TG_VisitIdentity(SQLObject):
    """A visit to your website."""

    class sqlmeta:
        table = 'visit_identity'

    visit_key = StringCol(length=40, alternateID=True,
        alternateMethodName='by_visit_key')
    user_id = IntCol()


def encrypt_password(cleartext_password):
    """Encrypt given cleartext password."""
    try:
        hash = identity.current_provider.encrypt_password(cleartext_password)
    except identity.exceptions.RequestRequiredException:
        # Creating identity provider just to encrypt password
        # (so we don't reimplement the encryption step).
        ip = SqlObjectIdentityProvider()
        hash = ip.encrypt_password(cleartext_password)
        if hash == cleartext_password:
            log.info("Identity provider not enabled, and no encryption "
                "algorithm specified in config. Setting password as plaintext.")
    return hash
