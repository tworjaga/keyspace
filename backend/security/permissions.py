"""
Permission Management Module
Provides role-based access control and permission management
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Set, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class UserRole(Enum):
    """User roles with different permission levels"""
    ADMIN = "admin"
    ANALYST = "analyst"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    GUEST = "guest"


class Permission(Enum):
    """Available permissions"""
    # Attack permissions
    ATTACK_START = "attack.start"
    ATTACK_STOP = "attack.stop"
    ATTACK_PAUSE = "attack.pause"
    ATTACK_RESUME = "attack.resume"

    # Configuration permissions
    CONFIG_READ = "config.read"
    CONFIG_WRITE = "config.write"
    CONFIG_EXPORT = "config.export"

    # Session permissions
    SESSION_SAVE = "session.save"
    SESSION_LOAD = "session.load"
    SESSION_DELETE = "session.delete"

    # Tool permissions
    TOOLS_WORDLIST_GENERATOR = "tools.wordlist_generator"
    TOOLS_CHARSET_ANALYZER = "tools.charset_analyzer"
    TOOLS_CHARSET_OPTIMIZER = "tools.charset_optimizer"
    TOOLS_ATTACK_PROFILER = "tools.attack_profiler"

    # Security permissions
    SECURITY_AUDIT_VIEW = "security.audit.view"
    SECURITY_AUDIT_EXPORT = "security.audit.export"
    SECURITY_COMPLIANCE_VIEW = "security.compliance.view"
    SECURITY_COMPLIANCE_GENERATE = "security.compliance.generate"

    # Administrative permissions
    ADMIN_USER_MANAGE = "admin.user.manage"
    ADMIN_ROLE_MANAGE = "admin.role.manage"
    ADMIN_SYSTEM_CONFIG = "admin.system.config"


@dataclass
class User:
    """User account information"""
    user_id: str
    username: str
    role: UserRole
    is_active: bool = True
    created_at: str = ""
    last_login: str = ""
    password_hash: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create from dictionary"""
        data['role'] = UserRole(data['role'])
        return cls(**data)


@dataclass
class RoleDefinition:
    """Role definition with permissions"""
    role: UserRole
    permissions: Set[Permission]
    description: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'RoleDefinition':
        """Create from dictionary"""
        return cls(
            role=UserRole(data["role"]),
            permissions=set(Permission(p) for p in data["permissions"]),
            description=data["description"]
        )


class PermissionManager:
    """Manages user permissions and access control"""

    def __init__(self, config_file: str = "config/permissions.json"):
        self.config_file = Path(config_file)
        self.users: Dict[str, User] = {}
        self.roles: Dict[UserRole, RoleDefinition] = {}

        # Initialize default roles
        self._initialize_default_roles()

        # Load configuration
        self.load_config()

    def _initialize_default_roles(self):
        """Initialize default role definitions"""
        self.roles = {
            UserRole.ADMIN: RoleDefinition(
                role=UserRole.ADMIN,
                permissions=set(Permission),  # All permissions
                description="Full system access with all permissions"
            ),
            UserRole.ANALYST: RoleDefinition(
                role=UserRole.ANALYST,
                permissions={
                    Permission.ATTACK_START, Permission.ATTACK_STOP,
                    Permission.ATTACK_PAUSE, Permission.ATTACK_RESUME,
                    Permission.CONFIG_READ, Permission.CONFIG_WRITE,
                    Permission.SESSION_SAVE, Permission.SESSION_LOAD,
                    Permission.TOOLS_WORDLIST_GENERATOR,
                    Permission.TOOLS_CHARSET_ANALYZER,
                    Permission.TOOLS_CHARSET_OPTIMIZER,
                    Permission.TOOLS_ATTACK_PROFILER,
                    Permission.SECURITY_AUDIT_VIEW
                },
                description="Can run attacks and use analysis tools"
            ),
            UserRole.OPERATOR: RoleDefinition(
                role=UserRole.OPERATOR,
                permissions={
                    Permission.ATTACK_START, Permission.ATTACK_STOP,
                    Permission.ATTACK_PAUSE, Permission.ATTACK_RESUME,
                    Permission.CONFIG_READ,
                    Permission.SESSION_LOAD,
                    Permission.TOOLS_WORDLIST_GENERATOR,
                    Permission.TOOLS_CHARSET_ANALYZER
                },
                description="Can operate attacks with limited configuration access"
            ),
            UserRole.AUDITOR: RoleDefinition(
                role=UserRole.AUDITOR,
                permissions={
                    Permission.SECURITY_AUDIT_VIEW,
                    Permission.SECURITY_AUDIT_EXPORT,
                    Permission.SECURITY_COMPLIANCE_VIEW,
                    Permission.SECURITY_COMPLIANCE_GENERATE
                },
                description="Can view audit logs and generate compliance reports"
            ),
            UserRole.GUEST: RoleDefinition(
                role=UserRole.GUEST,
                permissions={
                    Permission.CONFIG_READ,
                    Permission.TOOLS_CHARSET_ANALYZER,
                    Permission.TOOLS_ATTACK_PROFILER
                },
                description="Read-only access to analysis tools"
            )
        }

    def load_config(self):
        """Load users and roles from configuration file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)

                # Load users
                if "users" in data:
                    for user_data in data["users"]:
                        user = User.from_dict(user_data)
                        self.users[user.user_id] = user

                # Load custom roles
                if "custom_roles" in data:
                    for role_data in data["custom_roles"]:
                        role_def = RoleDefinition.from_dict(role_data)
                        self.roles[role_def.role] = role_def

        except Exception as e:
            print(f"Failed to load permission config: {e}")

    def save_config(self):
        """Save users and roles to configuration file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "users": [user.to_dict() for user in self.users.values()],
                "custom_roles": [role.to_dict() for role in self.roles.values()
                               if role.role not in [UserRole.ADMIN, UserRole.ANALYST,
                                                   UserRole.OPERATOR, UserRole.AUDITOR,
                                                   UserRole.GUEST]]
            }

            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Failed to save permission config: {e}")

    def create_user(self, username: str, password: str, role: UserRole) -> Optional[User]:
        """Create a new user account"""
        try:
            if not username or not password:
                return None

            # Check if username already exists
            for user in self.users.values():
                if user.username == username:
                    return None

            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Create user
            user_id = f"user_{len(self.users) + 1}"
            user = User(
                user_id=user_id,
                username=username,
                role=role,
                password_hash=password_hash,
                created_at=str(__import__('datetime').datetime.now())
            )

            self.users[user_id] = user
            self.save_config()

            return user

        except Exception as e:
            print(f"Failed to create user: {e}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            for user in self.users.values():
                if user.username == username and user.password_hash == password_hash and user.is_active:
                    # Update last login
                    user.last_login = str(__import__('datetime').datetime.now())
                    self.save_config()
                    return user

            return None

        except Exception as e:
            print(f"Authentication failed: {e}")
            return None

    def has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        if not user or not user.is_active:
            return False

        role_def = self.roles.get(user.role)
        if not role_def:
            return False

        return permission in role_def.permissions

    def has_any_permission(self, user: User, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions"""
        return any(self.has_permission(user, perm) for perm in permissions)

    def has_all_permissions(self, user: User, permissions: List[Permission]) -> bool:
        """Check if user has all of the specified permissions"""
        return all(self.has_permission(user, perm) for perm in permissions)

    def get_user_permissions(self, user: User) -> Set[Permission]:
        """Get all permissions for a user"""
        if not user or not user.is_active:
            return set()

        role_def = self.roles.get(user.role)
        if not role_def:
            return set()

        return role_def.permissions.copy()

    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Update a user's role"""
        try:
            if user_id not in self.users:
                return False

            self.users[user_id].role = new_role
            self.save_config()
            return True

        except Exception as e:
            print(f"Failed to update user role: {e}")
            return False

    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account"""
        try:
            if user_id not in self.users:
                return False

            self.users[user_id].is_active = False
            self.save_config()
            return True

        except Exception as e:
            print(f"Failed to deactivate user: {e}")
            return False

    def create_custom_role(self, role_name: str, permissions: Set[Permission],
                          description: str) -> bool:
        """Create a custom role"""
        try:
            # Create enum value (this is a limitation - custom roles use string names)
            role_enum = UserRole(role_name)

            role_def = RoleDefinition(
                role=role_enum,
                permissions=permissions,
                description=description
            )

            self.roles[role_enum] = role_def
            self.save_config()
            return True

        except Exception as e:
            print(f"Failed to create custom role: {e}")
            return False

    def get_all_users(self) -> List[User]:
        """Get all users"""
        return list(self.users.values())

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_role_definition(self, role: UserRole) -> Optional[RoleDefinition]:
        """Get role definition"""
        return self.roles.get(role)

    def get_all_roles(self) -> Dict[UserRole, RoleDefinition]:
        """Get all role definitions"""
        return self.roles.copy()
