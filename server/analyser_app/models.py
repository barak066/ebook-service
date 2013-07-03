from django.db import models
from picklefield.fields import PickledObjectField

NAME_LENGTH = 255
LINK_LENGTH = 4000
TEXT_LENGTH = 10000


class Task(models.Model):
    serialized_task = PickledObjectField()
    name = models.CharField(max_length=NAME_LENGTH)
    parser_name = models.CharField(max_length=NAME_LENGTH)
    weight = models.IntegerField()
    link = models.CharField(max_length=LINK_LENGTH,null=True,blank=True)
    good = models.BooleanField(default=True)
    reason = models.TextField(null=True,blank=True)
    when = models.DateTimeField(auto_now =True)

    def __unicode__(self):
       return u'%s: %s (%d)' % (self.parser_name,self.name,self.weight)

    def save(self, **kwargs):
        self.serialized_task.weight = self.weight
        if 'link' in self.serialized_task.__dict__:
            self.serialized_task.link = self.link
        super(Task, self).save(kwargs)


class Refresh(models.Model):
    #TODO add checking for right link form (http://...)
    link = models.CharField(max_length=255,unique=True)
    last_modified = models.DateTimeField()

    def __unicode__(self):
        return u'%s, %s' % (self.link, self.last_modified)

    class Meta:
        verbose_name_plural="Refreshes"

    def check_refreshable(self, lm_date):
        from datetime import datetime
        format = "%a, %d %b %Y %H:%M:%S %Z"
        if type(lm_date) != datetime:
            lm_date = datetime.strptime(lm_date, format)
        return self.last_modified != lm_date

    @staticmethod
    def check_need_refresh(link, lm_date):
        refreshes = Refresh.objects.filter(link=link)
        if not refreshes:
            return True
        refresh = refreshes[0]
        return refresh.last_modified != lm_date

