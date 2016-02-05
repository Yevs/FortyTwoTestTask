from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.utils import OperationalError

from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType
from hello.models import ModelChange

# IMPORTANT: do not remove ModelChane from the list:
# will result in forever recursion
IGNORE_ADD = [Session, ContentType, ModelChange]

IGNORE_EDIT = [Session, ContentType]
IGNORE_DELETE = [Session, ContentType]


@receiver(post_save)
def model_change(sender, **kwargs):
    try:
        if kwargs['created']:
                if sender not in IGNORE_ADD:
                    ModelChange(type='add',
                                model=sender.__name__,
                                instance_pk=kwargs['instance'].pk).save()
                    return None
        if sender not in IGNORE_EDIT:
            ModelChange(type='edit',
                        model=sender.__name__,
                        instance_pk=kwargs['instance'].pk).save()
    except (RuntimeError, OperationalError):  # south migration
        pass


@receiver(post_delete)
def person_delete(sender, **kwargs):
    try:
        if sender in IGNORE_DELETE:
            return
        ModelChange(type='delete',
                    model=sender.__name__,
                    instance_pk=kwargs['instance'].pk).save()
    except:
        pass
