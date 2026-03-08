from django.contrib import admin
from .models import CivicScore



# used to register a model in the Django Admin Panel so that an admin can manage the data easily from the browser.

@admin.register(CivicScore)                  #Register the CivicScore model with Django Admin using the class CivicScoreAdmin.(short version of writing: admin.site.register(CivicScore, CivicScoreAdmin))
class CivicScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "total_points")     #This controls which columns appear in the admin list page.  (So list_display makes the admin more readable.)
    search_fields = ("user__username",)         #This enables search functionality in the admin panel.
    
    # user → ForeignKey field
    # username → field inside the User model
    # __ → Django lookup syntax
