from django.db import models

class Sector(models.Model):
    sector_id = models.AutoField(primary_key=True, db_column="sector_id")
    name = models.TextField(unique=True, db_column="name")
    description = models.TextField(blank=True, null=True, db_column="description")

    class Meta:
        db_table = "sector"   # exact table name
        managed = False       # do NOT let Django create/alter this table

    def __str__(self):
        return self.name

