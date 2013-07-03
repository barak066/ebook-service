from django.db import models

LINK_LENGTH = 4000

class Request(models.Model):
    request = models.TextField(max_length=LINK_LENGTH)
    request_hash = models.CharField(unique=True, max_length=32)
    
    def __unicode__(self):
        return self.request

class PublicContent(models.Model):
    public_content = models.TextField(max_length=10000)
    
    def __unicode__(self):
        return self.public_content
        
class PrivateContent(models.Model):
    private_content = models.TextField(max_length=10000)
    
    def __unicode__(self):
        return self.private_content
        
class OpenID(models.Model):
    open_id = models.TextField(max_length=LINK_LENGTH)
    request = models.ManyToManyField(Request)
    private_content = models.ManyToManyField(PrivateContent)
    public_content = models.ManyToManyField(PublicContent)
    session_key = models.CharField(unique=True, max_length=32)
    
    def __unicode__(self):
        return self.open_id
       
