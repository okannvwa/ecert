def has_permission_for_task(user, task):
    """
    Checks if a user has permission to interact with a task based on the column and their group.
    Superusers are always granted permission.
    """
    if user.is_superuser:
        return True
    if task.column in ['expertise', 'notificeren'] and user.groups.filter(name="Team Expertise").exists():
        return True
    if task.column == 'contentbeheer' and user.groups.filter(name="Team Contentbeheer").exists():
        return True
    return False