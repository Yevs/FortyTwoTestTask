from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from hello.models import Person, RequestLog, ModelChange


@receiver(post_save, sender=Person)
def person_change(sender, **kwargs):
    if kwargs['created']:
        ModelChange(type='add',
                    model='Person',
                    instance_pk=kwargs['instance'].pk).save()
        return
    # else would be better here but then
    # there would be flake8 error
    # "functions should be longer than single if"
    ModelChange(type='edit',
                model='Person',
                instance_pk=kwargs['instance'].pk).save()


@receiver(post_delete, sender=Person)
def person_delete(sender, **kwargs):
    ModelChange(type='delete',
                model='Person',
                instance_pk=kwargs['instance'].pk).save()


@receiver(post_save, sender=RequestLog)
def request_log_change(sender, **kwargs):
    if kwargs['created']:
        ModelChange(type='add',
                    model='RequestLog',
                    instance_pk=kwargs['instance'].pk).save()
        return
    # else would be better here but then
    # there would be flake8 error
    # "functions should be longer than single if"
    ModelChange(type='edit',
                model='RequestLog',
                instance_pk=kwargs['instance'].pk).save()


@receiver(post_delete, sender=RequestLog)
def request_log_delete(sender, **kwargs):
    ModelChange(type='delete',
                model='RequestLog',
                instance_pk=kwargs['instance'].pk).save()
