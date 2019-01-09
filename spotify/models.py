from django.db import models
from django.contrib import admin
import datetime
from django.utils import timezone

class Username(models.Model):
	user = models.CharField(max_length=100)
	country = models.CharField(max_length=2)
	image = models.CharField(max_length=200)
	URL = models.CharField(max_length=200)
	followers = models.IntegerField()
	date_joined = models.DateTimeField(default=timezone.now)
	email = models.CharField(max_length=50)
	rtoken = models.CharField(max_length=200)
	atoken = models.CharField(max_length=200)	
	texpiresat = models.IntegerField()
	historyperm = models.BooleanField(default=False)
	def __str__(self):
		return self.user

class Answer(models.Model):
	answer = models.CharField(max_length=500)
	answer_date = models.DateTimeField(default=timezone.now)
	def __str__(self):
		return self.answer

class Recommend(models.Model):
	recmander = models.ForeignKey(Username, on_delete=models.CASCADE, related_name='recmander')
	recdado = models.ForeignKey(Username, on_delete=models.CASCADE, related_name='recdado', blank = True, null=True)
	recdate = models.DateTimeField(default=timezone.now)
	spotid = models.CharField(max_length=50)
	genurl = models.CharField(max_length=8, default='unlucky')
	tipo = models.CharField(max_length=20)
	msg = models.CharField(max_length=500, default='just play')
	visto = models.BooleanField(default=False)
	prova = models.BooleanField(default=False)
	top = models.BooleanField(default=False)
	liked = models.BooleanField(default=False)
	answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='ans', blank = True, null=True)
	def __str__(self):
		return self.spotid


		

