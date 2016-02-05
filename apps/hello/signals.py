from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType
from hello.models import ModelChange

# IMPORTANT: do not remove ModelChane from the list:
# will result in forever recursion
IGNORE = [Session, ContentType, ModelChange]


@receiver(post_save)
def model_change(sender, **kwargs):
    if sender in IGNORE:
        return
    if kwargs['created']:
        ModelChange(type='add',
                    model=sender.__name__,
                    instance_pk=kwargs['instance'].pk).save()
    else:
        ModelChange(type='edit',
                    model=sender.__name__,
                    instance_pk=kwargs['instance'].pk).save()


@receiver(post_delete)
def person_delete(sender, **kwargs):
    if sender in IGNORE:
        return
    ModelChange(type='delete',
                model=sender.__name__,
                instance_pk=kwargs['instance'].pk).save()
