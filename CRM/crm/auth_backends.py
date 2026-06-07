from __future__ import annotations

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone

from crm.models import RoleAssignment, RoleScopeChoices


class CRMModelBackend(ModelBackend):
    """
    Authentication + permissions backend with role-assignment awareness.

    - Blocks locked accounts (UserSecurityProfile.is_locked)
    - Extends permissions with active RoleAssignment groups
    - Supports object-bound assignments when `has_perm(..., obj)` is used
    """

    def user_can_authenticate(self, user):
        if not super().user_can_authenticate(user):
            return False
        profile = getattr(user, "security_profile", None)
        if profile is None:
            return True
        return not profile.is_locked

    def _active_assignments_qs(self, user_obj):
        now = timezone.now()
        return (
            RoleAssignment.objects.filter(user=user_obj, is_active=True)
            .filter(valid_from__lte=now)
            .filter(Q(valid_to__isnull=True) | Q(valid_to__gte=now))
            .select_related("group", "content_type")
        )

    def _assignment_groups_for_obj(self, user_obj, obj=None):
        assignments = self._active_assignments_qs(user_obj)
        functional_scope_q = Q(content_type__isnull=True, object_id__isnull=True)
        if obj is None:
            assignments = assignments.filter(Q(scope=RoleScopeChoices.GLOBAL) | functional_scope_q)
        else:
            ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)
            assignments = assignments.filter(
                Q(scope=RoleScopeChoices.GLOBAL)
                | functional_scope_q
                | Q(content_type=ct, object_id=getattr(obj, "pk", None))
            )
        return [assignment.group_id for assignment in assignments]

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()
        if obj is None:
            return super().get_all_permissions(user_obj, obj=None)

        if user_obj.is_superuser:
            return {
                f"{app_label}.{codename}"
                for app_label, codename in Permission.objects.values_list("content_type__app_label", "codename")
            }

        user_perm_values = user_obj.user_permissions.values_list("content_type__app_label", "codename")
        user_perms = {f"{app_label}.{codename}" for app_label, codename in user_perm_values}

        group_ids = set(user_obj.groups.values_list("id", flat=True))
        group_ids.update(self._assignment_groups_for_obj(user_obj, obj=obj))
        if not group_ids:
            return user_perms

        group_perm_values = Permission.objects.filter(group__id__in=group_ids).values_list(
            "content_type__app_label",
            "codename",
        )
        group_perms = {f"{app_label}.{codename}" for app_label, codename in group_perm_values}
        return user_perms | group_perms

    def get_group_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        perms = set(super().get_group_permissions(user_obj, obj=obj))
        group_ids = self._assignment_groups_for_obj(user_obj, obj=obj)
        if not group_ids:
            return perms

        dynamic = Permission.objects.filter(group__id__in=group_ids).values_list(
            "content_type__app_label",
            "codename",
        )
        perms.update({f"{app_label}.{codename}" for app_label, codename in dynamic})
        return perms
