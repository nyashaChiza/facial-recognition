from django.db import models

class Citizen(models.Model):
    ID_CHOICES = (('Passport', 'Passport'),('National ID', 'National ID'),('Driver License', 'Driver License'))
    
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    id_type = models.CharField(max_length=255, choices = ID_CHOICES)
    id_number = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    
class Incident(models.Model):
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='incidents', )
    title = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.citizen.first_name} {self.citizen.last_name}"
    

class CitizenImage(models.Model):
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='image')
    image = models.ImageField(upload_to='citizen/images/')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.citizen.first_name} {self.citizen.last_name}"
