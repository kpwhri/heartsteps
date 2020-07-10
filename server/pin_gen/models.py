from django.db import models

class Pin(models.Model):
    pin_digits = models.CharField(max_length=50)

    def __str__(self):
        return self.pin_digits
        
class Customer(models.Model):
	name = models.CharField(max_length=200, null=True)
	phone = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200, null=True)
	date_created = models.DateTimeField(auto_now_add=True, null=True)


	def __str__(self):
		return self.name


